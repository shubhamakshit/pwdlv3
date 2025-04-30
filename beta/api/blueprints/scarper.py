# scraper_blueprint.py

from flask import Blueprint, jsonify, request
from beta.batch_scraper_2.Endpoints import Endpoints
from mainLogic.utils.glv import Global
from mainLogic.utils.glv_var import debugger,vars

# Initialize the blueprint
scraper_blueprint = Blueprint('scraper', __name__)

# Initialize BatchAPI with a default token. The token can be updated later via the '/api/set-token' route.
batch_api = Endpoints().set_token(vars['prefs'].get('token',{}).get("token",""))

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

@scraper_blueprint.route('/subjects', methods=['GET'])
@scraper_blueprint.route('/api/subjects', methods=['GET'])
def get_subjects():
    try:
        batch_name = request.args.get('batch_name', batch_api.batch_name)
        batch_api.batch_name = batch_name
        subjects = batch_api.GET_KHAZANA_SUBJECTS()
        return create_response(data=subjects)
    except Exception as e:
        return create_response(error=str(e)), 500

@scraper_blueprint.route('/batches/<subject_slug>', methods=['GET'])
@scraper_blueprint.route('/api/batches/<subject_slug>', methods=['GET'])
def get_topics(subject_slug):
    try:
        batch_name = request.args.get('batch_name', batch_api.batch_name)
        batch_api.batch_name = batch_name
        topics = batch_api.GET_KHAZANA_BATCHES(subject_slug)
        return create_response(data=topics)
    except Exception as e:
        return create_response(error=str(e)), 500

@scraper_blueprint.route('/chapters/<subject_slug>', methods=['GET'])
@scraper_blueprint.route('/api/chapters/<subject_slug>', methods=['GET'])
def get_subtopics(subject_slug):
    try:
        batch_name = request.args.get('batch_name', batch_api.batch_name)
        batch_api.batch_name = batch_name
        subtopics = batch_api.GET_KHAZANA_CHAPTERS(subject_slug)
        return create_response(data=subtopics)
    except Exception as e:
        return create_response(error=str(e)), 500

@scraper_blueprint.route('/lectures', methods=['GET'])
@scraper_blueprint.route('/api/lectures', methods=['GET'])
def get_lectures():
    try:
        batch_name = request.args.get('batch_name', batch_api.batch_name)
        subject_slug = request.args.get('subject_slug')
        chapter_slug = request.args.get('chapter_slug')

        if not all([subject_slug, chapter_slug]):
            return create_response(error="Missing required parameters"), 400

        batch_api.batch_name = batch_name

        lectures = batch_api.GET_KHAZANA_LECTURES(
            batch_name, subject_slug, chapter_slug
        )
        return create_response(data=lectures)
    except Exception as e:
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


@scraper_blueprint.route('/api/batches')
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
