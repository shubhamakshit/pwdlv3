import json


def chapters_endpoint(batch_id, subject_id, khazana=False, page=1):
    if not khazana:
        return f'https://api.penpencil.co/v2/batches/{batch_id}/subject/{subject_id}/topics?page={page}'
    else:
        return f'https://api.penpencil.co/v1/programs/62cd4128972ca20018b4c092/subjects/{batch_id}/chapters/{subject_id}/topics?page={page}'


def content_endpoint(batch_id, subject_id, chapter_id, khazana=False, page=1, content="videos"):
    if not khazana:
        return f'https://api.penpencil.co/v2/batches/{batch_id}/subject/{subject_id}/contents?page={page}&contentType={content}&tag={chapter_id}'
    else:
        return f'https://api.penpencil.co/v1/programs/62cd4128972ca20018b4c092/subjects/{batch_id}/chapters/{subject_id}/topics/{chapter_id}/contents/sub-topic?page={page}'



from mainLogic.utils.glv import Global


class Subject:

    def __init__(self, batch_id, subject_id, token, khazana):
        self.batch_id = batch_id
        self.subject_id = subject_id
        self.token = token
        self.khazana = khazana

        Global.sprint(chapters_endpoint(batch_id, subject_id, khazana))
        self.get_chapters(chapters_endpoint(batch_id, subject_id, khazana), khazana)

    def get_chapters(self, endpoint, khazana=False, verbose=True):
        import requests

        payload = {}
        headers = {
            'Authorization': f'Bearer {self.token}'
        }

        response = requests.request("GET", endpoint, headers=headers, data=payload)

        if verbose:
            Global.dprint(response.text)

        if response.status_code == 200:
            data = response.json()['data']


            for chapter in data:

                # if khazana:
                #
                #     chapter = chapter['chapter']

                Global.sprint(chapter['name'])
                Global.sprint(chapter['slug'])

                chapter_url = content_endpoint(self.batch_id, self.subject_id, chapter['slug'], self.khazana)
                Global.dprint(chapter_url)
                self.get_lectures(chapter_url, self.khazana, verbose)

    def get_lectures(self, endpoint, khazana,verbose=True):
        import requests

        payload = {}
        headers = {
            'Authorization': f'Bearer {self.token}'
        }

        response = requests.request("GET", endpoint, headers=headers, data=payload)

        #Global.dprint(response.text)

        if response.status_code == 200:
            data = response.json()
            print(json.dumps(data, indent=4))

            for lecture in data:
                if khazana:
                    if 'content' in lecture:
                        Global.sprint(lecture['content']['name'])
                        lecture = lecture['content']
                if 'videoDetails' in lecture:
                    name = lecture['videoDetails']['name']
                else:
                    name = lecture['name']
                Global.sprint("\t" + name)
