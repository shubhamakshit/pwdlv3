from typing import Any, Dict, List, Optional
from datetime import datetime

# Helper class for Image details
class ImageDetail:
    def __init__(self, _id: str, baseUrl: str, key: str, name: str):
        self.id = _id
        self.baseUrl = baseUrl
        self.key = key
        self.name = name

    @staticmethod
    def from_json(json_data: Dict[str, Any]) -> 'ImageDetail':
        return ImageDetail(
            _id=json_data.get('_id'),
            baseUrl=json_data.get('baseUrl'),
            key=json_data.get('key'),
            name=json_data.get('name')
        )

# Helper class for Schedule details
class ScheduleDetail:
    def __init__(self, _id: str, day: str, endTime: str, startTime: str):
        self.id = _id
        self.day = day
        # Convert date/time strings to datetime objects
        # Assuming ISO format, adjust if different (e.g., just time)
        self.endTime = datetime.fromisoformat(endTime.replace('Z', '+00:00')) if endTime else None
        self.startTime = datetime.fromisoformat(startTime.replace('Z', '+00:00')) if startTime else None

    @staticmethod
    def from_json(json_data: Dict[str, Any]) -> 'ScheduleDetail':
        return ScheduleDetail(
            _id=json_data.get('_id'),
            day=json_data.get('day'),
            endTime=json_data.get('endTime'),
            startTime=json_data.get('startTime')
        )

# Main BatchSubjectDetails class
class BatchSubjectDetails:
    def __init__(self,
                 _id: str,
                 batchId: Optional[str] = None,
                 displayOrder: Optional[int] = None,
                 fileId: Optional[str] = None,
                 imageId: Optional[Dict[str, Any]] = None, # Raw dict for image before conversion
                 lectureCount: Optional[int] = None,
                 name: Optional[str] = None,
                 qbgSubjectId: Optional[str] = None,
                 schedules: List[Dict[str, Any]] = None, # Raw list of dicts for schedules
                 slug: Optional[str] = None,
                 subjectId: Optional[str] = None,
                 substituteTeacherIds: List[str] = None,
                 tagCount: Optional[int] = None,
                 teacherIds: List[str] = None
                ):
        self.id: str = _id
        self.batchId: Optional[str] = batchId
        self.displayOrder: Optional[int] = displayOrder
        self.fileId: Optional[str] = fileId

        # Process nested 'imageId' object using ImageDetail model
        self.image: Optional[ImageDetail] = ImageDetail.from_json(imageId) if imageId else None

        self.lectureCount: Optional[int] = lectureCount
        self.name: Optional[str] = name
        self.qbgSubjectId: Optional[str] = qbgSubjectId

        # Process nested 'schedules' array using ScheduleDetail model
        self.schedules: List[ScheduleDetail] = [ScheduleDetail.from_json(s) for s in (schedules if schedules is not None else [])]

        self.slug: Optional[str] = slug
        self.subjectId: Optional[str] = subjectId
        self.substituteTeacherIds: List[str] = substituteTeacherIds if substituteTeacherIds is not None else []
        self.tagCount: Optional[int] = tagCount
        self.teacherIds: List[str] = teacherIds if teacherIds is not None else []

    @staticmethod
    def from_json(json_data: Dict[str, Any]) -> 'BatchSubjectDetails':
        return BatchSubjectDetails(
            _id=json_data.get('_id'),
            batchId=json_data.get('batchId'),
            displayOrder=json_data.get('displayOrder'),
            fileId=json_data.get('fileId'),
            imageId=json_data.get('imageId'), # Pass raw dict for nested conversion
            lectureCount=json_data.get('lectureCount'),
            name=json_data.get('name'),
            qbgSubjectId=json_data.get('qbgSubjectId'),
            schedules=json_data.get('schedules', []), # Pass raw list for nested conversion
            slug=json_data.get('slug'),
            subjectId=json_data.get('subjectId'),
            substituteTeacherIds=json_data.get('substituteTeacherIds', []),
            tagCount=json_data.get('tagCount'),
            teacherIds=json_data.get('teacherIds', [])
        )