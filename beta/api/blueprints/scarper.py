import json
import os
import shutil
import urllib.parse

import urllib3
from flask import Blueprint, jsonify, request
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

# Initialize BatchAPI with a default token. The token can be updated later via the '/api/set-token' route.

try:

    batch_api = Endpoints().set_token(vars['prefs'].get('token',{}).get("token",""))
except Exception as e:
    # get token via check_Dependencies

    re_check_dependencies()
    token = glv_var.vars["prefs"].get("token_config",{})
    #debugger.debug(f"Token config: {token}")
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
        debugger.error("Scraper may not work as intended")
        debugger.error(e)

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
        import json
        debugger.debug(json.dumps(chapter))
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

@scraper_blueprint.route('/api/lecture/<batch_name>/<id>', methods=['GET'])
def get_lecture_info(batch_name,id):

    try:
        args = request.args
        debugger.success(f"batch_name: {batch_name}")
        url = args.get("url","")
        topic_name = args.get("topic_name","")
        debugger.success(f"batch_api.token: {batch_api.token}")
        debugger.success(f"batch_api.random_id: {batch_api.random_id}")

        # batch_api.batch_name = batch_name
        # subjects = batch_api.GET_BATCH(batch_name)
        #notes = batch_api.process("notes",batch_name=batch_name,subject_name=subject_name,chapter_name=chapter_name)
        from mainLogic.big4.Ravenclaw_decrypt.key import LicenseKeyFetcher as Lf
        lf = Lf(batch_api.token, batch_api.random_id)
        keys = lf.get_key(id,batch_name)

        return create_response(data={
            "url":keys[2],
            "key":keys[1],
            "kid":keys[0]
            })
        
    except Exception as e:

        debugger.error(f"Error: {e}")
        return create_response(error=str(e)), 500
    
@scraper_blueprint.route('/api/batches/<batch_name>/<subject_name>/<chapter_name>/dpp_pdf', methods=['GET'])
def get_dpp_pdf(batch_name, subject_name, chapter_name):
    try:
        debugger.success(f"batch_name: {batch_name}")
        debugger.success(f"batch_api.token: {batch_api.token}")
        debugger.success(f"batch_api.random_id: {batch_api.random_id}")

        # batch_api.batch_name = batch_name
        # subjects = batch_api.GET_BATCH(batch_name)
        dpp_pdf = batch_api.process("dpp_pdf",batch_name=batch_name,subject_name=subject_name,chapter_name=chapter_name)
        return create_response(data=renamer(dpp_pdf,'topic','name'))
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



