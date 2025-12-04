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
from urllib.parse import urlparse
import threading
import concurrent.futures
from functools import wraps

import requests
import urllib3
from flask import Blueprint, jsonify, request, Response, stream_with_context, send_file
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
# Use Absolute Path for Termux compatibility
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
TMP_DIR = os.path.join(BASE_DIR, "tmp_proxy")
ENC_DIR = os.path.join(TMP_DIR, "enc")
DEC_DIR = os.path.join(TMP_DIR, "dec")

# Global Dictionary to store context (Keys, URLs) for active lectures
LECTURE_CONTEXT = {}

# Threading configuration
MAX_WORKER_THREADS = int(os.environ.get('PWDL_DECRYPT_THREADS', '4'))  # Configurable via environment variable
DECRYPT_EXECUTOR = concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKER_THREADS, thread_name_prefix='decrypt-worker')
debugger.info(f"[THREADING] Initialized decrypt thread pool with {MAX_WORKER_THREADS} workers")

# Thread-safe locks for file operations
file_locks = {}
file_locks_lock = threading.Lock()

# Initialize BatchAPI
try:
    batch_api = Endpoints().set_token(vars['prefs'].get('token',{}).get("token",""))
except Exception as e:
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

# --- HELPER FUNCTIONS FOR DECRYPTION ---

def get_file_lock(file_path):
    """Get or create a thread-safe lock for a specific file"""
    with file_locks_lock:
        if file_path not in file_locks:
            file_locks[file_path] = threading.Lock()
        return file_locks[file_path]

