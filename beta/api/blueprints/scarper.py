import urllib.parse

import urllib3
from flask import Blueprint, jsonify, request
from beta.batch_scraper_2.Endpoints import Endpoints
from mainLogic.utils.dependency_checker import re_check_dependencies
from mainLogic.utils.glv import Global
from mainLogic.utils.glv_var import debugger
from mainLogic.utils import glv_var
# Initialize the blueprint
scraper_blueprint = Blueprint('scraper', __name__)

# Initialize BatchAPI with a default token. The token can be updated later via the '/api/set-token' route.
try:
    batch_api = Endpoints().set_token(vars['prefs'].get('token',{}).get("token",""))
except Exception as e:
    # get token via check_Dependencies
    re_check_dependencies()
    debugger.debug(glv_var.vars['prefs'])
    access_token = glv_var.vars['prefs'].get('token_config',{})
    batch_api = Endpoints().set_token(access_token.get("token",""),access_token.get("randomId",""))

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
            debugger.error(f"Error renaming f{old_key} to {new_key}: {e}")
        new_data.append(element)

    return new_data
# from werkzeug.urls import url_quote, url_unquote

@scraper_blueprint.route('/api/khazana/lecture/<program_name>/<topic_name>/<lecture_id>/<path:lecture_url>', methods=['GET'])
def get_khazana_lecture(program_name, topic_name, lecture_id, lecture_url):
    try:
        debugger.success(f"batch_name: {program_name}")
        debugger.success(f"batch_api.token: {batch_api.token}")
        debugger.success(f"batch_api.random_id: {batch_api.random_id}")

        # decode lecture_url
        lecture_url = urllib.parse.unquote(lecture_url)
        # print the vars
        debugger.success(f"lecture_url: {lecture_url}")
        debugger.success(f"lecture_id: {lecture_id}")
        debugger.success(f"topic_name: {topic_name}")
        debugger.success(f"program_name: {program_name}")

        
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
        debugger.success(f"batch_name: {program_name}")
        debugger.success(f"batch_api.token: {batch_api.token}")
        debugger.success(f"batch_api.random_id: {batch_api.random_id}")

        # batch_api.batch_name = batch_name
        # khazana = batch_api.GET_KHAZANA_BATCH(batch_name)
        khazana = batch_api.process("details", khazana=True, program_name=program_name)
        return create_response(data=khazana)
    except Exception as e:
        debugger.error(f"Error: {e}")
        return create_response(error=str(e)), 500

@scraper_blueprint.route('/api/khazana/<program_name>/<subject_name>', methods=['GET'])
def get_khazana_subject(program_name, subject_name):
    try:
        debugger.success(f"batch_name: {program_name}")
        debugger.success(f"batch_api.token: {batch_api.token}")
        debugger.success(f"batch_api.random_id: {batch_api.random_id}")

        # batch_api.batch_name = batch_name
        # khazana = batch_api.GET_KHAZANA_BATCH(batch_name)
        khazana = batch_api.process("subject", khazana=True, program_name=program_name, subject_name=subject_name)
        return create_response(data=khazana)
    except Exception as e:
        debugger.error(f"Error: {e}")
        return create_response(error=str(e)), 500

@scraper_blueprint.route('/api/khazana/<program_name>/<subject_name>/<teacher_name>', methods=['GET'])
def get_khazana_topics(program_name, subject_name, teacher_name):
    try:
        debugger.success(f"batch_name: {program_name}")
        debugger.success(f"batch_api.token: {batch_api.token}")
        debugger.success(f"batch_api.random_id: {batch_api.random_id}")

        # batch_api.batch_name = batch_name
        # khazana = batch_api.GET_KHAZANA_BATCH(batch_name)
        khazana = batch_api.process("topics", khazana=True, program_name=program_name, subject_name=subject_name, teacher_name=teacher_name)
        return create_response(data=khazana)
    except Exception as e:
        debugger.error(f"Error: {e}")
        return create_response(error=str(e)), 500

@scraper_blueprint.route('/api/khazana/<program_name>/<subject_name>/<teacher_name>/<topic_name>', methods=['GET'])
def get_khazana_sub_topics(program_name, subject_name, teacher_name, topic_name):
    try:
        debugger.success(f"batch_name: {program_name}")
        debugger.success(f"batch_api.token: {batch_api.token}")
        debugger.success(f"batch_api.random_id: {batch_api.random_id}")

        # batch_api.batch_name = batch_name
        # khazana = batch_api.GET_KHAZANA_BATCH(batch_name)
        khazana = batch_api.process("sub_topic", khazana=True, program_name=program_name, subject_name=subject_name, teacher_name=teacher_name, topic_name=topic_name)
        return create_response(data=khazana)
    except Exception as e:
        debugger.error(f"Error: {e}")
        return create_response(error=str(e)), 500

