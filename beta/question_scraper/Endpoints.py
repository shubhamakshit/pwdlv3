import json

from mainLogic.utils.Endpoint import Endpoint


class Endpoints:





    DEFAULT_HEADERS = {
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'en-US,en;q=0.9,la;q=0.8',
        'client-id': '5eb393ee95fab7468a79d189',
        'client-type': 'WEB',
        'client-version': '300',
        'content-type': 'application/json',
        'dnt': '1',
        'origin': 'https://pw-infinite-practise.pw.live',
        'priority': 'u=1, i',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',

    }


    @staticmethod
    def GET_QUESTIONS_EP(
            subject_id = '734chcfe1nhx5ay0lh0n5d4qj',
            chapters = [{'chapterId': 'dlfqana46gj8kjshdzwwlhb7p', 'classId': 'oyhh7ve8217so92jw81tefbyp'}],
            difficulty_level = [3],
            questions_count = 90,
    ):
        return Endpoint(
            url='https://api.penpencil.co/v3/test-service/65d75d320531c20018ade9bb/infinitePractice/v2/start-test',
            method='POST',
            payload=json.dumps({
                "exams": [
                    "7d5erv0sihqah96p8noqgbxkp"
                ],
                "examCategory": "vckzned6mqjlkub8wsfh605rp",
                "testMode": "PRACTICE",
                "questionsCount": questions_count,
                "chapters": chapters,
                "subject": subject_id,
                "difficultyLevel": [
                    3
                ],
                "isReattempt": False
            }),
            headers=Endpoints.DEFAULT_HEADERS,
            post_function=lambda data: data['data']
        )

    @staticmethod
    def GET_SUBJECTS_BATCH_EP(batch_id='65d75d320531c20018ade9bb'):
        return Endpoint(
            url=f'https://api.penpencil.co/v3/batches/{batch_id}/infinitePractice/subjects',
            method='GET',
            headers=Endpoints.DEFAULT_HEADERS,
            post_function=lambda data: data['data']
        )

    @staticmethod
    def GET_CHAPTERS_EP(batch_id='65d75d320531c20018ade9bb', subject_id='734chcfe1nhx5ay0lh0n5d4qj'):
        return Endpoint(
            url=f'https://api.penpencil.co/v3/batches/{batch_id}/infinitePractice/chapters?subjectId={subject_id}',
            method='GET',
            headers=Endpoints.DEFAULT_HEADERS,
            post_function=lambda data: data['data']
        )

