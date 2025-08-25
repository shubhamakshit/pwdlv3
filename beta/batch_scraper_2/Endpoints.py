from typing import Callable, List, Type, TypeVar, Dict, Any, Optional, Union, Generic

from beta.util import extract_uuid, generate_safe_file_name
from mainLogic.utils.Endpoint import Endpoint
from mainLogic.utils.glv_var import debugger

# Import all your models
from .models.BatchChapterDetail import BatchChapterDetail
from .models.BatchLectureDetail import BatchLectureDetail
from .models.BatchSubjectDetails import BatchSubjectDetails
from .models.BatchNotesDetail import BatchNotesDetail
from .models.DppNotesDetails import DppNotesDetails
from .models.TestDetails import TestDetails

# --- Placeholder for Khazana Models (You will define these later) ---
# from .models.KhazanaProgramDetail import KhazanaProgramDetail
# from .models.KhazanaSubjectDetail import KhazanaSubjectDetail
# from .models.KhazanaTopicDetail import KhazanaTopicDetail
# from .models.KhazanaSubTopicDetail import KhazanaSubTopicDetail
# from .models.KhazanaChapterContentDetail import KhazanaChapterContentDetail
# from .models.KhazanaLectureDetail import KhazanaLectureDetail


T = TypeVar('T') # T represents the specific model type when model_class is used

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

            def  url_test(self,test_id:str) -> str:
                return f"{self.base}/{self.v3}/test-service/tests/mapping/{test_id}/preview-test"

            def post_process(self, response: Dict[str, Any], keys_to_extract: List[str], model_class: Optional[Type[T]] = None) -> Union[List[T], T, Any]:
                try:
                    data = response
                    if self.outer.verbose:
                        debugger.debug(f"Processing response:")
                        debugger.info(data)
                        
                    for key in keys_to_extract:
                        if isinstance(data, dict) and key in data:
                            data = data[key]
                        else:
                            raise KeyError(f"Key '{key}' not found at level {key}")

                    if model_class:
                        if isinstance(data, list):
                            processed_data = [model_class.from_json(item) for item in data]
                            if self.outer.verbose:
                                debugger.success(f"Successfully extracted and modeled data using {model_class.__name__} (List)")
                            return processed_data
                        elif isinstance(data, dict):
                            processed_data = model_class.from_json(data)
                            if self.outer.verbose:
                                debugger.success(f"Successfully extracted and modeled data using {model_class.__name__} (Single Object)")
                            return processed_data
                        else:
                            if self.outer.verbose:
                                debugger.warning(f"Model class {model_class.__name__} provided, but data is neither dict nor list. Returning raw data.")
                            return data
                    else:
                        if self.outer.verbose:
                            debugger.success(f"Successfully extracted raw data using keys {keys_to_extract}")
                        return data
                except Exception as e:
                    debugger.error(f"Failed to extract or model data: {e}")
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

        class Lambert(Generic[T]):
            def __init__(self, url_func: Callable, post_process_args: List[str], required_args: List[str], model: Optional[Type[T]] = None, raw_return_type: Type = Dict[str, Any]):
                self.url_func = url_func
                self.post_process_args = post_process_args
                self.required_args = required_args
                self.model = model
                self.raw_return_type = raw_return_type

        # --- Batch API Logs ---
        self.data_logs = {
            "details": Lambert[BatchSubjectDetails](self.API.url_details, ["data", "subjects"], ["batch_name"], model=BatchSubjectDetails, raw_return_type=List[Dict[str, Any]]),
            "subject": Lambert[BatchSubjectDetails](self.API.url_subject, ["data"], ["batch_name", "subject_name"],model=BatchChapterDetail ,raw_return_type=List[Dict[str, Any]]),
            "chapter": Lambert[BatchChapterDetail](self.API.url_chapter, ["data"], ["batch_name", "subject_name", "chapter_name"], model=BatchLectureDetail, raw_return_type=List[Dict[str, Any]]),
            "notes"  : Lambert[BatchNotesDetail](self.API.url_notes, ["data"], ["batch_name", "subject_name", "chapter_name"], model=BatchNotesDetail, raw_return_type=List[Dict[str, Any]]),
            "lecture": Lambert[BatchLectureDetail](self.API.url_lecture, ["data"], ["batch_name","lecture_id"],model=BatchLectureDetail ,raw_return_type=Dict[str, Any]),
            "dpp_pdf": Lambert[DppNotesDetails](self.API.url_dpp_pdf, ["data"], ["batch_name", "subject_name", "chapter_name"],model=DppNotesDetails, raw_return_type=List[Dict[str, Any]]),
            "test" : Lambert[TestDetails](self.API.url_test,[],["test_id"],model=TestDetails,raw_return_type=Dict[str, Any])

        }

        # --- Khazana API Logs (add models as you define them) ---
        self.khazana_logs= {
            "details"  :   Lambert[Any](self.Khazana.url_details, ["data"], ["program_name"], raw_return_type=List[Dict[str, Any]]),
            "subject"  :   Lambert[Any](self.Khazana.url_subject, ["data"], ["program_name", "subject_name"], raw_return_type=List[Dict[str, Any]]),
            "topics"   :   Lambert[Any](self.Khazana.url_topics, ["data"], ["program_name", "subject_name", "teacher_name"], raw_return_type=List[Dict[str, Any]]),
            "sub_topic" :  Lambert[Any](self.Khazana.url_sub_topic, ["data"], ["program_name", "subject_name", "teacher_name", "topic_name"], raw_return_type=List[Dict[str, Any]]),
            "chapter"  :   Lambert[Any](self.Khazana.url_chapter, ["data"], ["program_name", "subject_name", "teacher_name", "topic_name","sub_topic_name"], raw_return_type=List[Dict[str, Any]]),
            "lecture"  :   Lambert[Any](self.Khazana.url_lecture, ["data"], ["program_name", "topic_name", "lecture_id", "lecture_url"], raw_return_type=Dict[str, Any]),
            # Example if you had a KhazanaSubjectDetail model:
            # "khazana_subject": Lambert[KhazanaSubjectDetail](self.Khazana.url_subject, ["data"], ["program_name", "subject_name"], model=KhazanaSubjectDetail, raw_return_type=List[Dict[str, Any]]),
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

    # --- Original `process` method (backward compatible) ---
    def process(self, type: str, khazana: bool = False, use_model: bool = False, **kwargs) -> Union[List[T], T, Any]:
        lambert_map = self.data_logs if not khazana else self.khazana_logs
        
        # We need to get the specific Lambert instance here to infer its T
        # However, Python's static type checker can't dynamically infer T based on 'type' string.
        # So, we'll keep the return type general but explain how a user would know.
        lambert: Lambert[Any] = lambert_map[type] 

        missing_args = [arg for arg in lambert.required_args if arg not in kwargs]
        if missing_args:
            raise ValueError(f"Missing required arguments for '{type}': {missing_args}")

        url = lambert.url_func(**kwargs)
        if self.verbose:
            debugger.debug(f"Fetching from URL: {url}")

        endpoint = Endpoint(url, headers=self.DEFAULT_HEADERS)
        fetched_response = endpoint.fetch()[0]
        
        model_to_use = lambert.model if use_model else None
        processed_data = self.API.post_process(fetched_response, lambert.post_process_args, model_to_use)
        
        return processed_data

    # --- New specific methods for Batch API ---

    def get_batch_details(self, batch_name: str) -> List[BatchSubjectDetails]:
        """
        Retrieves batch details, returning a list of BatchSubjectDetails objects.
        """
        # Note: 'details' Lambert config has ["data", "subjects"] which means it extracts
        # a list of subject dictionaries, which map to BatchSubjectDetails.
        return self.process(
            type="details",
            use_model=True,
            batch_name=batch_name
        ) # type: ignore # Mypy might complain here without explicit casting or a more complex return type in `process`

    def get_batch_subjects(self, batch_name: str, subject_name: str) -> List[BatchChapterDetail]:
        """
        Retrieves subjects for a batch, returning a list of BatchSubjectDetails objects.
        """
        return self.process(
            type="subject",
            use_model=True,
            batch_name=batch_name,
            subject_name=subject_name
        ) # type: ignore

    def get_batch_chapters(self, batch_name: str, subject_name: str, chapter_name: str) -> List[BatchLectureDetail]:
        """
        Retrieves chapters for a subject, returning a list of BatchChapterDetail objects.
        """
        return self.process(
            type="chapter",
            use_model=True,
            batch_name=batch_name,
            subject_name=subject_name,
            chapter_name=chapter_name
        ) # type: ignore

    def get_batch_notes(self, batch_name: str, subject_name: str, chapter_name: str) -> List[BatchNotesDetail]:
        """
        Retrieves notes for a chapter, returning a list of BatchNotesDetail objects.
        """
        return self.process(
            type="notes",
            use_model=True,
            batch_name=batch_name,
            subject_name=subject_name,
            chapter_name=chapter_name
        ) # type: ignore

    def get_batch_lectures(self, lecture_id: str, batch_name: str) -> BatchLectureDetail:
        """
        Retrieves lecture details, returning a single BatchLectureDetail object.
        """
        return self.process(
            type="lecture",
            use_model=True,
            batch_name=batch_name,
            lecture_id=lecture_id
        ) # type: ignore

    def get_batch_dpp_notes(self, batch_name: str, subject_name: str, chapter_name: str) -> List[DppNotesDetails]:
        """
        Retrieves DPP notes, returning a list of DppNotesDetails objects.
        """
        return self.process(
            type="dpp_pdf",
            use_model=True,
            batch_name=batch_name,
            subject_name=subject_name,
            chapter_name=chapter_name
        ) # type: ignore

    def get_test(self,test_id:str) -> TestDetails:
        return self.process(
            type="test",
            use_model=True,
            test_id=test_id
        )
    # --- New specific methods for Khazana API (placeholders for your future models) ---

    # Example: If you create a KhazanaProgramDetail model
    # def get_khazana_program_details(self, program_name: str) -> KhazanaProgramDetail:
    #     """
    #     Retrieves Khazana program details, returning a KhazanaProgramDetail object.
    #     """
    #     return self.process(
    #         type="details", # Assuming 'details' in khazana_logs points to program details
    #         khazana=True,
    #         use_model=True,
    #         program_name=program_name
    #     ) # type: ignore

    # Example: If you create a KhazanaSubjectDetail model
    # def get_khazana_subjects(self, program_name: str, subject_name: str) -> List[KhazanaSubjectDetail]:
    #     """
    #     Retrieves Khazana subjects, returning a list of KhazanaSubjectDetail objects.
    #     """
    #     return self.process(
    #         type="subject", # Assuming 'subject' in khazana_logs points to subject list
    #         khazana=True,
    #         use_model=True,
    #         program_name=program_name,
    #         subject_name=subject_name
    #     ) # type: ignore

    # ... and so on for other Khazana endpoints