@scraper_blueprint.route('/api/khazana/<program_name>/<subject_name>/<teacher_name>/<topic_name>/<sub_topic_name>', methods=['GET'])
def get_khazana_chapter(program_name, subject_name, teacher_name, topic_name, sub_topic_name):
    try:
        debugger.success(f"batch_name: {program_name}")
        debugger.success(f"batch_api.token: {batch_api.token}")
        debugger.success(f"batch_api.random_id: {batch_api.random_id}")

        # batch_api.batch_name = batch_name
        # khazana = batch_api.GET_KHAZANA_BATCH(batch_name)
        khazana = batch_api.process("chapter", khazana=True, program_name=program_name, subject_name=subject_name, teacher_name=teacher_name, topic_name=topic_name, sub_topic_name=sub_topic_name)
        return create_response(data=khazana)
    except Exception as e:
        debugger.error(f"Error: {e}")
        return create_response(error=str(e)), 500

@scraper_blueprint.route('/api/batches/<batch_name>', methods=['GET'])
def get_batch(batch_name):
    try:
        debugger.success(f"batch_name: {batch_name}")
        debugger.success(f"batch_api.token: {batch_api.token}")
        debugger.success(f"batch_api.random_id: {batch_api.random_id}")

        # batch_api.batch_name = batch_name
        # subjects = batch_api.GET_BATCH(batch_name)
        details = batch_api.process("details",batch_name=batch_name)
        return create_response(data=renamer(details,'subject','name'))
    except Exception as e:
        debugger.error(f"Error: {e}")
        return create_response(error=str(e)), 500

@scraper_blueprint.route('/api/batches/<batch_name>/<subject_name>', methods=['GET'])
def get_subject(batch_name, subject_name):
    try:
        debugger.success(f"batch_name: {batch_name}")
        debugger.success(f"batch_api.token: {batch_api.token}")
        debugger.success(f"batch_api.random_id: {batch_api.random_id}")

        # batch_api.batch_name = batch_name
        # subjects = batch_api.GET_BATCH(batch_name)
        subject = batch_api.process("subject",batch_name=batch_name,subject_name=subject_name)
        return create_response(data=renamer(subject,'topic','name'))
    except Exception as e:
        debugger.error(f"Error: {e}")
        return create_response(error=str(e)), 500

@scraper_blueprint.route('/api/batches/<batch_name>/<subject_name>/<chapter_name>/lectures', methods=['GET'])
@scraper_blueprint.route('/api/batches/<batch_name>/<subject_name>/<chapter_name>', methods=['GET'])
def get_chapter(batch_name, subject_name, chapter_name):
    try:
        debugger.success(f"batch_name: {batch_name}")
        debugger.success(f"batch_api.token: {batch_api.token}")
        debugger.success(f"batch_api.random_id: {batch_api.random_id}")

        # batch_api.batch_name = batch_name
        # subjects = batch_api.GET_BATCH(batch_name)
        chapter = batch_api.process("chapter",batch_name=batch_name,subject_name=subject_name,chapter_name=chapter_name)
        return create_response(data=renamer(chapter,'topic','name'))
    except Exception as e:
        debugger.error(f"Error: {e}")
        return create_response(error=str(e)), 500

@scraper_blueprint.route('/api/batches/<batch_name>/<subject_name>/<chapter_name>/notes', methods=['GET'])
def get_notes(batch_name, subject_name, chapter_name):
    try:
        debugger.success(f"batch_name: {batch_name}")
        debugger.success(f"batch_api.token: {batch_api.token}")
        debugger.success(f"batch_api.random_id: {batch_api.random_id}")

        # batch_api.batch_name = batch_name
        # subjects = batch_api.GET_BATCH(batch_name)
        notes = batch_api.process("notes",batch_name=batch_name,subject_name=subject_name,chapter_name=chapter_name)
        return create_response(data=renamer(notes,'topic','name'))
    except Exception as e:

        debugger.error(f"Error: {e}")
        return create_response(error=str(e)), 500


@scraper_blueprint.route('/normal/subjects', methods=['GET'])
@scraper_blueprint.route('/api/normal/subjects', methods=['GET'])
def get_normal_subjects():
    try:
        batch_name = request.args.get('batch_name')
        # batch_api.batch_name = batch_name
        # subjects = batch_api.GET_NORMAL_SUBJECTS()
        details = batch_api.process("details",batch_name=batch_name)
        return create_response(data=renamer(details,'subject','name'))
    except Exception as e:
        debugger.error(f"Error: {e}")
        return create_response(error=str(e)), 500

@scraper_blueprint.route('/normal/chapters/<subject_slug>', methods=['GET'])
@scraper_blueprint.route('/api/normal/chapters/<subject_slug>', methods=['GET'])
def get_normal_chapters(subject_slug):
    try:
        batch_name = request.args.get('batch_name')
        # batch_api.batch_name = batch_name

        Global.hr()
        debugger.success(f"batch_name: {batch_name}")
        debugger.success(f"subject_slug: {subject_slug}")
        Global.hr()


        chapters = batch_api.process("subject",batch_name=batch_name,subject_name=subject_slug)

        debugger.success(f"chapters: {chapters}")

        return create_response(data=chapters)
    except Exception as e:

        debugger.error(e)
        return create_response(error=str(e)), 500

@scraper_blueprint.route('/normal/lectures', methods=['GET'])
@scraper_blueprint.route('/api/normal/lectures', methods=['GET'])
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