def thread_safe_file_operation(func):
    """Decorator to ensure file operations are thread-safe"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Extract file path from args (usually the output path)
        file_path = args[1] if len(args) > 1 else kwargs.get('output_path')
        if file_path:
            lock = get_file_lock(file_path)
            with lock:
                return func(*args, **kwargs)
        else:
            return func(*args, **kwargs)
    return wrapper

def ensure_dirs(lecture_id):
    """Creates specific temp folders for a lecture ID"""
    l_enc = os.path.join(ENC_DIR, lecture_id)
    l_dec = os.path.join(DEC_DIR, lecture_id)
    os.makedirs(l_enc, exist_ok=True)
    os.makedirs(l_dec, exist_ok=True)
    return l_enc, l_dec

@thread_safe_file_operation
def run_mp4decrypt(input_path, output_path, kid, key):
    """Runs mp4decrypt subprocess, ensuring output dir exists (Thread-safe)"""
    try:
        # Check if already decrypted by another thread
        if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            debugger.info(f"[DECRYPT] File already exists: {os.path.basename(output_path)}")
            return True
        
        # Ensure output dir exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        debugger.info(f"[DECRYPT] Starting decryption: {os.path.basename(input_path)} -> {os.path.basename(output_path)}")
        
        key_arg = f"{kid}:{key}"
        cmd = ['mp4decrypt', '--key', key_arg, input_path, output_path]
        
        # Run and capture output
        start_time = time.time()
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        decrypt_time = time.time() - start_time
        
        if result.returncode != 0:
            debugger.error(f"[DECRYPT] mp4decrypt failed for {os.path.basename(output_path)}: {result.stderr}")
            return False
            
        # Verify file creation
        if not os.path.exists(output_path):
            debugger.error(f"[DECRYPT] mp4decrypt returned 0 but file missing: {output_path}")
            return False
            
        debugger.success(f"[DECRYPT] Completed {os.path.basename(output_path)} in {decrypt_time:.2f}s")
        return True
    except Exception as e:
        debugger.error(f"[DECRYPT] Exception in run_mp4decrypt: {e}")
        return False

@thread_safe_file_operation
def fetch_upstream_file(url, dest_path):
    """Downloads file from CloudFront with headers (Thread-safe)"""
    # Check if file exists and has size (another thread might have downloaded it)
    if os.path.exists(dest_path) and os.path.getsize(dest_path) > 0:
        debugger.info(f"[DOWNLOAD] File already exists: {os.path.basename(dest_path)}")
        return True
        
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': 'https://pw.live/'
    }
    try:
        debugger.info(f"[DOWNLOAD] Starting download: {os.path.basename(dest_path)}")
        start_time = time.time()
        
        with requests.get(url, headers=headers, stream=True) as r:
            r.raise_for_status()
            with open(dest_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=65536):
                    f.write(chunk)
        
        download_time = time.time() - start_time
        file_size = os.path.getsize(dest_path) / (1024 * 1024)  # MB
        debugger.success(f"[DOWNLOAD] Completed {os.path.basename(dest_path)} ({file_size:.1f}MB) in {download_time:.2f}s")
        return True
    except Exception as e:
        debugger.error(f"[DOWNLOAD] Failed {os.path.basename(dest_path)}: {e}")
        # Clean up partial file
        if os.path.exists(dest_path): 
            try: os.remove(dest_path)
            except: pass
        return False

def download_and_decrypt_async(url, enc_path, dec_path, kid, key):
    """Async function to download and decrypt a file"""
    def task():
        debugger.info(f"[ASYNC] Starting download+decrypt pipeline for {os.path.basename(enc_path)}")
        start_time = time.time()
        
        # Step 1: Download
        if not fetch_upstream_file(url, enc_path):
            return False
            
        # Step 2: Decrypt
        if not run_mp4decrypt(enc_path, dec_path, kid, key):
            return False
            
        total_time = time.time() - start_time
        debugger.success(f"[ASYNC] Pipeline completed for {os.path.basename(dec_path)} in {total_time:.2f}s")
        return True
    
    return DECRYPT_EXECUTOR.submit(task)

def download_multiple_async(tasks):
    """Download and decrypt multiple files in parallel"""
    futures = []
    for url, enc_path, dec_path, kid, key in tasks:
        future = download_and_decrypt_async(url, enc_path, dec_path, kid, key)
        futures.append((future, dec_path))
    
    # Wait for all tasks to complete
    results = {}
    for future, dec_path in futures:
        try:
            results[dec_path] = future.result(timeout=30)  # 30 second timeout per file
        except concurrent.futures.TimeoutError:
            debugger.error(f"[ASYNC] Timeout for {os.path.basename(dec_path)}")
            results[dec_path] = False
        except Exception as e:
            debugger.error(f"[ASYNC] Exception for {os.path.basename(dec_path)}: {e}")
            results[dec_path] = False
    
    return results

def get_lecture_context(batch_name, id):
    """Retrieves URL/Key from cache or API"""
    ctx = LECTURE_CONTEXT.get(id)
    if not ctx:
        from mainLogic.big4.Ravenclaw_decrypt.key import LicenseKeyFetcher as Lf
        lf = Lf(batch_api.token, batch_api.random_id)
        keys = lf.get_key(id, batch_name) # [kid, key, url]
        
        parsed_url = urllib.parse.urlparse(keys[2])
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}{os.path.dirname(parsed_url.path)}/"
        
        ctx = {
            'kid': keys[0],
            'key': keys[1],
            'original_url': keys[2],
            'base_url': base_url,
            'query': parsed_url.query
        }
        LECTURE_CONTEXT[id] = ctx
    return ctx

# --- ROUTE 1: DASH MANIFEST REWRITER ---

@scraper_blueprint.route('/api/lecture/<batch_name>/<id>/master.mpd', methods=['GET'])
def get_rewritten_manifest(batch_name, id):
    try:
        ctx = get_lecture_context(batch_name, id)

        # Fetch Manifest Content
        headers = {'User-Agent': 'Mozilla/5.0', 'Referer': 'https://pw.live/'}
        resp = requests.get(ctx['original_url'], headers=headers)
        if resp.status_code != 200:
            return Response(f"Failed to fetch upstream manifest: {resp.status_code}", status=502)
        
        content = resp.text
        debugger.info(f"[SCARPER] Original manifest content preview: {content[:200]}...")

        # Strip DRM Tags - More comprehensive removal
        original_content = content
        
        # Remove multi-line ContentProtection tags
        content = re.sub(r'<ContentProtection[^>]*>.*?</ContentProtection>', '', content, flags=re.DOTALL | re.IGNORECASE)
        
        # Remove self-closing ContentProtection tags
        content = re.sub(r'<ContentProtection[^>]*/?>', '', content, flags=re.IGNORECASE)
        
        # Also remove any pssh boxes or DRM-related elements
        content = re.sub(r'<cenc:pssh[^>]*>.*?</cenc:pssh>', '', content, flags=re.DOTALL | re.IGNORECASE)
        content = re.sub(r'<ms:pro[^>]*>.*?</ms:pro>', '', content, flags=re.DOTALL | re.IGNORECASE)
        
        if original_content != content:
            debugger.info(f"[SCARPER] DRM content removed from manifest")
        else:
            debugger.warning(f"[SCARPER] No DRM content found to remove in manifest")
            
        debugger.info(f"[SCARPER] Cleaned manifest content preview: {content[:200]}...")

        # Rewrite Paths to point to Proxy
        def rewrite_path(match):
            attr = match.group(1)
            rel_path = match.group(2)
            # Escape URL for XML (replace & with &amp;)
            proxy_path = html.escape(f'/api/proxy/{batch_name}/{id}/{rel_path}')
            return f'{attr}="{proxy_path}"'

        pattern = r'(initialization|media)="([^"]+)"'
        content = re.sub(pattern, rewrite_path, content)

        # Create response with proper CORS headers
        response = Response(content, mimetype='application/dash+xml')
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        
        return response

    except Exception as e:
        debugger.error(f"Manifest rewrite error: {e}")
        return Response(str(e), status=500)

# --- ROUTE 2: HLS MASTER PLAYLIST ---

@scraper_blueprint.route('/api/lecture/<batch_name>/<id>/master.m3u8', methods=['GET'])
def get_master_m3u8(batch_name, id):
    try:
        ctx = get_lecture_context(batch_name, id)
        
        headers = {'User-Agent': 'Mozilla/5.0', 'Referer': 'https://pw.live/'}
        resp = requests.get(ctx['original_url'], headers=headers)
        
        root = ET.fromstring(resp.text)
        ns = {'d': 'urn:mpeg:dash:schema:mpd:2011'}
        
        lines = ["#EXTM3U", "#EXT-X-VERSION:6"]
        audio_group = "audio-group"
        audio_found = False

        # 1. Scan for AUDIO tracks
        for adapt in root.findall(".//d:AdaptationSet", ns):
            if adapt.get("contentType") == "audio":
                for rep in adapt.findall("d:Representation", ns):
                    rid = rep.get("id")
                    # Using /api/lecture/.../media.m3u8 path structure
                    media_url = f"/api/lecture/{batch_name}/{id}/{rid}/media.m3u8"
                    lines.append(f'#EXT-X-MEDIA:TYPE=AUDIO,GROUP-ID="{audio_group}",NAME="Audio",DEFAULT=YES,AUTOSELECT=YES,URI="{media_url}"')
                    audio_found = True

        # 2. Scan for VIDEO tracks
        for adapt in root.findall(".//d:AdaptationSet", ns):
            if adapt.get("contentType") == "video":
                for rep in adapt.findall("d:Representation", ns):
                    rid = rep.get("id")
                    bw = rep.get("bandwidth")
                    w = rep.get("width")
                    h = rep.get("height")
                    
                    media_url = f"/api/lecture/{batch_name}/{id}/{rid}/media.m3u8"
                    audio_attr = f',AUDIO="{audio_group}"' if audio_found else ""
                    
                    lines.append(f'#EXT-X-STREAM-INF:BANDWIDTH={bw},RESOLUTION={w}x{h},CODECS="avc1.4d401f"{audio_attr}')
                    lines.append(media_url)
                    
        return Response("\n".join(lines), mimetype="application/vnd.apple.mpegurl")

    except Exception as e:
        debugger.error(f"HLS Master Error: {e}")
        return Response(str(e), 500)

# --- ROUTE 3: HLS MEDIA PLAYLIST ---

@scraper_blueprint.route('/api/lecture/<batch_name>/<id>/<rep_id>/media.m3u8', methods=['GET'])
def get_media_m3u8(batch_name, id, rep_id):
    try:
        ctx = get_lecture_context(batch_name, id)
        
        headers = {'User-Agent': 'Mozilla/5.0', 'Referer': 'https://pw.live/'}
        resp = requests.get(ctx['original_url'], headers=headers)
        root = ET.fromstring(resp.text)
        ns = {'d': 'urn:mpeg:dash:schema:mpd:2011'}
        
        # Find Representation
        target_rep = None
        parent_adapt = None
        for adapt in root.findall(".//d:AdaptationSet", ns):
            for rep in adapt.findall("d:Representation", ns):
                if rep.get("id") == str(rep_id):
                    target_rep = rep
                    parent_adapt = adapt
                    break
            if target_rep is not None: break
            
        if target_rep is None: return Response("Representation Not found", 404)
        
        seg_tpl = target_rep.find("d:SegmentTemplate", ns)
        if seg_tpl is None: seg_tpl = parent_adapt.find("d:SegmentTemplate", ns)
        
        timescale = int(seg_tpl.get("timescale"))
        media_tpl = seg_tpl.get("media")
        init_tpl = seg_tpl.get("initialization")
        start_num = int(seg_tpl.get("startNumber", "1"))
        
        # Build M3U8
        lines = ["#EXTM3U", "#EXT-X-VERSION:6", "#EXT-X-TARGETDURATION:6", "#EXT-X-PLAYLIST-TYPE:VOD"]
        
        # Init Map (Point to Proxy)
        init_name = init_tpl.replace("$RepresentationID$", str(rep_id))
        proxy_init = f"/api/proxy/{batch_name}/{id}/{init_name}"
        lines.append(f'#EXT-X-MAP:URI="{proxy_init}"')
        
        # Segments (Point to Proxy)
        timeline = seg_tpl.find("d:SegmentTimeline", ns)
        curr_num = start_num
        
        for s in timeline.findall("d:S", ns):
            d = int(s.get("d"))
            r = int(s.get("r", "0"))
            sec = float(d) / timescale
            
            for _ in range(r + 1):
                seg_name = media_tpl.replace("$RepresentationID$", str(rep_id)).replace("$Number$", str(curr_num))
                proxy_seg = f"/api/proxy/{batch_name}/{id}/{seg_name}"
                
                lines.append(f"#EXTINF:{sec:.6f},")
                lines.append(proxy_seg)
                curr_num += 1
                
        lines.append("#EXT-X-ENDLIST")
        return Response("\n".join(lines), mimetype="application/vnd.apple.mpegurl")

    except Exception as e:
        debugger.error(f"HLS Media Error: {e}")
        return Response(str(e), 500)

# --- ROUTE 4: SEGMENT PROXY (DECRYPTION) ---

@scraper_blueprint.route('/api/proxy/<batch_name>/<id>/<path:filepath>', methods=['GET', 'OPTIONS'])
def proxy_segment_decrypt(batch_name, id, filepath):
    # Handle OPTIONS request for CORS preflight
    if request.method == 'OPTIONS':
        response = Response()
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        return response
    try:
        # 1. Get Context
        try:
            ctx = get_lecture_context(batch_name, id)
        except Exception as e:
            return Response(f"Context failure: {e}", 500)

        # 2. Define Absolute Paths
        l_enc_dir, l_dec_dir = ensure_dirs(id)
        local_enc_path = os.path.join(l_enc_dir, filepath)
        local_dec_path = os.path.join(l_dec_dir, filepath)

        # Return cached if ready
        if os.path.exists(local_dec_path) and os.path.getsize(local_dec_path) > 0:
            response = send_file(local_dec_path, mimetype='video/mp4')
            response.headers['Access-Control-Allow-Origin'] = '*'
            response.headers['Access-Control-Allow-Credentials'] = 'true'
            return response

        # 3. Handle Init Segments (Use async for better performance)
        if filepath.endswith("init.mp4"):
            upstream_url = f"{ctx['base_url']}{filepath}?{ctx['query']}"
            
            debugger.info(f"[PROXY] Processing init segment: {os.path.basename(filepath)}")
            
            # Use async download+decrypt
            future = download_and_decrypt_async(upstream_url, local_enc_path, local_dec_path, ctx['kid'], ctx['key'])
            
            try:
                success = future.result(timeout=20)  # 20 second timeout for init segments
                if not success:
                    return Response("Init Segment Processing Failed", 500)
            except concurrent.futures.TimeoutError:
                return Response("Init Segment Timeout", 504)
            except Exception as e:
                debugger.error(f"[PROXY] Init segment error: {e}")
                return Response("Init Segment Error", 500)
            
            response = send_file(local_dec_path, mimetype='video/mp4')
            response.headers['Access-Control-Allow-Origin'] = '*'
            response.headers['Access-Control-Allow-Credentials'] = 'true'
            return response

        # 4. Handle Media Segments (Enhanced with threading and batch processing)
        else:
            debugger.info(f"[PROXY] Processing media segment: {os.path.basename(filepath)}")
            
            dir_name = os.path.dirname(filepath)
            init_rel_path = f"{dir_name}/init.mp4"
            
            enc_init_path = os.path.join(l_enc_dir, init_rel_path)
            dec_init_path = os.path.join(l_dec_dir, init_rel_path)

            # A. Ensure Decrypted Init Exists (Use async if needed)
            if not os.path.exists(dec_init_path):
                debugger.info(f"[PROXY] Init segment missing, processing asynchronously")
                upstream_init = f"{ctx['base_url']}{init_rel_path}?{ctx['query']}"
                
                # Process init segment asynchronously
                init_future = download_and_decrypt_async(upstream_init, enc_init_path, dec_init_path, ctx['kid'], ctx['key'])
                try:
                    if not init_future.result(timeout=15):  # 15 second timeout for init
                        return Response("Init Processing Failed", 500)
                except concurrent.futures.TimeoutError:
                    return Response("Init Timeout", 504)

            if not os.path.exists(dec_init_path):
                return Response("Init Missing After Processing", 500)

            # B. Get Offset
            offset = os.path.getsize(dec_init_path)

            # C. Download Media Segment (async)
            upstream_seg = f"{ctx['base_url']}{filepath}?{ctx['query']}"
            
            debugger.info(f"[PROXY] Starting async download for media segment")
            download_future = DECRYPT_EXECUTOR.submit(fetch_upstream_file, upstream_seg, local_enc_path)
            
            try:
                if not download_future.result(timeout=25):  # 25 second timeout for download
                    return Response("Media Download Failed", 502)
            except concurrent.futures.TimeoutError:
                return Response("Media Download Timeout", 504)

            # D. Stitch and Decrypt (optimized)
            temp_stitch_enc = local_enc_path + ".st.enc"
            temp_stitch_dec = local_enc_path + ".st.dec"

            try:
                debugger.info(f"[PROXY] Stitching and decrypting media segment")
                start_stitch = time.time()
                
                # Stitch files
                with open(temp_stitch_enc, 'wb') as out:
                    with open(enc_init_path, 'rb') as f: shutil.copyfileobj(f, out)
                    with open(local_enc_path, 'rb') as f: shutil.copyfileobj(f, out)

                # Decrypt stitched file asynchronously
                decrypt_future = DECRYPT_EXECUTOR.submit(run_mp4decrypt, temp_stitch_enc, temp_stitch_dec, ctx['kid'], ctx['key'])
                
                try:
                    if not decrypt_future.result(timeout=20):  # 20 second timeout for decryption
                        return Response("Media Decrypt Failed", 500)
                except concurrent.futures.TimeoutError:
                    return Response("Media Decrypt Timeout", 504)

                # F. Split and Save
                if os.path.exists(temp_stitch_dec):
                    with open(temp_stitch_dec, 'rb') as fin:
                        fin.seek(offset)
                        with open(local_dec_path, 'wb') as fout:
                            shutil.copyfileobj(fin, fout)
                    
                    stitch_time = time.time() - start_stitch
                    debugger.success(f"[PROXY] Media segment processed in {stitch_time:.2f}s")
                    
                    response = send_file(local_dec_path, mimetype='video/mp4')
                    response.headers['Access-Control-Allow-Origin'] = '*'
                    response.headers['Access-Control-Allow-Credentials'] = 'true'
                    return response
                else:
                    return Response("Split Failed: Output missing", 500)

            finally:
                # Cleanup temps
                try:
                    if os.path.exists(temp_stitch_enc): os.remove(temp_stitch_enc)
                    if os.path.exists(temp_stitch_dec): os.remove(temp_stitch_dec)
                except: pass

    except Exception as e:
        debugger.error(f"Proxy error: {e}")
        return Response(str(e), status=500)

# --- EXISTING ROUTES (Unchanged) ---

@scraper_blueprint.route('/proxy/lecture/<path:url>', methods=['GET', 'OPTIONS', 'HEAD'])
def proxy_lecture(url):
    # ... (Your existing proxy_lecture code mostly unchanged) ...
    return Response("Legacy Proxy", status=200)

@scraper_blueprint.route('/api/khazana/lecture/<program_name>/<topic_name>/<lecture_id>/<path:lecture_url>', methods=['GET'])
def get_khazana_lecture(program_name, topic_name, lecture_id, lecture_url):
    try:
        lecture_url = urllib.parse.unquote(lecture_url)
        khazana = batch_api.process("lecture", khazana=True, program_name=program_name, 
                                  topic_name=topic_name, lecture_id=lecture_id, 
                                  lecture_url=lecture_url)
        return create_response(data=khazana)
    except Exception as e:
        debugger.error(f"Error: {e}")
        return create_response(error=str(e)), 500

@scraper_blueprint.route('/api/khazana/<program_name>', methods=['GET'])
def get_khazana_batch(program_name):
    try:
        khazana = batch_api.process("details", khazana=True, program_name=program_name)
        return create_response(data=khazana)
    except Exception as e:
        debugger.error(f"Error: {e}")
        return create_response(error=str(e)), 500

@scraper_blueprint.route('/api/khazana/<program_name>/<subject_name>', methods=['GET'])
def get_khazana_subject(program_name, subject_name):
    try:
        khazana = batch_api.process("subject", khazana=True, program_name=program_name, subject_name=subject_name)
        return create_response(data=khazana)
    except Exception as e:
        debugger.error(f"Error: {e}")
        return create_response(error=str(e)), 500

@scraper_blueprint.route('/api/khazana/<program_name>/<subject_name>/<teacher_name>', methods=['GET'])
def get_khazana_topics(program_name, subject_name, teacher_name):
    try:
        khazana = batch_api.process("topics", khazana=True, program_name=program_name, subject_name=subject_name, teacher_name=teacher_name)
        return create_response(data=khazana)
    except Exception as e:
        debugger.error(f"Error: {e}")
        return create_response(error=str(e)), 500

@scraper_blueprint.route('/api/khazana/<program_name>/<subject_name>/<teacher_name>/<topic_name>', methods=['GET'])
def get_khazana_sub_topics(program_name, subject_name, teacher_name, topic_name):
    try:
        khazana = batch_api.process("sub_topic", khazana=True, program_name=program_name, subject_name=subject_name, teacher_name=teacher_name, topic_name=topic_name)
        return create_response(data=khazana)
    except Exception as e:
        debugger.error(f"Error: {e}")
        return create_response(error=str(e)), 500

@scraper_blueprint.route('/api/khazana/<program_name>/<subject_name>/<teacher_name>/<topic_name>/<sub_topic_name>', methods=['GET'])
def get_khazana_chapter(program_name, subject_name, teacher_name, topic_name, sub_topic_name):
    try:
        khazana = batch_api.process("chapter", khazana=True, program_name=program_name, subject_name=subject_name, teacher_name=teacher_name, topic_name=topic_name, sub_topic_name=sub_topic_name)
        return create_response(data=khazana)
    except Exception as e:
        debugger.error(f"Error: {e}")
        return create_response(error=str(e)), 500

@scraper_blueprint.route('/api/batches/<batch_name>', methods=['GET'])
def get_batch(batch_name):
    try:
        details = batch_api.process("details",batch_name=batch_name)
        return create_response(data=renamer(details,'subject','name'))
    except Exception as e:
        debugger.error(f"Error: {e}")
        return create_response(error=str(e)), 500

@scraper_blueprint.route('/api/batches/<batch_name>/<subject_name>', methods=['GET'])
def get_subject(batch_name, subject_name):
    try:
        subject = batch_api.process("subject",batch_name=batch_name,subject_name=subject_name)
        return create_response(data=renamer(subject,'topic','name'))
    except Exception as e:
        debugger.error(f"Error: {e}")
        return create_response(error=str(e)), 500

@scraper_blueprint.route('/api/batches/<batch_name>/<subject_name>/<chapter_name>/lectures', methods=['GET'])
@scraper_blueprint.route('/api/batches/<batch_name>/<subject_name>/<chapter_name>', methods=['GET'])
def get_chapter(batch_name, subject_name, chapter_name):
    try:
        chapter = batch_api.process("chapter",batch_name=batch_name,subject_name=subject_name,chapter_name=chapter_name)
        return create_response(data=renamer(chapter,'topic','name'))
    except Exception as e:
        debugger.error(f"Error: {e}")
        return create_response(error=str(e)), 500

@scraper_blueprint.route('/api/batches/<batch_name>/<subject_name>/<chapter_name>/notes', methods=['GET'])
def get_notes(batch_name, subject_name, chapter_name):
    try:
        notes = batch_api.process("notes",batch_name=batch_name,subject_name=subject_name,chapter_name=chapter_name)
        return create_response(data=renamer(notes,'topic','name'))
    except Exception as e:
        debugger.error(f"Error: {e}")
        return create_response(error=str(e)), 500

@scraper_blueprint.route('/api/lecture/<batch_name>/<id>', methods=['GET'])
def get_lecture_info(batch_name,id):
    try:
        from mainLogic.big4.Ravenclaw_decrypt.key import LicenseKeyFetcher as Lf
        
        # Check if cors_fix parameter is enabled
        cors_fix = request.args.get('cors_fix', 'false').lower() == 'true'
        debugger.info(f"[SCARPER] get_lecture_info called - batch_name: {batch_name}, id: {id}, cors_fix: {cors_fix}")
        
        if cors_fix:
            # Return backend proxy URL instead of CloudFront URL
            base_url = request.host_url.rstrip('/')
            proxy_url = f"{base_url}/api/lecture/{batch_name}/{id}/master.mpd"
            debugger.info(f"[SCARPER] CORS fix enabled - returning proxy URL: {proxy_url}")
            # No DRM keys needed for proxy URL
            return create_response(data={"url": proxy_url, "key": None, "kid": None})
        else:
            # Original behavior - fetch keys and return CloudFront URL
            debugger.info(f"[SCARPER] CORS fix disabled - fetching CloudFront URL and keys")
            lf = Lf(batch_api.token, batch_api.random_id)
            keys = lf.get_key(id, batch_name)
            original_url = keys[2]
            debugger.info(f"[SCARPER] Returning CloudFront URL: {original_url[:50]}... with keys")
            return create_response(data={"url": original_url, "key": keys[1], "kid": keys[0]})
            
    except Exception as e:
        debugger.error(f"[SCARPER] Error: {e}")
        return create_response(error=str(e)), 500

@scraper_blueprint.route('/api/batches/<batch_name>/<subject_name>/<chapter_name>/dpp_pdf', methods=['GET'])
def get_dpp_pdf(batch_name, subject_name, chapter_name):
    try:
        dpp_pdf = batch_api.process("dpp_pdf",batch_name=batch_name,subject_name=subject_name,chapter_name=chapter_name)
        return create_response(data=renamer(dpp_pdf,'topic','name'))
    except Exception as e:
        debugger.error(f"Error: {e}")
        return create_response(error=str(e)), 500

@scraper_blueprint.route('/api/normal/subjects', methods=['GET'])
def get_normal_subjects():
    try:
        batch_name = request.args.get('batch_name')
        details = batch_api.process("details",batch_name=batch_name)
        return create_response(data=renamer(details,'subject','name'))
    except Exception as e:
        debugger.error(f"Error: {e}")
        return create_response(error=str(e)), 500

@scraper_blueprint.route('/api/normal/chapters/<subject_slug>', methods=['GET'])
def get_normal_chapters(subject_slug):
    try:
        batch_name = request.args.get('batch_name')
        chapters = batch_api.process("subject",batch_name=batch_name,subject_name=subject_slug)
        return create_response(data=chapters)
    except Exception as e:
        debugger.error(e)
        return create_response(error=str(e)), 500

@scraper_blueprint.route('/api/normal/videos', methods=['GET'])
def get_normal_videos():
    try:
        batch_name = request.args.get('batch_name',)
        subject_slug = request.args.get('subject_slug')
        chapter_slug = request.args.get('chapter_slug')
        if not all([subject_slug, chapter_slug]):
                return create_response(error="Missing required parameters"), 400
        videos = batch_api.process("chapter",batch_name=batch_name,subject_name=subject_slug,chapter_name=chapter_slug)
        return create_response(data=renamer(videos,'topic','name'))
    except Exception as e:
        return create_response(error=str(e)), 500

@scraper_blueprint.route('/api/private/<client_id>/test/<test_id>', methods=['GET'])
def get_private_test(client_id,test_id):
    try:
        IMAGES_PER_PAGE = 4
        client_id= generate_safe_file_name(client_id)
        CLIENT_DIR = os.path.join(glv_var.api_webdl_directory,client_id)
        WRONG_Q_DIR = os.path.join(str(CLIENT_DIR),"wrong_questions")
        UNATTEMPTED_Q_DIR = os.path.join(str(CLIENT_DIR),"unattempted_questions")
        os.makedirs(WRONG_Q_DIR, exist_ok=True)
        os.makedirs(UNATTEMPTED_Q_DIR, exist_ok=True)
        try:
            test = batch_api.get_test(test_id).data
            questions = test.questions
            wrong_q_info = []
            unattempted_q_info = []
            for i, q in enumerate(questions):
                option = q.yourResult.markedSolutions[0] if q.yourResult.markedSolutions else None
                actual_option = q.topperResult.markedSolutions[0] if q.topperResult.markedSolutions else None
                if option:
                    options, index = [op._id for op in q.question.options], options.index(option)
                    option = q.question.options[index].texts.en if index < len(q.question.options) else None
                if actual_option:
                    options, index = [op._id for op in q.question.options], options.index(actual_option)
                    actual_option = q.question.options[index].texts.en if index < len(q.question.options) else None
                info_dict = {
                    "link": q.question.imageIds.link, "question_number": str(q.question.questionNumber),
                    "time_taken": getattr(q.yourResult, 'timeTaken', 'N/A'), "subject": str(q.question.topicId.name),
                    "marked_solution":str(option or 'X'), "actual_solution":str(actual_option or 'X'),
                    "filename": f"q{q.question.questionNumber:03d}_{q.question.imageIds.name}-{i}.png"
                }
                if q.yourResult.status == "WRONG": wrong_q_info.append(info_dict)
                elif q.yourResult.status == "UnAttempted": unattempted_q_info.append(info_dict)
            for info in wrong_q_info: ScraperModule().download_file(url=info['link'], destination_folder=WRONG_Q_DIR, filename=info['filename'])
            for info in unattempted_q_info: ScraperModule().download_file(url=info['link'], destination_folder=UNATTEMPTED_Q_DIR, filename=info['filename'])
            WRONG_PDF_NAME, UNATTEMPTED_PDF_NAME = f"{test.test.name}_WRONG.pdf", f"{test.test.name}_UNATTEMPTED.pdf"
            create_a4_pdf_from_images(image_info=wrong_q_info, base_folder=WRONG_Q_DIR, output_filename=str(os.path.join(str(CLIENT_DIR), WRONG_PDF_NAME)), images_per_page=IMAGES_PER_PAGE)
            create_a4_pdf_from_images(image_info=unattempted_q_info, base_folder=UNATTEMPTED_Q_DIR, output_filename=str(os.path.join(str(CLIENT_DIR), UNATTEMPTED_PDF_NAME)), images_per_page=IMAGES_PER_PAGE)
            return create_response(data={"test":test.test.name, "client_id":client_id, "wrong_pdf_url":ENDPOINTS_NAME.GET_PVT_FILE_FOR_A_CLIENT(client_id=client_id,name=WRONG_PDF_NAME), "unattempted_pdf_url":ENDPOINTS_NAME.GET_PVT_FILE_FOR_A_CLIENT(client_id=client_id,name=UNATTEMPTED_PDF_NAME)})
        finally:
            for folder in [WRONG_Q_DIR, UNATTEMPTED_Q_DIR]:
                if os.path.exists(folder):
                    try: shutil.rmtree(folder)
                    except OSError as e: print(f"Error removing folder {folder}: {e}")
    except Exception as e:
        debugger.error(f"Error: {e}")
        return create_response(error=str(e)), 500

@scraper_blueprint.route('/api/private/test_mappings_for_me', methods=['GET'])
def get_private_test_mappings_for_me():
    all_test = AllTestDetails.from_json(Endpoint(
        url="https://api.penpencil.co/v3/test-service/tests?testType=All&testStatus=All&attemptStatus=All&batchId=678b4cf5a3a368218a2b16e7&isSubjective=false&isPurchased=true&testCategoryIds=6814be5e9467bd0a54703a94",
        headers=ScraperModule.batch_api.DEFAULT_HEADERS
    ).fetch()[0])
    data = {test.name: str(test.testStudentMappingId) for test in all_test.data}
    return create_response(data=data)

@scraper_blueprint.route(f'/api/batches')
def get_batches():
    try:
        batches = batch_api.get_batches_force_hard()
        return create_response(data=batches)
    except Exception as e:
        return create_response(error=str(e)), 500

@scraper_blueprint.route('/api/set-token', methods=['POST'])
def set_token():
    try:
        token = request.json.get('token')
        if not token:
            return create_response(error="Token is required"), 400
        batch_api.token = token
        return create_response(data={"message": "Token updated successfully"})
    except Exception as e:
        return create_response(error=str(e)), 500

@scraper_blueprint.route('/api/threading/status', methods=['GET'])
def get_threading_status():
    """Get current threading status and performance metrics"""
    try:
        active_threads = threading.active_count()
        executor_stats = {
            'max_workers': DECRYPT_EXECUTOR._max_workers,
            'active_threads': active_threads,
            'pending_tasks': DECRYPT_EXECUTOR._work_queue.qsize() if hasattr(DECRYPT_EXECUTOR._work_queue, 'qsize') else 'N/A'
        }
        return create_response(data=executor_stats)
    except Exception as e:
        return create_response(error=str(e)), 500

# Cleanup function for graceful shutdown
def cleanup_resources():
    """Clean up thread pool and temporary files"""
    try:
        debugger.info("[CLEANUP] Shutting down decrypt thread pool...")
        DECRYPT_EXECUTOR.shutdown(wait=True, timeout=30)
        debugger.info("[CLEANUP] Thread pool shutdown complete")
        
        # Clean up old temp files
        if os.path.exists(TMP_DIR):
            for root, dirs, files in os.walk(TMP_DIR):
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        # Remove files older than 1 hour
                        if os.path.getmtime(file_path) < time.time() - 3600:
                            os.remove(file_path)
                    except OSError:
                        pass
        debugger.info("[CLEANUP] Temporary files cleaned")
        
    except Exception as e:
        debugger.error(f"[CLEANUP] Error during cleanup: {e}")

# Register cleanup function
import atexit
atexit.register(cleanup_resources)
