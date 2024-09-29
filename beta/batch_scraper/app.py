import json

import requests
from beta.batch_scraper.Endpoints import Endpoints
from mainLogic.utils import glv_var
from mainLogic.utils.glv import Global


class BatchAPI:
    def __init__(self, batch_name: str, token: str, force=True):
        self.batch_name = batch_name
        self.token = token
        self.force = force

        print(f"token: {self.token}")

    def dataFromAPI(self, url: str, headers: dict = {}, params: dict = {}, data: dict = {}, method: str = 'GET',
                    post_modifier_function=None):

        if self.force:
            Global.errprint("Forced to get token from stored prefs")
            try:
                self.token = glv_var.vars['prefs'].get('token')
            except Exception as e:
                Global.errprint(f"Error: {e}")
                self.token = None
                raise ValueError("Token not found in prefs")

            Global.sprint(f"New Token: {self.token}")

        if self.token:
            if 'Authorization' not in headers:
                headers['Authorization'] = f'Bearer {self.token}'

        if method == 'GET':
            response = requests.get(url, headers=headers, params=params)
        elif method == 'POST':
            response = requests.post(url, headers=headers, params=params, data=data)
        elif method == 'PUT':
            response = requests.put(url, headers=headers, params=params, data=data)
        elif method == 'DELETE':
            response = requests.delete(url, headers=headers, params=params)
        else:
            raise ValueError('Method not recognized')

        Global.hr()
        print(f"Debugging at {url}")
        Global.sprint(f"Response: {response}")
        print(f"Response Status Code: {response.status_code}")
        print(f"Response Text: " + "\n"+f"{json.dumps(response.json())}")
        Global.hr()

        if callable(post_modifier_function):
            return post_modifier_function(response)
        return response.json() if response.status_code == 200 else response.text

    def get_paginated_data(self, url: str, headers: dict = {}, params: dict = {}, data: dict = {},
                           method: str = 'GET', post_modifier_function=None):
        all_data = []
        page = 1

        while True:
            paginated_url = url.format(page=page)
            #print(f"Fetching data from {paginated_url}")
            response = self.dataFromAPI(paginated_url, headers, params, data, method, post_modifier_function)
            if isinstance(response, str):
                break
            all_data.extend(response)
            #print(response)
            if not response:
                break
            page += 1

            # Break if the paginated URL is the same as the base URL
            if paginated_url == url:
                break

        return all_data

    def get_subject_details_khazana(self):
        def batch_details_to_subject_slugs(data):
            return [{
                'slug': subject['slug'],
                'name': subject['name'],
                # 'chapter_count': subject['tagCount'],
                # 'img': '' if 'imageId' not in subject else subject['imageId']['baseUrl'] + subject['imageId']['key']
            } for subject in data]

        return (
            batch_details_to_subject_slugs(
                self.get_paginated_data(
                    Endpoints.batch_details_khazana(batch_slug=self.batch_name),
                    post_modifier_function=lambda response: response.json()['data']
                )
            )
        )

    def get_batches_of_subject_khazana(self, kh_subject_slug):
        def get_chapter_slugs(data):
            return [{
                'name': f"{chapter['name']} {chapter['description'].split(';')[0]}",
                'slug': chapter['slug'],
                'topics': chapter['totalTopics'],
                'img': '' if 'imageId' not in chapter else (chapter['imageId']['baseUrl'] + chapter['imageId']['key'])
            } for chapter in data]

        return (
            get_chapter_slugs(
                self.get_paginated_data(
                    Endpoints.get_batches_of_subject_khazana(subject_slug=kh_subject_slug),
                    post_modifier_function=lambda response: response.json()['data']
                )
            )
        )

    def get_topics_of_subject_of_a_batch_khazana(self, subject_slug_kh):
        def get_chapter_slugs(data):
            return [{
                'name': chapter['name'],
                'slug': chapter['slug'],
                'id': chapter['_id'],
                'video_count': chapter['totalLectures'],
            } for chapter in data]

        return (
            get_chapter_slugs(
                self.get_paginated_data(
                    Endpoints.get_topics_of_subject_of_a_batch_khazana(subject_slug=subject_slug_kh),
                    post_modifier_function=lambda response: response.json()['data']
                )
            )
        )

    def get_lectures_of_topic_of_subject_of_a_batch_khazana(self, subject_slug_kh, chapter_slug_kh, topic_id):

        # get topic id first
        sub_topic_id = self.get_paginated_data(
            Endpoints.sub_topic_khazana(
                batch_slug=self.batch_name,
                subject_slug=subject_slug_kh,
                id=topic_id
            ),
            post_modifier_function=lambda response: response.json()['data']
        )[0]['_id']

        def get_video_slugs(data):
            return [{
                'name': video['title'],
                'url': video['content'][0]['videoUrl'],
                'img': video['content'][0]["videoDetails"]["image"],
            } for video in data]

        return (
            get_video_slugs(
                self.get_paginated_data(
                    Endpoints.get_lectures_of_topic_of_subject_of_a_batch_khazana(
                        batch_slug=self.batch_name,
                        subject_slug=subject_slug_kh,
                        chapter_slug=chapter_slug_kh,
                        topic_id=topic_id,
                        sub_topic_id=sub_topic_id,
                        page=1
                    ),
                    headers={
                        "randomId": "441c443a-2ab0-40da-86c1-885b88892094",
                        "Referer": "https://www.pw.live/",
                        "sec-ch-ua": '"Google Chrome";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
                        "sec-ch-ua-mobile": "?0",
                        "client-type": "WEB",
                        "client-id": "5eb393ee95fab7468a79d189",
                        "integration-with": "",
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
                        "Accept": "application/json, text/plain, */*",
                        "client-version": "6.0.6"
                    },
                    post_modifier_function=lambda response: response.json()['data']
                )
            )
        )

    def get_subjects_details(self):
        def batch_details_to_subject_slugs(data):
            print(f"Data: {json.dumps(data)}")
            return [{
                'slug': subject['slug'],
                'name': subject['subject'],
                'chapter_count': subject['tagCount'] if 'tagCount' in subject else 0,

            } for subject in data]

        return (
            batch_details_to_subject_slugs(
                self.dataFromAPI(
                    Endpoints.batch_details(batch_slug=self.batch_name),
                    post_modifier_function=lambda response: response.json()['data']['subjects']
                )
            )
        )

    def get_chapter_slugs(self, subject_slug):
        def get_chapter_slugs(data):
            return [{
                'name': chapter['name'],
                'slug': chapter['slug'],
                'video_count': chapter['videos'],
            } for chapter in data]

        Global.hr()
        print(f"Batch: {self.batch_name}")
        print(f"Subject: {subject_slug}")
        Global.hr()

        return (
            get_chapter_slugs(
                self.get_paginated_data(
                    Endpoints.get_topics_of_subject(batch_slug=self.batch_name,subject_slug=subject_slug),
                    post_modifier_function=lambda response: response.json()['data']
                )
            )
        )

    def get_video_data(self, subject_slug, chapter_slug):
        def get_video_slugs(data):
            return [{
                'name': video['topic'],
                'url': video['url'],
                'img': video['videoDetails']['image'],
            } for video in data]

        return (
            get_video_slugs(
                self.get_paginated_data(
                    Endpoints.get_videos_of_a_chapter(subject_slug=subject_slug, chapter_slug=chapter_slug),
                    post_modifier_function=lambda response: response.json()['data']
                )
            )
        )

# TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3Mjc4MjAxNDEuNTEsImRhdGEiOnsiX2lkIjoiNjI0Njc3MTBlYjAxMzcwMDE4YTMzMjM2IiwidXNlcm5hbWUiOiI2MjA3NDg2OTAzIiwiZmlyc3ROYW1lIjoiU2hhdXJ5YSBDaGFuZHJhIiwibGFzdE5hbWUiOiIiLCJvcmdhbml6YXRpb24iOnsiX2lkIjoiNWViMzkzZWU5NWZhYjc0NjhhNzlkMTg5Iiwid2Vic2l0ZSI6InBoeXNpY3N3YWxsYWguY29tIiwibmFtZSI6IlBoeXNpY3N3YWxsYWgifSwiZW1haWwiOiJzaGF1cnlhY2hhbmRyYXdvcmtAZ21haWwuY29tIiwicm9sZXMiOlsiNWIyN2JkOTY1ODQyZjk1MGE3NzhjNmVmIiwiNWNjOTVhMmU4YmRlNGQ2NmRlNDAwYjM3Il0sImNvdW50cnlHcm91cCI6IklOIiwidHlwZSI6IlVTRVIifSwiaWF0IjoxNzI3MjE1MzQxfQ.46-GMHHcv6Ps6GaQxQ7FtM-wY0rtGNIFRBZMt-Mh5Ok"
# batch = BatchAPI("12th-neet-khazana-370407", TOKEN)
#
# subjects = batch.get_subject_details_khazana()
# phy = subjects[0]['slug']
# batches_subject = batch.get_batches_of_subject_khazana(phy)
#
# alakh_sir_batch = batches_subject[0]['slug']
# print(alakh_sir_batch)
# topics = batch.get_topics_of_subject_of_a_batch_khazana(alakh_sir_batch)
# topic_0 = topics[0]
#
# lectures = batch.get_lectures_of_topic_of_subject_of_a_batch_khazana(
#     subject_slug_kh=phy,
#     chapter_slug_kh=alakh_sir_batch,
#     topic_id=topic_0['slug']
# )
# print(
#     f"Subject: {phy} "+
#     f"Chapter: {alakh_sir_batch} "+
#     f"Topic: {topic_0['slug']} "
# )
#lakshya-neet-2025-416888
# # all slugs
# print(phy)
#
#
# normal_batch = BatchAPI("", TOKEN)
# subjects = normal_batch.get_subjects_details()
# phy = subjects[0]['slug']
# chapters = normal_batch.get_chapter_slugs(phy)
# chapter_0 = chapters[0]
# videos = normal_batch.get_video_data(phy, chapter_0['slug'])
# print(videos)
#
