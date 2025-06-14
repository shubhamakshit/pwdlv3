# /home/user/pwdlv3/beta/batch_scraper_2/models/BatchChapterDetail.py

from typing import *  # <--- Add this line

class BatchChapterDetail:
    def __init__(self, _id: str, displayOrder: int, exercises: List[Any], lectureVideos: List[Any],
                 name: str, notes: List[Any], slug: str, type: str, typeId: str, videos: List[Any]):
        self.id = _id
        self.displayOrder = displayOrder
        self.exercises = exercises
        self.lectureVideos = lectureVideos
        self.name = name
        self.notes = notes
        self.slug = slug
        self.type = type
        self.typeId = typeId
        self.videos = videos

    @staticmethod
    def from_json(json_data: Dict[str, Any]): # You'll need to import Dict from typing as well if not already
        return BatchChapterDetail(
            _id=json_data.get('_id'),
            displayOrder=json_data.get('displayOrder'),
            exercises=json_data.get('exercises', []),
            lectureVideos=json_data.get('lectureVideos', []),
            name=json_data.get('name'),
            notes=json_data.get('notes', []),
            slug=json_data.get('slug'),
            type=json_data.get('type'),
            typeId=json_data.get('typeId'),
            videos=json_data.get('videos', [])
        )