import json
import os
import re
import shutil
import subprocess
import traceback
import urllib.parse
import html
import time
import xml.etree.ElementTree as ET
import base64
from urllib.parse import urlparse
import threading
import concurrent.futures
from functools import wraps

import requests
import urllib3
from flask import Blueprint, jsonify, request, Response, stream_with_context, send_file, render_template

from beta.batch_scraper_2.Endpoints import Endpoints
from beta.batch_scraper_2.models.AllTestDetails import AllTestDetails
from beta.batch_scraper_2.module import ScraperModule
from beta.util import generate_safe_file_name
from mainLogic.utils.Endpoint import Endpoint
from mainLogic.utils.dependency_checker import re_check_dependencies
from mainLogic.utils.glv import Global
from mainLogic.utils.glv_var import debugger, ENDPOINTS_NAME
from mainLogic.utils import glv_var
from mainLogic.utils.image_utils import create_a4_pdf_from_images

# Initialize the blueprint
scraper_blueprint = Blueprint('scraper', __name__)

# --- CONFIGURATION FOR DECRYPTION PROXY ---
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
TMP_DIR = os.path.join(BASE_DIR, "tmp_proxy")
ENC_DIR = os.path.join(TMP_DIR, "enc")
DEC_DIR = os.path.join(TMP_DIR, "dec")

# Global Dictionary to store context (Keys, URLs) for active lectures
LECTURE_CONTEXT = {}

# Threading configuration
MAX_WORKER_THREADS = int(os.environ.get('PWDL_DECRYPT_THREADS', '4'))
DECRYPT_EXECUTOR = concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKER_THREADS, thread_name_prefix='decrypt-worker')
debugger.info(f"[THREADING] Initialized decrypt thread pool with {MAX_WORKER_THREADS} workers")

# Thread-safe locks for file operations
file_locks = {}
file_locks_lock = threading.Lock()

# Initialize BatchAPI
try:
    batch_api = Endpoints().set_token(vars['prefs'].get('token',{}).get("token",""))
except Exception:
    re_check_dependencies()
    token = glv_var.vars["prefs"].get("token_config",{})
    try:
        access_token = token["access_token"]
    except:
        access_token = token.get("token", "")

    random_id = token.get("random_id",None)
    try:
        if random_id is None:
            batch_api = Endpoints().set_token(access_token)
        else:
            batch_api = Endpoints().set_token(access_token,random_id=random_id)
    except Exception as e :
        debugger.error(f"Scraper init error: {e}")

def create_response(data=None, error=None):
    response = {"data": data}
    if error is not None:
        response["error"] = error
    return jsonify(response)

def renamer(data,old_key,new_key):
    new_data = []
    for element in data:
        try:
            element[new_key] = element.pop(old_key)
        except: pass
        new_data.append(element)
    return new_data

# --- HELPER FUNCTIONS ---

def get_lecture_context(batch_name, id):
    """Retrieves URL/Key from cache or API"""
    ctx = LECTURE_CONTEXT.get(id)
    if not ctx:
        from mainLogic.big4.Ravenclaw_decrypt.key import LicenseKeyFetcher as Lf
        lf = Lf(batch_api.token, batch_api.random_id)
        keys = lf.get_key(id, batch_name) # [kid, key, url]
        
        parsed_url = urllib.parse.urlparse(keys[2])
        
        ctx = {
            'kid': keys[0],
            'key': keys[1],
            'original_url': keys[2],
            'query': parsed_url.query
        }
        LECTURE_CONTEXT[id] = ctx
    return ctx

# --- HLS Rewriter Endpoint ---

