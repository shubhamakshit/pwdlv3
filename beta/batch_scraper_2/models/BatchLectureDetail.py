from typing import Any, Dict, List, Optional
from datetime import datetime

# Helper class for video details
class VideoDetail:
    def __init__(self, _id: str, createdAt: str, description: str, drmProtected: bool,
                 duration: int, findKey: str, image: str, name: str,
                 status: str, types: List[str], videoUrl: str):
        self.id = _id
        # Safely convert creation date to datetime object
        self.createdAt = datetime.fromisoformat(createdAt.replace('Z', '+00:00')) if createdAt else None
        self.description = description
        self.drmProtected = drmProtected
        self.duration = duration
        self.findKey = findKey
        self.image = image
        self.name = name
        self.status = status
        self.types = types
        self.videoUrl = videoUrl

    @staticmethod
    def from_json(json_data: Dict[str, Any]) -> 'VideoDetail':
        return VideoDetail(
            _id=json_data.get('_id'),
            createdAt=json_data.get('createdAt'),
            description=json_data.get('description'),
            drmProtected=json_data.get('drmProtected'),
            duration=json_data.get('duration'),
            findKey=json_data.get('findKey'),
            image=json_data.get('image'),
            name=json_data.get('name'),
            status=json_data.get('status'),
            types=json_data.get('types', []),
            videoUrl=json_data.get('videoUrl')
        )

# Helper class for tag details
class TagDetail:
    def __init__(self, _id: str, name: str):
        self.id = _id
        self.name = name

    @staticmethod
    def from_json(json_data: Dict[str, Any]) -> 'TagDetail':
        return TagDetail(
            _id=json_data.get('_id'),
            name=json_data.get('name')
        )

# Main BatchLectureDetail class
class BatchLectureDetail:
    def __init__(self,
                 _id: str,
                 conversationId: Optional[str] = None,
                 dRoomId: Optional[str] = None,
                 date: Optional[str] = None,
                 endTime: Optional[str] = None,
                 hasAttachment: Optional[bool] = None,
                 isBatchDoubtEnabled: Optional[bool] = None,
                 isChatEnabled: Optional[bool] = None,
                 isCommentDisabled: Optional[bool] = None,
                 isDPPNotes: Optional[bool] = None,
                 isDPPVideos: Optional[bool] = None,
                 isDoubtEnabled: Optional[bool] = None,
                 isFree: Optional[bool] = None,
                 isLocked: Optional[bool] = None,
                 isPathshala: Optional[bool] = None,
                 isSimulatedLecture: Optional[bool] = None,
                 isVideoLecture: Optional[bool] = None,
                 lectureType: Optional[str] = None,
                 name: Optional[str] = None,
                 restrictedSchedule: Optional[str] = None,
                 restrictedTime: Optional[str] = None,
                 roomId: Optional[str] = None,
                 startTime: Optional[str] = None,
                 status: Optional[str] = None,
                 tags: List[Dict[str, Any]] = None,
                 teachers: List[Any] = None,
                 timeline: List[Any] = None,
                 url: Optional[str] = None,
                 urlType: Optional[str] = None,
                 videoDetails: Optional[Dict[str, Any]] = None,
                 whiteboardType: Optional[str] = None,
                 ytStreamKey: Optional[str] = None,
                 ytStreamUrl: Optional[str] = None
                ):
        self.id: str = _id
        self.conversationId: Optional[str] = conversationId
        self.dRoomId: Optional[str] = dRoomId
        # Convert date strings to datetime objects
        self.date: Optional[datetime] = datetime.fromisoformat(date.replace('Z', '+00:00')) if date else None
        self.endTime: Optional[datetime] = datetime.fromisoformat(endTime.replace('Z', '+00:00')) if endTime else None
        self.hasAttachment: Optional[bool] = hasAttachment
        self.isBatchDoubtEnabled: Optional[bool] = isBatchDoubtEnabled
        self.isChatEnabled: Optional[bool] = isChatEnabled
        self.isCommentDisabled: Optional[bool] = isCommentDisabled
        self.isDPPNotes: Optional[bool] = isDPPNotes
        self.isDPPVideos: Optional[bool] = isDPPVideos
        self.isDoubtEnabled: Optional[bool] = isDoubtEnabled
        self.isFree: Optional[bool] = isFree
        self.isLocked: Optional[bool] = isLocked
        self.isPathshala: Optional[bool] = isPathshala
        self.isSimulatedLecture: Optional[bool] = isSimulatedLecture
        self.isVideoLecture: Optional[bool] = isVideoLecture
        self.lectureType: Optional[str] = lectureType
        self.name: Optional[str] = name
        self.restrictedSchedule: Optional[str] = restrictedSchedule
        self.restrictedTime: Optional[str] = restrictedTime
        self.roomId: Optional[str] = roomId
        self.startTime: Optional[datetime] = datetime.fromisoformat(startTime.replace('Z', '+00:00')) if startTime else None
        self.status: Optional[str] = status

        # Process nested 'tags' array using TagDetail model
        self.tags: List[TagDetail] = [TagDetail.from_json(tag) for tag in (tags if tags is not None else [])]

        self.teachers: List[Any] = teachers if teachers is not None else []
        self.timeline: List[Any] = timeline if timeline is not None else []

        self.url: Optional[str] = url
        self.urlType: Optional[str] = urlType

        # Process nested 'videoDetails' object using VideoDetail model
        self.videoDetails: Optional[VideoDetail] = VideoDetail.from_json(videoDetails) if videoDetails else None

        self.whiteboardType: Optional[str] = whiteboardType
        self.ytStreamKey: Optional[str] = ytStreamKey
        self.ytStreamUrl: Optional[str] = ytStreamUrl

    @staticmethod
    def from_json(json_data: Dict[str, Any]) -> 'BatchLectureDetail':
        return BatchLectureDetail(
            _id=json_data.get('_id'),
            conversationId=json_data.get('conversationId'),
            dRoomId=json_data.get('dRoomId'),
            date=json_data.get('date'),
            endTime=json_data.get('endTime'),
            hasAttachment=json_data.get('hasAttachment'),
            isBatchDoubtEnabled=json_data.get('isBatchDoubtEnabled'),
            isChatEnabled=json_data.get('isChatEnabled'),
            isCommentDisabled=json_data.get('isCommentDisabled'),
            isDPPNotes=json_data.get('isDPPNotes'),
            isDPPVideos=json_data.get('isDPPVideos'),
            isDoubtEnabled=json_data.get('isDoubtEnabled'),
            isFree=json_data.get('isFree'),
            isLocked=json_data.get('isLocked'),
            isPathshala=json_data.get('isPathshala'),
            isSimulatedLecture=json_data.get('isSimulatedLecture'),
            isVideoLecture=json_data.get('isVideoLecture'),
            lectureType=json_data.get('lectureType'),
            name=json_data.get('name'),
            restrictedSchedule=json_data.get('restrictedSchedule'),
            restrictedTime=json_data.get('restrictedTime'),
            roomId=json_data.get('roomId'),
            startTime=json_data.get('startTime'),
            status=json_data.get('status'),
            tags=json_data.get('tags', []),
            teachers=json_data.get('teachers', []),
            timeline=json_data.get('timeline', []),
            url=json_data.get('url'),
            urlType=json_data.get('urlType'),
            videoDetails=json_data.get('videoDetails'),
            whiteboardType=json_data.get('whiteboardType'),
            ytStreamKey=json_data.get('ytStreamKey'),
            ytStreamUrl=json_data.get('ytStreamUrl')
        )