@scraper_blueprint.route('/api/private/<client_id>/test/<test_id>', methods=['GET'])
def get_private_test(client_id,test_id):
    try:
        debugger.success(f"test_id: {test_id}")
        debugger.success(f"batch_api.token: {batch_api.token}")
        debugger.success(f"batch_api.random_id: {batch_api.random_id}")
        #return create_response(data=batch_api.process("test",test_id=test_id))

        # --- Configuration ---
        IMAGES_PER_PAGE = 4

        client_id= generate_safe_file_name(client_id)

        CLIENT_DIR = os.path.join(glv_var.api_webdl_directory,client_id)

        WRONG_Q_DIR = os.path.join(str(CLIENT_DIR),"wrong_questions")
        UNATTEMPTED_Q_DIR = os.path.join(str(CLIENT_DIR),"unattempted_questions")

        os.makedirs(WRONG_Q_DIR, exist_ok=True)
        os.makedirs(UNATTEMPTED_Q_DIR, exist_ok=True)

        #test_id = args.test_id



        try:
            # --- 2. Fetch Data using the provided test_id ---
            print("Fetching test data...")
            test = batch_api.get_test(test_id).data
            questions = test.questions
            print(f"Found {len(questions)} total questions.")

            # --- 3. Prepare Info & Download ---
            wrong_q_info = []
            unattempted_q_info = []

            for i, q in enumerate(questions):
                option = q.yourResult.markedSolutions[0] if q.yourResult.markedSolutions else None
                actual_option = q.topperResult.markedSolutions[0] if q.topperResult.markedSolutions else None
                if option:
                    options = [op._id for op in q.question.options]
                    index = options.index(option)
                    option = q.question.options[index].texts.en if index < len(q.question.options) else None
                if actual_option:
                    options = [op._id for op in q.question.options]
                    index = options.index(actual_option)
                    actual_option = q.question.options[index].texts.en if index < len(q.question.options) else None

                info_dict = {
                    "link": q.question.imageIds.link,
                    "question_number": str(q.question.questionNumber),
                    "time_taken": getattr(q.yourResult, 'timeTaken', 'N/A'),
                    "subject": str(q.question.topicId.name),
                    "marked_solution":str(option if option else 'X'),
                    "actual_solution":str(actual_option if actual_option else 'X'),
                    # Prepend question number to filename for sorting
                    "filename": f"q{q.question.questionNumber:03d}_{q.question.imageIds.name}-{i}.png"
                }
                if q.yourResult.status == "WRONG":
                    wrong_q_info.append(info_dict)
                elif q.yourResult.status == "UnAttempted":
                    unattempted_q_info.append(info_dict)

            # Download Wrong questions
            print(f"\nDownloading {len(wrong_q_info)} WRONG questions...")
            for info in wrong_q_info:
                ScraperModule().download_file(
                    url=info['link'],
                    destination_folder=WRONG_Q_DIR,
                    filename=info['filename']
                )

            # Download Unattempted questions
            print(f"\nDownloading {len(unattempted_q_info)} UNATTEMPTED questions...")
            for info in unattempted_q_info:
                ScraperModule().download_file(
                    url=info['link'],
                    destination_folder=UNATTEMPTED_Q_DIR,
                    filename=info['filename']
                )

            print("\nAll downloads complete.")

            WRONG_PDF_NAME = f"{test.test.name}_WRONG.pdf"
            UNATTEMPTED_PDF_NAME = f"{test.test.name}_UNATTEMPTED.pdf"

            # --- 4. Create A4 PDFs ---
            create_a4_pdf_from_images(
                image_info=wrong_q_info,
                base_folder=WRONG_Q_DIR,
                output_filename=str(os.path.join(str(CLIENT_DIR), WRONG_PDF_NAME)),
                images_per_page=IMAGES_PER_PAGE
            )

            create_a4_pdf_from_images(
                image_info=unattempted_q_info,
                base_folder=UNATTEMPTED_Q_DIR,
                output_filename=str(os.path.join(str(CLIENT_DIR), UNATTEMPTED_PDF_NAME)),
                images_per_page=IMAGES_PER_PAGE
            )
            return create_response(data={
                "test":test.test.name,
                "client_id":client_id,
                "wrong_pdf_url":ENDPOINTS_NAME.GET_PVT_FILE_FOR_A_CLIENT(client_id=client_id,name=WRONG_PDF_NAME),
                "unattempted_pdf_url":ENDPOINTS_NAME.GET_PVT_FILE_FOR_A_CLIENT(client_id=client_id,name=UNATTEMPTED_PDF_NAME),

            })

        finally:
            # --- 5. Cleanup ---
            print("\n--- Cleaning up temporary files ---")
            for folder in [WRONG_Q_DIR, UNATTEMPTED_Q_DIR]:
                if os.path.exists(folder):
                    try:
                        shutil.rmtree(folder)
                        print(f"Removed temporary folder: '{folder}'")
                    except OSError as e:
                        print(f"Error removing folder {folder}: {e}")


    except Exception as e:
        debugger.error(f"Error: {e}")
        return create_response(error=str(e)), 500



@scraper_blueprint.route('/api/private/test_mappings_for_me', methods=['GET'])
def get_private_test_mappings_for_me():
    all_test = AllTestDetails.from_json(Endpoint(
        url="https://api.penpencil.co/v3/test-service/tests?testType=All&testStatus=All&attemptStatus=All&batchId=678b4cf5a3a368218a2b16e7&isSubjective=false&isPurchased=true&testCategoryIds=6814be5e9467bd0a54703a94",
        headers=ScraperModule.batch_api.DEFAULT_HEADERS
        ).fetch()[0])

    data = {}
    for test in all_test.data:
        data[test.name] = str(test.testStudentMappingId)

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
