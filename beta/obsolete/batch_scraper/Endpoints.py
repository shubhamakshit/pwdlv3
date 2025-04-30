from beta.util import extract_uuid, generate_safe_file_name
from mainLogic.utils.Endpoint import Endpoint
from mainLogic.utils.glv_var import debugger


class Endpoints:
    DEFAULT_HEADERS = {
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
    }

    @staticmethod
    def post_function_subjects_khazana(data):
        return [{
            'slug': subject['slug'],
            'name': subject['name']
        } for subject in data['data']] if isinstance(data, dict) and 'data' in data else []

    @staticmethod
    def post_function_batches_khazana(data):
        return [{
            'name': f"{chapter['name']} {chapter['description'].split(';')[0]}",
            'slug': chapter['slug'],
            'topics': chapter['totalTopics'],
            'img': '' if 'imageId' not in chapter else (chapter['imageId']['baseUrl'] + chapter['imageId']['key'])
        } for chapter in data['data']] if isinstance(data, dict) and 'data' in data else []

    @staticmethod
    def post_function_topics_khazana(data):
        return [{
            'name': chapter['name'],
            'slug': chapter['slug'],
            'id': chapter['_id'],
            'video_count': chapter['totalLectures']
        } for chapter in data['data']] if isinstance(data, dict) and 'data' in data else []

    @staticmethod
    def post_function_lectures_khazana(data):
        return [{
            'name': video['title'],
            'url': video['content'][0]['videoUrl'],
            'img': video['content'][0]["videoDetails"]["image"],
            'duration': video['content'][0]["videoDetails"]["duration"]
        } for video in data['data']] if isinstance(data, dict) and 'data' in data else []

    @staticmethod
    def post_function_subjects(data):
        return [{
            'slug': subject['slug'],
            'name': subject['subject'],
            'chapter_count': subject.get('tagCount', 0)
        } for subject in data['data']['subjects']] if isinstance(data, dict) and 'data' in data and 'subjects' in data['data'] else []

    @staticmethod
    def post_function_chapters(data):
        return [{
            'name': chapter['name'],
            'slug': chapter['slug'],
            'video_count': chapter['videos']
        } for chapter in data['data']] if isinstance(data, dict) and 'data' in data else []

    @staticmethod
    def post_function_videos(data):
        return [{
            'name': video['topic'],
            'url': video['url'],
            'img': video['videoDetails']['image'],
            'duration': video['videoDetails']['duration']
        } for video in data['data']] if isinstance(data, dict) and 'data' in data else []

    @staticmethod
    def post_function_videos_simple(data):

        try:
            return [{
                'name': generate_safe_file_name(video['topic']),
                'url': extract_uuid(video['url'])[0],
            } for video in data['data']] if isinstance(data, dict) and 'data' in data else []
        except Exception as e:
            debugger.error(f"Error in post_function_videos_simple: {e}")
            return []



    @staticmethod
    def post_function_batches(data):
        return [{
            'slug': batch['batchId']['slug'],
            'img': '' if 'previewImage' not in batch['batchId'] else (batch['batchId']['previewImage']['baseUrl'] + batch['batchId']['previewImage']['key'])
        } for batch in data['data']] if isinstance(data, dict) and 'data' in data else []

    @staticmethod
    def GET_KHAZANA_SUBJECTS_EP(batch_name):
        return Endpoint(
            url=f"https://api.penpencil.co/v1/programs/{batch_name}/subjects?page={{page}}",
            method='GET',
            headers=Endpoints.DEFAULT_HEADERS.copy(),
            post_function=Endpoints.post_function_subjects_khazana
        )

    @staticmethod
    def GET_KHAZANA_BATCHES_EP(batch_name, subject_slug):
        return Endpoint(
            url=f"https://api.penpencil.co/v2/programs/{batch_name}/subjects/{subject_slug}/chapters?page={{page}}",
            method='GET',
            headers=Endpoints.DEFAULT_HEADERS.copy(),
            post_function=Endpoints.post_function_batches_khazana
        )

    @staticmethod
    def GET_KHAZANA_CHAPTERS_EP(batch_name, subject_slug):
        return Endpoint(
            url=f"https://api.penpencil.co/v1/programs/{batch_name}/subjects/{subject_slug}/chapters/{subject_slug}/topics?page={{page}}",
            method='GET',
            headers=Endpoints.DEFAULT_HEADERS.copy(),
            post_function=Endpoints.post_function_topics_khazana
        )

    @staticmethod
    def get_sub_topic_khazana(batch_name, subject_slug, topic_id):
        return Endpoint(
            url=f"https://api.penpencil.co/v1/programs/{batch_name}/subjects/{subject_slug}/chapters/{subject_slug}/topics/{topic_id}/contents/sub-topic?page={{page}}",
            method='GET',
            headers=Endpoints.DEFAULT_HEADERS.copy()
        )

    @staticmethod
    def GET_KHAZANA_LECTURES_EP(batch_name, subject_slug, chapter_slug, topic_id, sub_topic_id):
        return Endpoint(
            url=f"https://api.penpencil.co/v2/programs/contents?type=&programId={batch_name}&subjectId={subject_slug}&chapterId={chapter_slug}&topicId={topic_id}&page={{page}}&subTopicId={sub_topic_id}",
            method='GET',
            headers=Endpoints.DEFAULT_HEADERS.copy(),
            post_function=Endpoints.post_function_lectures_khazana
        )

    @staticmethod
    def GET_NORMAL_SUBJECTS_EP(batch_name):
        return Endpoint(
            url=f"https://api.penpencil.co/v3/batches/{batch_name}/details",
            method='GET',
            headers=Endpoints.DEFAULT_HEADERS.copy(),
            post_function=Endpoints.post_function_subjects
        )

    @staticmethod
    def GET_NORMAL_CHAPTERS_EP(batch_name, subject_slug):
        return Endpoint(
            url=f"https://api.penpencil.co/v2/batches/{batch_name}/subject/{subject_slug}/topics?page={{page}}",
            method='GET',
            headers=Endpoints.DEFAULT_HEADERS.copy(),
            post_function=Endpoints.post_function_chapters
        )

    @staticmethod
    def GET_NORMAL_LECTURES_EP(batch_name, subject_slug, chapter_slug,simple=False):
        return Endpoint(
            url=f"https://api.penpencil.co/v2/batches/{batch_name}/subject/{subject_slug}/contents?page={{page}}&contentType=videos&tag={chapter_slug}",
            method='GET',
            headers=Endpoints.DEFAULT_HEADERS.copy(),
            post_function=Endpoints.post_function_videos if not simple else Endpoints.post_function_videos_simple
        )

    @staticmethod
    def get_batches_force_hard():
        return Endpoint(
            url="https://api.penpencil.co/v1/cohort/634fd2463ce3d7001c50798a/batches?page={page}&filter=true&tag=online&batchChildUrl=/batches-new/?tag=online&version=2",
            method='GET',
            headers=Endpoints.DEFAULT_HEADERS.copy(),
            post_function=Endpoints.post_function_batches
        )