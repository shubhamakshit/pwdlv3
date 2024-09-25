class Endpoints:

    @staticmethod
    def batch_details(batch_slug='lakshya-neet-2025-416888'):
        return f"https://api.penpencil.co/v3/batches/{batch_slug}/details"

    @staticmethod
    def get_topics_of_subject(batch_slug='lakshya-neet-2025-416888',subject_slug='physics-553715',page='{page}'):
        return f"https://api.penpencil.co/v2/batches/{batch_slug}/subject/{subject_slug}/topics?page={page}"

    @staticmethod
    def get_videos_of_a_chapter(batch_slug='lakshya-neet-2025-416888',subject_slug='physics-553715',chapter_slug='introduction-to-physics',page='{page}'):
        return f"https://api.penpencil.co/v2/batches/{batch_slug}/subject/{subject_slug}/contents?page={page}&contentType=videos&tag={chapter_slug}"

    @staticmethod
    def batch_details_khazana(batch_slug='12th-neet-khazana-370407',page='{page}'):
        return f"https://api.penpencil.co/v1/programs/{batch_slug}/subjects?page={page}"

    @staticmethod
    def get_batches_of_subject_khazana(batch_slug='12th-neet-khazana-370407',subject_slug='complete-12th-physics-by-964859',page='{page}'):
        return f"https://api.penpencil.co/v2/programs/{batch_slug}/subjects/{subject_slug}/chapters?page={page}"

    @staticmethod
    def get_topics_of_subject_of_a_batch_khazana(batch_slug='12th-neet-khazana-370407',subject_slug='complete-12th-physics-by-964859',page='{page}'):
        return f"https://api.penpencil.co/v1/programs/{batch_slug}/subjects/{subject_slug}/chapters/{subject_slug}/topics?page={page}"

    @staticmethod
    def sub_topic_khazana(
            batch_slug='12th-neet-khazana-370407',
            subject_slug='complete-12th-physics-by-964859',
            id="",
            page='{page}'
    ):
        return ("https://api.penpencil.co/v1/programs/"+
                f"{batch_slug}/subjects/{subject_slug}/chapters/{subject_slug}/topics/{id}/contents/sub-topic?page={page}")

    @staticmethod
    def get_lectures_of_topic_of_subject_of_a_batch_khazana(batch_slug='12th-neet-khazana-370407',subject_slug='complete-12th-physics-by-964859',chapter_slug='complete-12th-physics-by-964859',topic_id="", sub_topic_id="",page='{page}'):
        return f"https://api.penpencil.co/v2/programs/contents?type=&programId={batch_slug}&subjectId={subject_slug}&chapterId={chapter_slug}&topicId={topic_id}&page={page}&subTopicId={sub_topic_id}"
