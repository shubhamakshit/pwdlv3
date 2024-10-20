import json
from mainLogic.utils.Endpoint import Endpoint
from mainLogic.utils import glv_var
from mainLogic.utils.glv import Global
from beta.batch_scraper.Endpoints import Endpoints

class BatchAPI:
    def __init__(self, batch_name: str, token: str, force=True):
        self.batch_name = batch_name
        self.token = token
        self.force = force


    def dataFromAPI(self, endpoint: Endpoint):
        if self.force:
            Global.errprint("Forced to get token from stored prefs")
            try:
                self.token = glv_var.vars['prefs']['token']
            except Exception as e:
                Global.errprint(f"Error: {e}")
                self.token = None
                raise ValueError("Token not found in prefs")
            Global.sprint(f"New Token: {self.token}")

        if self.token and 'Authorization' not in endpoint.headers:
            endpoint.headers['Authorization'] = f'Bearer {self.token}'

        response_obj, status_code, response = endpoint.fetch()

        Global.hr()
        print(f"Debugging at {endpoint.url}")
        Global.sprint(f"Response: {response}")
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

    def GET_KHAZANA_SUBJECTS(self):
        return self.get_paginated_data(Endpoints.GET_KHAZANA_SUBJECTS_EP(self.batch_name))

    def GET_KHAZANA_BATCHES(self, kh_subject_slug):
        return self.get_paginated_data(Endpoints.GET_KHAZANA_BATCHES_EP(self.batch_name, kh_subject_slug))

    def GET_KHAZANA_CHAPTERS(self, subject_slug_kh):
        return self.get_paginated_data(Endpoints.GET_KHAZANA_CHAPTERS_EP(self.batch_name, subject_slug_kh))

    def GET_KHAZANA_LECTURES(self, subject_slug_kh, chapter_slug_kh, topic_id):
        # First get sub_topic_id
        Global.hr()
        print(f"Fetching sub-topic for Batch: {self.batch_name}, Subject: {subject_slug_kh}, Topic: {topic_id}")
        sub_topic_response = self.dataFromAPI(
            Endpoints.get_sub_topic_khazana(self.batch_name, subject_slug_kh, topic_id)
        )

        if 'data' in sub_topic_response:
            sub_topic_response = sub_topic_response['data']
        else:
            # Error handling
            Global.errprint(f"No data found in response @ khazana lectures: {sub_topic_response}")
            return []


        sub_topic_id = sub_topic_response[0]['_id'] if sub_topic_response else None
        print(f"Sub-topic ID: {sub_topic_id}")



        if not sub_topic_id:
            Global.errprint("No sub-topic ID found")
            return []

        Global.hr()
        print(f"Fetching lectures for Sub-topic ID: {sub_topic_id}")
        return self.get_paginated_data(
            Endpoints.GET_KHAZANA_LECTURES_EP(self.batch_name, subject_slug_kh, chapter_slug_kh, topic_id, sub_topic_id)
        )

    def GET_NORMAL_SUBJECTS(self):
        return self.dataFromAPI(Endpoints.GET_NORMAL_SUBJECTS_EP(self.batch_name))

    def GET_NORMAL_CHAPTERS(self, subject_slug):
        Global.hr()
        print(f"Batch: {self.batch_name}")
        print(f"Subject: {subject_slug}")
        Global.hr()

        return self.get_paginated_data(
            Endpoints.GET_NORMAL_CHAPTERS_EP(self.batch_name, subject_slug)
        )

    def GET_NORMAL_LECTURES(self, subject_slug, chapter_slug):
        return self.get_paginated_data(
            Endpoints.GET_NORMAL_LECTURES_EP(self.batch_name, subject_slug, chapter_slug)
        )

    def get_batches_force_hard(self):
        return self.get_paginated_data(Endpoints.get_batches_force_hard())