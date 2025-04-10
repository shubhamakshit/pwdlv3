import json
from tabnanny import verbose

from beta.question_scraper.Endpoints import Endpoints
from mainLogic.utils import glv_var
from mainLogic.utils.Endpoint import Endpoint
from mainLogic.utils.glv import Global
from mainLogic.utils.glv_var import debugger


class QuestionsAPI:

    def __init__(self, token: str,random_id:str, force=True, verbose=False):
        self.token = token
        self.random_id = random_id
        self.force = force
        self.verbose = verbose

    def dataFromAPI(self, endpoint: Endpoint):
        if self.force:
            debugger.error("Forced to get token from stored prefs")
            try:
                self.token = glv_var.vars['prefs']['token']
                self.random_id = glv_var.vars['prefs']['random_id']
            except Exception as e:
                debugger.error(f"Error: {e}")
                self.token = None
                raise ValueError("Token not found in prefs")
            debugger.success(f"New Token: {self.token}")

        if self.token and 'Authorization' not in endpoint.headers:
            endpoint.headers['Authorization'] = f'Bearer {self.token}'
        if self.random_id and 'random_id' not in endpoint.headers:
            # endpoint.headers['random_id'] = self.random_id
            endpoint.headers['randomid'] = self.random_id

        if self.verbose:
            debugger.success(f"Headers: {endpoint.headers}")
            debugger.success(f"Payload: {endpoint.payload}")


        response_obj, status_code, response = endpoint.fetch()

        if self.verbose:
            Global.hr()
            print(f"Debugging at {endpoint.url}")
            debugger.success(f"Response: {response}")
            print(f"Response Status Code: {status_code}")
            print(f"Response Text: \n{json.dumps(response_obj)}")
            Global.hr()

        if endpoint.post_function:
            return endpoint.post_function(response_obj)
        return response_obj if status_code == 200 else response.text

    def get_paginated_data(self, endpoint: Endpoint):
        all_data = []
        page = 1

        while True:
            paginated_endpoint = endpoint.__copy__()
            paginated_endpoint.url = paginated_endpoint.url.format(page=page)
            response = self.dataFromAPI(paginated_endpoint)

            if isinstance(response, str):
                break
            if not response:
                break

            all_data.extend(response)
            page += 1

            if paginated_endpoint.url == endpoint.url:
                break

        return all_data

    def GET_SUBJECTS(self):
        return self.dataFromAPI(Endpoints.GET_SUBJECTS_BATCH_EP())

    def GET_CHAPTERS(self, batch_id=None, subject_id=None):

        return self.dataFromAPI(Endpoints.GET_CHAPTERS_EP(subject_id=subject_id))

    def GET_QUESTION(self, subject_id=None, chapters=None, difficulty_level=None, questions_count=None):
        return self.dataFromAPI(Endpoints.GET_QUESTIONS_EP(subject_id=subject_id, chapters=chapters, difficulty_level=difficulty_level, questions_count=questions_count))
