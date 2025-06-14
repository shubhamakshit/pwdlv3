from typing import Callable, List, Type, TypeVar, Dict, Any, Optional, Union

from beta.util import extract_uuid, generate_safe_file_name
from mainLogic.utils.Endpoint import Endpoint
from mainLogic.utils.glv_var import debugger

# Import the BatchChapterDetail model from its dedicated file
# Ensure models/BatchChapterDetail.py has `from typing import List, Any, Dict`
from .models.BatchChapterDetail import BatchChapterDetail
from .models.BatchLectureDetail import BatchLectureDetail
from .models.BatchSubjectDetails import BatchSubjectDetails
from .models.BatchNotesDetail import BatchNotesDetail
from .models.DppNotesDetails import DppNotesDetails


T = TypeVar('T')

class Endpoints:
    def __init__(self, verbose=False):
        self.verbose = verbose
        self.DEFAULT_HEADERS = {
            'client-id': '5eb393ee95fab7468a79d189',
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

            def url_details(self, batch_name: str) -> str:
                return f"{self.base}/{self.v3}/batches/{batch_name}/details"

            def url_subject(self, batch_name: str, subject_name: str) -> str:
                return f"{self.base}/{self.v2}/batches/{batch_name}/subject/{subject_name}/topics?limit={self.hard_limit}"

            def url_chapter(self, batch_name: str, subject_name: str, chapter_name: str) -> str:
                return f"{self.base}/{self.v2}/batches/{batch_name}/subject/{subject_name}/contents?limit={self.hard_limit}&contentType=videos&tag={chapter_name}"

            def url_notes(self, batch_name: str, subject_name: str, chapter_name: str) -> str:
                return f"{self.base}/{self.v2}/batches/{batch_name}/subject/{subject_name}/contents?limit={self.hard_limit}&contentType=notes&tag={chapter_name}"

            def url_lecture(self, lecture_id: str, batch_name: str) -> str:
                return f"https://api.penpencil.co/{self.v1}/videos/video-url-details?type=BATCHES&childId={lecture_id}&parentId={batch_name}&reqType=query&videoContainerType=DASH"

            def url_dpp_pdf(self, batch_name: str, subject_name: str, chapter_name: str) -> str:
                return f"{self.base}/{self.v2}/batches/{batch_name}/subject/{subject_name}/contents?page=1&contentType=DppNotes&tag={chapter_name}&limit={self.hard_limit}"

            def post_process(self, response: Dict[str, Any], keys_to_extract: List[str], model_class: Optional[Type[T]] = None) -> Union[List[T], Any]:
                try:
                    data = response
                    debugger.debug(f"Processing response:")
                    debugger.info(data)
                    for key in keys_to_extract:
                        if isinstance(data, dict) and key in data:
                            data = data[key]
                        else:
                            raise KeyError(f"Key '{key}' not found at level {key}")

                    if model_class and isinstance(data, list):
                        processed_data = [model_class.from_json(item) for item in data]
                        if self.outer.verbose:
                            debugger.success(f"Successfully extracted and modeled data using {model_class.__name__}")
                        return processed_data
                    elif self.outer.verbose:
                        debugger.success(f"Successfully extracted data using keys {keys_to_extract}")
                    return data
                except Exception as e:
                    debugger.error(f"Failed to extract data: {e}")
                    # Return an empty list for consistency if data extraction fails and a list was expected
                    # or a meaningful default based on context. For now, matching original behavior.
                    return []

        class Khazana(API):
            def __init__(self, outer):
                super().__init__(outer)

            def url_details(self, program_name: str) -> str:
                return f"{self.base}/{self.v1}/programs/{program_name}/subjects?page=1&limit={self.hard_limit}"

            def url_subject(self, program_name: str, subject_name: str) -> str:
                return f"{self.base}/{self.v2}/programs/{program_name}/subjects/{subject_name}/chapters?page=1&limit={self.hard_limit}"

            def url_topics(self, program_name: str, subject_name: str, teacher_name: str) -> str:
                return f"{self.base}/{self.v1}/programs/{program_name}/subjects/{subject_name}/chapters/{teacher_name}/topics?page=1&limit={self.hard_limit}"

            def url_sub_topic(self, program_name: str, subject_name: str, teacher_name: str, topic_name: str) -> str:
                return f"{self.base}/{self.v1}/programs/{program_name}/subjects/{subject_name}/chapters/{teacher_name}/topics/{topic_name}/contents/sub-topic?page=1&limit={self.hard_limit}"

            def url_chapter(self, program_name: str, subject_name: str, teacher_name: str, topic_name: str, sub_topic_name: str) -> str:
                return f"{self.base}/{self.v2}/programs/contents?programId={program_name}&subjectId={subject_name}&chapterId={teacher_name}&topicId={topic_name}&subTopicId={sub_topic_name}&page=1&limit={self.hard_limit}"

            def url_lecture(self, program_name: str, topic_name: str, lecture_id: str, lecture_url: str) -> str:
                return (f"{self.base}/{self.v1}/videos/video-url-details?type=RECORDED&videoContainerType=DASH&reqType"
                        f"=query&childId={lecture_id}&parentId={program_name}&"
                        f"videoUrl={lecture_url}&secondaryParentId={topic_name}")


        self.API = API(self)
        self.Khazana = Khazana(self)

        class Lambert:
            # Added a new attribute to store the "raw" return type for clarity
            def __init__(self, url_func: Callable, post_process_args: List[str], required_args: List[str], model: Optional[Type[T]] = None, raw_return_type: Type = Dict[str, Any]):
                self.url_func = url_func
                self.post_process_args = post_process_args
                self.required_args = required_args
                self.model = model
                # Store the expected return type if 'use_model=False'
                self.raw_return_type = raw_return_type

        self.data_logs = {
            # Expected return if use_model=False: List[Dict[str, Any]]
            "details": Lambert(self.API.url_details, ["data", "subjects"], ["batch_name"], raw_return_type=List[Dict[str, Any]]),
            # Expected return if use_model=False: List[Dict[str, Any]]
            "subject": Lambert(self.API.url_subject, ["data"], ["batch_name", "subject_name"],model=BatchSubjectDetails ,raw_return_type=List[Dict[str, Any]]),
            # If use_model=True: List[BatchChapterDetail]
            # If use_model=False: List[Dict[str, Any]]
            "chapter": Lambert(self.API.url_chapter, ["data"], ["batch_name", "subject_name", "chapter_name"], model=BatchChapterDetail, raw_return_type=List[Dict[str, Any]]),
            # If use_model=True: List[BatchChapterDetail]
            # If use_model=False: List[Dict[str, Any]]
            "notes"  : Lambert(self.API.url_notes, ["data"], ["batch_name", "subject_name", "chapter_name"], model=BatchNotesDetail, raw_return_type=List[Dict[str, Any]]),
            # Expected return if use_model=False: Dict[str, Any] (or specific video details dict)
            "lecture": Lambert(self.API.url_lecture, ["data"], ["batch_name","lecture_id"],model=BatchLectureDetail ,raw_return_type=Dict[str, Any]),
            # Expected return if use_model=False: List[Dict[str, Any]]
            "dpp_pdf": Lambert(self.API.url_dpp_pdf, ["data"], ["batch_name", "subject_name", "chapter_name"],model=DppNotesDetails, raw_return_type=List[Dict[str, Any]]),
        }

        self.khazana_logs= {
            # Expected return if use_model=False: List[Dict[str, Any]]
            "details"  :   Lambert(self.Khazana.url_details, ["data"], ["program_name"], raw_return_type=List[Dict[str, Any]]),
            # Expected return if use_model=False: List[Dict[str, Any]]
            "subject"  :   Lambert(self.Khazana.url_subject, ["data"], ["program_name", "subject_name"], raw_return_type=List[Dict[str, Any]]),
            # Expected return if use_model=False: List[Dict[str, Any]]
            "topics"   :   Lambert(self.Khazana.url_topics, ["data"], ["program_name", "subject_name", "teacher_name"], raw_return_type=List[Dict[str, Any]]),
            # Expected return if use_model=False: List[Dict[str, Any]]
            "sub_topic" :  Lambert(self.Khazana.url_sub_topic, ["data"], ["program_name", "subject_name", "teacher_name", "topic_name"], raw_return_type=List[Dict[str, Any]]),
            # Expected return if use_model=False: List[Dict[str, Any]]
            "chapter"  :   Lambert(self.Khazana.url_chapter, ["data"], ["program_name", "subject_name", "teacher_name", "topic_name","sub_topic_name"], raw_return_type=List[Dict[str, Any]]),
            # Expected return if use_model=False: Dict[str, Any] (or specific video details dict)
            "lecture"  :   Lambert(self.Khazana.url_lecture, ["data"], ["program_name", "topic_name", "lecture_id", "lecture_url"], raw_return_type=Dict[str, Any]),
            # Add models to Khazana logs here if applicable in the future, and update raw_return_type
        }


    def set_token(self, token: str, random_id: str = "a3e290fa-ea36-4012-9124-8908794c33aa") -> 'Endpoints':
        self.token = token
        self.DEFAULT_HEADERS.setdefault('Authorization', 'Bearer ' + self.token)
        if random_id:
            self.random_id = random_id
            self.DEFAULT_HEADERS['randomid'] = self.random_id
        if self.verbose:
            debugger.debug("Authorization token set successfully.")
        return self

    # Return type uses TypeVar T to represent the specific model type when use_model=True,
    # or Any (which can be a Dict, List[Dict], etc.) when use_model=False.
    def process(self, type: str, khazana: bool = False, use_model: bool = False, **kwargs) -> Union[List[T], Dict[str, Any], Any]:
        lambert = self.data_logs[type] if not khazana else self.khazana_logs[type]

        missing_args = [arg for arg in lambert.required_args if arg not in kwargs]
        if missing_args:
            raise ValueError(f"Missing required arguments for '{type}': {missing_args}")

        url = lambert.url_func(**kwargs)
        if self.verbose:
            debugger.debug(f"Fetching from URL: {url}")

        endpoint = Endpoint(url, headers=self.DEFAULT_HEADERS)
        fetched_response = endpoint.fetch()[0]
        
        # Conditionally pass the model based on use_model parameter
        model_to_use = lambert.model if use_model else None
        processed_data = self.API.post_process(fetched_response, lambert.post_process_args, model_to_use)
        
        # While the post_process returns Union[List[T], Any], the process method
        # can narrow it down based on 'use_model' and 'lambert.model'.
        # However, for the main 'process' method's signature, Union[List[T], Any]
        # is the most accurate general representation.
        return processed_data