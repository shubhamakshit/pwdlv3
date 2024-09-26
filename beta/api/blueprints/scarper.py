from flask import Flask, jsonify, request, Blueprint
from beta.batch_scraper.app import BatchAPI  # Assuming the original code is in a file named BatchAPI.py


def create_scraper_blueprint(token=None):
    scraper = Blueprint('scraper', __name__)

    # Initialize BatchAPI with the provided token or a default token
    batch_api = BatchAPI("12th-neet-khazana-370407", token)

    def create_response(data=None, error=None):
        response = {"data": data}
        if error is not None:
            response["error"] = error
        return jsonify(response)

    @scraper.route('/subjects', methods=['GET'])
    @scraper.route('/api/subjects', methods=['GET'])
    def get_subjects():
        try:
            batch_name = request.args.get('batch_name', batch_api.batch_name)
            batch_api.batch_name = batch_name
            subjects = batch_api.get_subject_details_khazana()
            return create_response(data=subjects)
        except Exception as e:
            return create_response(error=str(e)), 500

    @scraper.route('/batches/<subject_slug>', methods=['GET'])
    @scraper.route('/api/batches/<subject_slug>', methods=['GET'])
    def get_topics(subject_slug):
        try:
            batch_name = request.args.get('batch_name', batch_api.batch_name)
            batch_api.batch_name = batch_name
            topics = batch_api.get_batches_of_subject_khazana(subject_slug)
            return create_response(data=topics)
        except Exception as e:
            return create_response(error=str(e)), 500

    @scraper.route('/chapters/<subject_slug>', methods=['GET'])
    @scraper.route('/api/chapters/<subject_slug>', methods=['GET'])
    def get_subtopics(subject_slug):
        try:
            batch_name = request.args.get('batch_name', batch_api.batch_name)
            batch_api.batch_name = batch_name
            subtopics = batch_api.get_topics_of_subject_of_a_batch_khazana(subject_slug)
            return create_response(data=subtopics)
        except Exception as e:
            return create_response(error=str(e)), 500

    @scraper.route('/lectures', methods=['GET'])
    @scraper.route('/api/lectures', methods=['GET'])
    def get_lectures():
        try:
            batch_name = request.args.get('batch_name', batch_api.batch_name)
            subject_slug = request.args.get('subject_slug')
            chapter_slug = request.args.get('chapter_slug')
            #topic_id = request.args.get('topic_id')

            if not all([subject_slug, chapter_slug]):
                return create_response(error="Missing required parameters"), 400

            batch_api.batch_name = batch_name
            lectures = batch_api.get_lectures_of_topic_of_subject_of_a_batch_khazana(
                batch_name, subject_slug, chapter_slug
            )
            return create_response(data=lectures)
        except Exception as e:
            return create_response(error=str(e)), 500

    @scraper.route('/normal/subjects', methods=['GET'])
    @scraper.route('/api/normal/subjects', methods=['GET'])
    def get_normal_subjects():
        try:
            batch_name = request.args.get('batch_name', batch_api.batch_name)
            batch_api.batch_name = batch_name
            subjects = batch_api.get_subjects_details()
            return create_response(data=subjects)
        except Exception as e:
            return create_response(error=str(e)), 500

    @scraper.route('/normal/chapters/<subject_slug>', methods=['GET'])
    @scraper.route('/api/normal/chapters/<subject_slug>', methods=['GET'])
    def get_normal_chapters(subject_slug):
        try:
            batch_name = request.args.get('batch_name', batch_api.batch_name)
            batch_api.batch_name = batch_name
            chapters = batch_api.get_chapter_slugs(subject_slug)
            return create_response(data=chapters)
        except Exception as e:
            return create_response(error=str(e)), 500

    @scraper.route('/normal/lectures', methods=['GET'])
    @scraper.route('/api/normal/lectures', methods=['GET'])
    @scraper.route('/api/normal/videos', methods=['GET'])
    def get_normal_videos():
        try:
            batch_name = request.args.get('batch_name', batch_api.batch_name)
            subject_slug = request.args.get('subject_slug')
            chapter_slug = request.args.get('chapter_slug')

            if not all([subject_slug, chapter_slug]):
                return create_response(error="Missing required parameters"), 400

            batch_api.batch_name = batch_name
            videos = batch_api.get_video_data(subject_slug, chapter_slug)
            return create_response(data=videos)
        except Exception as e:
            return create_response(error=str(e)), 500


    @scraper.route('/api/set-token', methods=['POST'])
    def set_token():
        try:
            token = request.json.get('token')
            if not token:
                return create_response(error="Token is required"), 400
            batch_api.token = token
            return create_response(data={"message": "Token updated successfully"})
        except Exception as e:
            return create_response(error=str(e)), 500

    return scraper

# Usage example:
# app = Flask(__name__)
# scraper_blueprint = create_scraper_blueprint(token="your_token_here")
# app.register_blueprint(scraper_blueprint, url_prefix='/scraper')
