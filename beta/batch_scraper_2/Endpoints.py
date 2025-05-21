from typing import Callable, List

from beta.util import extract_uuid, generate_safe_file_name
from mainLogic.utils.Endpoint import Endpoint
from mainLogic.utils.glv_var import debugger


class Endpoints:
    def __init__(self, verbose=False):
        self.verbose = verbose
        self.DEFAULT_HEADERS = {
            'client-id': '5eb393ee95fab7468a79d189',
            # 'randomid': 'dbacc4f3-9024-491d-b2d3-72bd4b6ee281',
            'client-type': 'WEB',
        }
        self.token = None
        self.random_id = None

        class API:
            def __init__(self, outer):
                self.outer = outer
                self.base = "https://api.penpencil.co"
                self.v1 = "v1"
                self.v2 = "v2"
                self.v3 = "v3"
                self.hard_limit = 50

            def url_details(self, batch_name):
                return f"{self.base}/{self.v3}/batches/{batch_name}/details"

            def url_subject(self, batch_name, subject_name):
                return f"{self.base}/{self.v2}/batches/{batch_name}/subject/{subject_name}/topics?limit={self.hard_limit}"

            def url_chapter(self, batch_name, subject_name, chapter_name):
                return f"{self.base}/{self.v2}/batches/{batch_name}/subject/{subject_name}/contents?limit={self.hard_limit}&contentType=videos&tag={chapter_name}"

            def url_notes(self, batch_name, subject_name, chapter_name):
                return f"{self.base}/{self.v2}/batches/{batch_name}/subject/{subject_name}/contents?limit={self.hard_limit}&contentType=notes&tag={chapter_name}"

            def url_lecture(self, lecture_id, batch_name):
                return f"https://api.penpencil.co/{self.v1}/videos/video-url-details?type=BATCHES&childId={lecture_id}&parentId={batch_name}&reqType=query&videoContainerType=DASH"

            def url_dpp_pdf(self, batch_name, subject_name, chapter_name):
                return f"{self.base}/{self.v2}/batches/{batch_name}/subject/{subject_name}/contents?page=1&contentType=DppNotes&tag={chapter_name}&limit={self.hard_limit}"

            def post_process(self, response: dict, keys_to_extract: List[str]):
                try:
                    data = response
                    debugger.debug(f"Processing response:")
                    debugger.info(data)
                    for key in keys_to_extract:
                        if isinstance(data, dict) and key in data:
                            data = data[key]
                        else:
                            raise KeyError(f"Key '{key}' not found at level {key}")
                    if self.outer.verbose:
                        debugger.success(f"Successfully extracted data using keys {keys_to_extract}")
                    return data
                except Exception as e:
                    debugger.error(f"Failed to extract data: {e}")
                    return []

        class Khazana(API):
            def __init__(self, outer):
                super().__init__(outer)

            def url_details(self, program_name):
                return f"{self.base}/{self.v1}/programs/{program_name}/subjects?page=1&limit={self.hard_limit}"

            def url_subject(self, program_name, subject_name):
                # even though 'chapters' is returend it actually returns 'teachers'
                return f"{self.base}/{self.v2}/programs/{program_name}/subjects/{subject_name}/chapters?page=1&limit={self.hard_limit}"

            def url_topics(self, program_name, subject_name, teacher_name):
                return f"{self.base}/{self.v1}/programs/{program_name}/subjects/{subject_name}/chapters/{teacher_name}/topics?page=1&limit={self.hard_limit}"

            def url_sub_topic(self, program_name, subject_name, teacher_name, topic_name):
                # actually returns 'chapters' by a specific teacher
                # topic name is actually chapyter name
                return f"{self.base}/{self.v1}/programs/{program_name}/subjects/{subject_name}/chapters/{teacher_name}/topics/{topic_name}/contents/sub-topic?page=1&limit={self.hard_limit}"

            def url_chapter(self,program_name,subject_name,teacher_name,topic_name,sub_topic_name):
                return f"{self.base}/{self.v2}/programs/contents?programId={program_name}&subjectId={subject_name}&chapterId={teacher_name}&topicId={topic_name}&subTopicId={sub_topic_name}&page=1&limit={self.hard_limit}"

            def url_lecture(self,program_name,topic_name,lecture_id,lecture_url):
                return (f"{self.base}/{self.v1}/videos/video-url-details?type=RECORDED&videoContainerType=DASH&reqType"
                        f"=query&childId={lecture_id}&parentId={program_name}&"
                        f"videoUrl={lecture_url}&secondaryParentId={topic_name}")


        self.API = API(self)
        self.Khazana = Khazana(self)

        class Lambert:
            def __init__(self, url_func: Callable, post_process_args: List[str], required_args: List[str]):
                self.url_func = url_func
                self.post_process_args = post_process_args
                self.required_args = required_args

        self.data_logs = {
            "details": Lambert(self.API.url_details, ["data", "subjects"], ["batch_name"]),
            "subject": Lambert(self.API.url_subject, ["data"], ["batch_name", "subject_name"]),
            "chapter": Lambert(self.API.url_chapter, ["data"], ["batch_name", "subject_name", "chapter_name"]),
            "notes"  : Lambert(self.API.url_notes, ["data",], ["batch_name", "subject_name", "chapter_name"]),
            "lecture": Lambert(self.API.url_lecture, ["data"], ["batch_name","lecture_id"]),
            "dpp_pdf": Lambert(self.API.url_dpp_pdf, ["data"], ["batch_name", "subject_name", "chapter_name"]),
        }

        self.khazana_logs= {
            "details"   :   Lambert(self.Khazana.url_details, ["data"], ["program_name"]),
            "subject"   :   Lambert(self.Khazana.url_subject, ["data"], ["program_name", "subject_name"]),
            "topics"    :   Lambert(self.Khazana.url_topics, ["data"], ["program_name", "subject_name", "teacher_name"]),
            "sub_topic" :   Lambert(self.Khazana.url_sub_topic, ["data"], ["program_name", "subject_name", "teacher_name", "topic_name"]),
            "chapter"   :   Lambert(self.Khazana.url_chapter, ["data"], ["program_name", "subject_name", "teacher_name", "topic_name","sub_topic_name"]),
            "lecture"   :   Lambert(self.Khazana.url_lecture, ["data"], ["program_name", "topic_name", "lecture_id", "lecture_url"]),


        }


    def set_token(self, token, random_id="a3e290fa-ea36-4012-9124-8908794c33aa"):
        self.token = token
        self.DEFAULT_HEADERS.setdefault('Authorization', 'Bearer ' + self.token)
        if random_id:
            self.random_id = random_id
            self.DEFAULT_HEADERS['randomid'] = self.random_id
        if self.verbose:
            debugger.debug("Authorization token set successfully.")
        return self



    def process(self, type: str,khazana=False, **kwargs):
        lambert = self.data_logs[type] if not khazana else self.khazana_logs[type]

        missing_args = [arg for arg in lambert.required_args if arg not in kwargs]
        if missing_args:
            raise ValueError(f"Missing required arguments for '{type}': {missing_args}")

        url = lambert.url_func(**kwargs)
        if self.verbose:
            debugger.debug(f"Fetching from URL: {url}")

        endpoint = Endpoint(url, headers=self.DEFAULT_HEADERS)
        fetched_response = endpoint.fetch()[0]
        processed_data = self.API.post_process(fetched_response, lambert.post_process_args)
        return processed_data



