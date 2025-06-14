from typing import Any, Dict, List, Optional, Union
from datetime import datetime

# Helper class for Attachment details
class AttachmentDetail:
    def __init__(self, _id: str, baseUrl: str, key: str, name: str):
        self.id = _id
        self.baseUrl = baseUrl
        self.key = key
        self.name = name
        # The 'link' property is derived from baseUrl and key
        self.link = f"{baseUrl}{key}" if baseUrl and key else None

    @staticmethod
    def from_json(json_data: Dict[str, Any]) -> 'AttachmentDetail':
        return AttachmentDetail(
            _id=json_data.get('_id'),
            baseUrl=json_data.get('baseUrl'),
            key=json_data.get('key'),
            name=json_data.get('name')
        )

# Helper class for Homework details
class HomeworkDetail:
    def __init__(self,
                 _id: str,
                 actions: List[Any] = None, # Assuming 'actions' is a list of unspecified type
                 attachmentIds: List[Dict[str, Any]] = None, # Raw dicts before conversion
                 batchSubjectId: Optional[str] = None,
                 note: Optional[str] = None,
                 solutionVideoId: Optional[str] = None,
                 solutionVideoType: Optional[str] = None,
                 solutionVideoUrl: Optional[str] = None,
                 topic: Optional[str] = None
                ):
        self.id = _id
        self.actions = actions if actions is not None else []
        
        # Process nested 'attachmentIds' array using AttachmentDetail model
        self.attachments: List[AttachmentDetail] = [
            AttachmentDetail.from_json(attachment)
            for attachment in (attachmentIds if attachmentIds is not None else [])
        ]

        self.batchSubjectId = batchSubjectId
        self.note = note
        self.solutionVideoId = solutionVideoId
        self.solutionVideoType = solutionVideoType
        self.solutionVideoUrl = solutionVideoUrl
        self.topic = topic

    @staticmethod
    def from_json(json_data: Dict[str, Any]) -> 'HomeworkDetail':
        return HomeworkDetail(
            _id=json_data.get('_id'),
            actions=json_data.get('actions', []),
            attachmentIds=json_data.get('attachmentIds', []), # Pass raw list for nested conversion
            batchSubjectId=json_data.get('batchSubjectId'),
            note=json_data.get('note'),
            solutionVideoId=json_data.get('solutionVideoId'),
            solutionVideoType=json_data.get('solutionVideoType'),
            solutionVideoUrl=json_data.get('solutionVideoUrl'),
            topic=json_data.get('topic')
        )

# Main BatchNotesDetail class
class BatchNotesDetail:
    def __init__(self,
                 _id: str,
                 dRoomId: Optional[str] = None,
                 date: Optional[str] = None,
                 homeworkIds: List[Dict[str, Any]] = None, # Raw list of dicts for homeworks
                 isBatchDoubtEnabled: Optional[bool] = None,
                 isDPPNotes: Optional[bool] = None,
                 isFree: Optional[bool] = None,
                 isSimulatedLecture: Optional[bool] = None,
                 startTime: Optional[str] = None,
                 status: Optional[str] = None
                ):
        self.id: str = _id
        self.dRoomId: Optional[str] = dRoomId
        # Convert date strings to datetime objects
        self.date: Optional[datetime] = datetime.fromisoformat(date.replace('Z', '+00:00')) if date else None
        
        # Process nested 'homeworkIds' array using HomeworkDetail model
        self.homeworks: List[HomeworkDetail] = [
            HomeworkDetail.from_json(homework)
            for homework in (homeworkIds if homeworkIds is not None else [])
        ]
        
        self.isBatchDoubtEnabled: Optional[bool] = isBatchDoubtEnabled
        self.isDPPNotes: Optional[bool] = isDPPNotes
        self.isFree: Optional[bool] = isFree
        self.isSimulatedLecture: Optional[bool] = isSimulatedLecture
        self.startTime: Optional[datetime] = datetime.fromisoformat(startTime.replace('Z', '+00:00')) if startTime else None
        self.status: Optional[str] = status

    @staticmethod
    def from_json(json_data: Dict[str, Any]) -> 'BatchNotesDetail':
        return BatchNotesDetail(
            _id=json_data.get('_id'),
            dRoomId=json_data.get('dRoomId'),
            date=json_data.get('date'),
            homeworkIds=json_data.get('homeworkIds', []), # Pass raw list for nested conversion
            isBatchDoubtEnabled=json_data.get('isBatchDoubtEnabled'),
            isDPPNotes=json_data.get('isDPPNotes'),
            isFree=json_data.get('isFree'),
            isSimulatedLecture=json_data.get('isSimulatedLecture'),
            startTime=json_data.get('startTime'),
            status=json_data.get('status')
        )