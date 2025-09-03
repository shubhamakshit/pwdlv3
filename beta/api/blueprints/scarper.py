import json
import os
import re
import shutil
import traceback
import urllib.parse
from urllib.parse import urlparse

import requests
import urllib3
from flask import Blueprint, jsonify, request, Response, stream_with_context
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

# Initialize BatchAPI with a default token.
try:
    batch_api = Endpoints().set_token(vars['prefs'].get('token',{}).get("token",""))
except Exception as e:
    re_check_dependencies()
    token = glv_var.vars["prefs"].get("token_config",{})
    try:
        access_token = token["access_token"]
    except Exception as e:
        debugger.error(f"Error getting access token: {e}")
        try:
            access_token = token["token"]
        except Exception as e:
            debugger.error(f"Error getting access token: {e}")

    random_id = token.get("random_id",None)
    try:
        if random_id is None:
            batch_api = Endpoints().set_token(access_token)
        else:
            batch_api = Endpoints().set_token(access_token,random_id=random_id)
    except Exception as e :
        debugger.error("Failed to create batch_api instance, maybe the access_token is not available")
        debugger.error(f"Scraper may not work as intended: {e}")

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
        except Exception as e:
            debugger.error(f"Error renaming {old_key} to {new_key}: {e}")
        new_data.append(element)
    return new_data

# +++++++ USER-PROVIDED PROXY IMPLEMENTATION +++++++

@scraper_blueprint.route('/proxy/lecture/<path:url>', methods=['GET', 'OPTIONS', 'HEAD'])
def proxy_lecture(url):
    """
    Correctly streams proxied requests with proper CORS handling.
    """
    # Disable InsecureRequestWarning from urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    decoded_url = urllib.parse.unquote(url)
    origin = request.headers.get('Origin', '*')
    
    # Common CORS headers
    cors_headers = {
        'Access-Control-Allow-Origin': origin,
        'Access-Control-Allow-Methods': 'GET, HEAD, OPTIONS',
        'Access-Control-Allow-Headers': 'Origin, X-Requested-With, Content-Type, Accept, Authorization, Range',
        'Access-Control-Allow-Private-Network': 'true',
        'Access-Control-Expose-Headers': 'Content-Length, Content-Range, Accept-Ranges',
        'Vary': 'Origin'
    }

    # 1. Handle CORS Preflight (OPTIONS) request
    if request.method == 'OPTIONS':
        return Response(status=204, headers=cors_headers)

    # 2. Handle actual data requests (GET/HEAD)
    resp = None
    try:
        # Forward necessary headers, including Range for video seeking
        headers_to_forward = {
            key: value for key, value in request.headers.items()
            if key.lower() not in ['host', 'origin', 'referer', 'connection', 'accept-encoding']
        }
        
        # Add user agent if not present
        if 'user-agent' not in headers_to_forward:
            headers_to_forward['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'

        # Make the request
        resp = requests.get(decoded_url, stream=True, headers=headers_to_forward, verify=False)
        resp.raise_for_status()

        # Check if the request is for a DASH manifest file
        if '.mpd' in decoded_url.lower() or 'dash' in resp.headers.get('Content-Type', '').lower():
            # --- MANIFEST REWRITING LOGIC ---
            original_content = resp.text
            
            # The base path of the original URL, used for resolving relative paths
            base_path = '/'.join(decoded_url.split('/')[:-1])
            
            # The base URL of our proxy, used to prefix rewritten URLs
            proxy_base = f"http://{request.host}/proxy/lecture/"
            
            modified_content = original_content

            # --- URL Rewriting using REGEX for robustness ---

            # Rewrite <BaseURL> tags
            # It handles cases where BaseURL is relative (e.g., "video/")
            def rewrite_base_url(match):
                base_url_val = match.group(1)
                if base_url_val.startswith('http'):
                    return match.group(0) # Already absolute, don't touch
                # It's relative, construct the full proxied path
                return f'<BaseURL>{proxy_base}{base_path}/{base_url_val}</BaseURL>'

            modified_content = re.sub(r'<BaseURL>([^<]+)</BaseURL>', rewrite_base_url, modified_content)

            # Rewrite media="path/to/segment.m4s" and initialization="path/to/init.mp4"
            def rewrite_media_url(match):
                attr, url_val = match.groups()
                if url_val.startswith('http'):
                    return match.group(0) # Already absolute
                # It's relative, construct the full proxied path
                return f'{attr}="{proxy_base}{base_path}/{url_val}"'
                
            modified_content = re.sub(r'(media|initialization)="([^"]+)"', rewrite_media_url, modified_content)

            response = Response(modified_content, status=resp.status_code)
            response.headers['Content-Type'] = resp.headers.get('Content-Type', 'application/dash+xml')
            response.headers['Content-Length'] = str(len(modified_content.encode('utf-8')))
            
        else:
            # --- MEDIA CHUNK STREAMING LOGIC ---
            def generate():
                try:
                    for chunk in resp.iter_content(chunk_size=8192):
                        if chunk:
                            yield chunk
                finally:
                    if resp:
                        resp.close()
            
            # Copy response headers from origin, excluding problematic ones
            response_headers = {}
            for key, value in resp.headers.items():
                if key.lower() not in ['connection', 'transfer-encoding', 'content-encoding']:
                    response_headers[key] = value
            
            response = Response(stream_with_context(generate()), 
                              status=resp.status_code, 
                              headers=response_headers)

        # Add CORS headers to the final response
        response.headers.update(cors_headers)
        
        # Add cache headers for media segments to improve performance
        if any(ext in decoded_url.lower() for ext in ['.m4s', '.mp4', '.m4a', '.m4v']):
            response.headers['Cache-Control'] = 'public, max-age=3600'
        
        return response

    except requests.exceptions.RequestException as e:
        if resp:
            resp.close()
        debugger.error(f"Request error for URL {decoded_url}: {str(e)}")
        error_response = jsonify({"error": f"Proxy request failed: {str(e)}"})
        error_response.headers.update(cors_headers)
        return error_response, 502
        
    except Exception as e:
        if resp:
            resp.close()
        error_details = traceback.format_exc()
        debugger.error(f"Proxy error for URL {decoded_url}:\n{error_details}")
        error_response = jsonify({"error": f"Proxy failed: {str(e)}"})
        error_response.headers.update(cors_headers)
        return error_response, 500

# --- [The rest of your API routes are unchanged] ---

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
        lf = Lf(batch_api.token, batch_api.random_id)
        keys = lf.get_key(id,batch_name)

        original_url = keys[2]
        encoded_original_url = urllib.parse.quote(original_url, safe='')
        proxied_url = f"http://{request.host}/proxy/lecture/{encoded_original_url}"
        
        return create_response(data={"url": proxied_url, "key":keys[1], "kid":keys[0]})
    except Exception as e:
        debugger.error(f"Error: {e}")
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