@scraper_blueprint.route('/api/hls/<batch_name>/<id>/master.m3u8', methods=['GET'])
def hls_simplified_rewriter(batch_name, id):
    """
    Fetches the HLS master playlist, automatically selects a quality based on the
    `quality` query param (e.g., ?quality=0 for highest), fetches the corresponding
    media playlist, and rewrites its URLs to be playable.
    """
    try:
        ctx = get_lecture_context(batch_name, id)
        
        # Correctly derive the HLS master playlist URL using a robust regex.
        match = re.search(r'(https?://.*?/[a-f0-9\\-]+/)', ctx['original_url'])
        if not match:
            raise Exception("Could not determine the true base URL from the original URL.")
        
        true_base_url = match.group(1)
        hls_master_url = f"{true_base_url}master.m3u8?{ctx['query']}"

        debugger.info(f"[HLS] Fetching HLS master playlist from: {hls_master_url}")
        headers = {'User-Agent': 'Mozilla/5.0', 'Referer': 'https://pw.live/'}
        resp = requests.get(hls_master_url, headers=headers)
        resp.raise_for_status()
        
        master_content = resp.text
        
        # --- Find and rank qualities ---
        qualities = []
        for line in master_content.splitlines():
            if line.strip().endswith('.m3u8'):
                match = re.search(r'hls/(\d+)/main\.m3u8', line)
                if match:
                    qualities.append(int(match.group(1)))
        
        if not qualities:
            debugger.warning("[HLS] No quality levels found in master. Assuming this is already a media playlist.")
            media_content = master_content
            quality_match = re.search(r'hls/(\d+)/', hls_master_url)
            selected_quality = quality_match.group(1) if quality_match else '720' # Fallback default
        else:
            qualities.sort(reverse=True) # Sort from highest to lowest
            
            # --- Select quality based on query param ---
            try:
                quality_index = request.args.get('quality', default=0, type=int)
            except (ValueError, TypeError):
                quality_index = 0
            
            if not (0 <= quality_index < len(qualities)):
                debugger.warning(f"[HLS] Quality index {quality_index} is out of bounds. Defaulting to 0.")
                quality_index = 0
                
            selected_quality = qualities[quality_index]
            debugger.info(f"[HLS] Available qualities: {qualities}. Selected index {quality_index} -> {selected_quality}p")

            # --- Fetch the media playlist for the selected quality ---
            media_playlist_url = f"{true_base_url}hls/{selected_quality}/main.m3u8?{ctx['query']}"
            debugger.info(f"[HLS] Fetching media playlist from: {media_playlist_url}")
            
            media_resp = requests.get(media_playlist_url, headers=headers)
            media_resp.raise_for_status()
            media_content = media_resp.text
        
        # --- Rewrite segment and key URLs in the media playlist ---
        def rewrite_line(line):
            stripped_line = line.strip()
            if stripped_line.endswith('.ts') and not stripped_line.startswith('http'):
                segment_url_base = f"{true_base_url}hls/{selected_quality}/"
                return f"{segment_url_base}{stripped_line}?{ctx['query']}"
            elif stripped_line.startswith('#EXT-X-KEY'):
                uri_match = re.search(r'URI="([^"]+)"', stripped_line)
                if uri_match:
                    original_uri = uri_match.group(1)
                    separator = '&' if '?' in original_uri else '?'
                    new_uri = f"{original_uri}{separator}authorization={batch_api.token}"
                    return line.replace(original_uri, new_uri)
            return line
            
        modified_content = "\n".join([rewrite_line(line) for line in media_content.splitlines()])
        
        debugger.success(f"[HLS] Successfully rewrote and is serving media playlist for {id} at {selected_quality}p")
        
        return Response(modified_content, mimetype='application/vnd.apple.mpegurl', headers={'Access-Control-Allow-Origin': '*'})

    except Exception as e:
        debugger.error(f"[HLS] Error: {e}\n{traceback.format_exc()}")
        return Response(f"Error generating simplified HLS playlist: {e}", status=500)

# --- Other Original Routes ---
# This is a selection of the original routes to keep the file functional

@scraper_blueprint.route('/api/lecture/<batch_name>/<id>', methods=['GET'])
def get_lecture_info(batch_name,id):
    try:
        from mainLogic.big4.Ravenclaw_decrypt.key import LicenseKeyFetcher as Lf
        
        cors_fix = request.args.get('cors_fix', 'false').lower() == 'true'
        debugger.info(f"[SCARPER] get_lecture_info called - batch_name: {batch_name}, id: {id}, cors_fix: {cors_fix}")
        
        if cors_fix:
            base_url = request.host_url.rstrip('/')
            # Point to the new HLS endpoint
            proxy_url = f"{base_url}/api/hls/{batch_name}/{id}/master.m3u8"
            debugger.info(f"[SCARPER] CORS fix enabled - returning HLS proxy URL: {proxy_url}")
            return create_response(data={"url": proxy_url, "key": None, "kid": None})
        else:
            debugger.info(f"[SCARPER] CORS fix disabled - fetching CloudFront URL and keys")
            lf = Lf(batch_api.token, batch_api.random_id)
            keys = lf.get_key(id, batch_name)
            original_url = keys[2]
            debugger.info(f"[SCARPER] Returning CloudFront URL: {original_url[:50]}... with keys")
            return create_response(data={"url": original_url, "key": keys[1], "kid": keys[0]})
            
    except Exception as e:
        debugger.error(f"[SCARPER] Error: {e}")
        return create_response(error=str(e)), 500

@scraper_blueprint.route(f'/api/batches')
def get_batches():
    try:
        batches = batch_api.get_batches_force_hard()
        return create_response(data=batches)
    except Exception as e:
        return create_response(error=str(e)), 500
