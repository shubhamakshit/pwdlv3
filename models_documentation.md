# Models Documentation

This document provides a detailed overview of the data models used in the `batch_scraper_2` module. The models are used to structure the data received from the `api.penpencil.co` API endpoints.

---

## `BatchSubjectDetails`

Represents the details of a single subject available within a specific batch. This model is populated from the `/v3/batches/{batch_name}/details` endpoint.

- `id` (`str`): The unique identifier for the subject (e.g., `628b23f59332890011e682c4`).
- `batchId` (`Optional[str]`): The identifier of the batch this subject belongs to.
- `displayOrder` (`Optional[int]`): A number that determines the sorting order of the subject in a list.
- `fileId` (`Optional[str]`): An associated file identifier, if any.
- `image` (`Optional[ImageDetail]`): An object containing details about the subject's cover image.
- `lectureCount` (`Optional[int]`): The total number of lectures within this subject.
- `name` (`Optional[str]`): The display name of the subject (e.g., "Physics").
- `qbgSubjectId` (`Optional[str]`): The identifier for the subject in the question bank.
- `schedules` (`List[ScheduleDetail]`): A list of schedule objects defining when classes for this subject occur.
- `slug` (`Optional[str]`): A URL-friendly version of the subject name.
- `subjectId` (`Optional[str]`): Another identifier for the subject.
- `substituteTeacherIds` (`List[str]`): A list of IDs for substitute teachers.
- `tagCount` (`Optional[int]`): The number of tags associated with this subject.
- `teacherIds` (`List[str]`): A list of IDs for the primary teachers of this subject.

### Helper Class: `ImageDetail`
- `id` (`str`): The unique ID of the image record.
- `baseUrl` (`str`): The base URL for the image location (e.g., a CDN path).
- `key` (`str`): The specific path or key for the image file. The full URL is `baseUrl` + `key`.
- `name` (`str`): The filename of the image.

### Helper Class: `ScheduleDetail`
- `id` (`str`): The unique ID for the schedule entry.
- `day` (`str`): The day of the week for the class (e.g., "Monday").
- `endTime` (`Optional[datetime]`): The time the class ends.
- `startTime` (`Optional[datetime]`): The time the class starts.

---

## `BatchChapterDetail`

Represents a chapter or topic within a subject. This model is populated from the `/v2/batches/{batch_name}/subject/{subject_name}/topics` endpoint.

- `id` (`str`): The unique identifier for the chapter.
- `displayOrder` (`int`): The sorting order for the chapter.
- `exercises` (`List[Any]`): A list of exercises related to the chapter. The structure is currently not strictly typed.
- `lectureVideos` (`List[Any]`): A list of lecture videos for the chapter. The structure is currently not strictly typed.
- `name` (`str`): The name of the chapter (e.g., "Introduction to Kinematics").
- `notes` (`List[Any]`): A list of notes for the chapter. The structure is currently not strictly typed.
- `slug` (`str`): A URL-friendly version of the chapter name.
- `type` (`str`): The content type, typically "tag".
- `typeId` (`str`): The identifier for the content type.
- `videos` (`List[Any]`): A list of general videos for the chapter. The structure is currently not strictly typed.

---

## `BatchLectureDetail`

Represents a single lecture video's details. This model is populated from two main endpoints: a list from `/v2/batches/{batch_name}/subject/{subject_name}/contents?contentType=videos...` and a single object from `/v1/videos/video-url-details...`.

- `id` (`str`): The unique identifier for the lecture.
- `conversationId` (`Optional[str]`): Identifier for any associated conversation or chat.
- `dRoomId` (`Optional[str]`): Identifier for the discussion room.
- `date` (`Optional[datetime]`): The scheduled date of the lecture.
- `endTime` (`Optional[datetime]`): The scheduled end time of the lecture.
- `hasAttachment` (`Optional[bool]`): True if the lecture has associated attachments (like PDFs).
- `isBatchDoubtEnabled` (`Optional[bool]`): True if the doubt-solving feature is enabled.
- `isChatEnabled` (`Optional[bool]`): True if live chat is enabled.
- `isCommentDisabled` (`Optional[bool]`): True if comments are turned off.
- `isDPPNotes` (`Optional[bool]`): True if this lecture is associated with DPP notes.
- `isDPPVideos` (`Optional[bool]`): True if this lecture is associated with DPP videos.
- `isDoubtEnabled` (`Optional[bool]`): True if the doubt feature is enabled for this specific lecture.
- `isFree` (`Optional[bool]`): True if the lecture is available for free.
- `isLocked` (`Optional[bool]`): True if the lecture is locked and requires a subscription.
- `isPathshala` (`Optional[bool]`): True if it is a "Pathshala" type lecture.
- `isSimulatedLecture` (`Optional[bool]`): True if this is a simulated or recorded live lecture.
- `isVideoLecture` (`Optional[bool]`): True if the content is a video lecture.
- `lectureType` (`Optional[str]`): The type of lecture (e.g., "LIVE").
- `name` (`Optional[str]`): The title of the lecture.
- `restrictedSchedule` (`Optional[str]`): Information about restricted scheduling.
- `restrictedTime` (`Optional[str]`): Information about restricted viewing times.
- `roomId` (`Optional[str]`): The identifier for the live room.
- `startTime` (`Optional[datetime]`): The scheduled start time of the lecture.
- `status` (`Optional[str]`): The status of the lecture (e.g., "COMPLETED").
- `tags` (`List[TagDetail]`): A list of tags associated with the lecture.
- `teachers` (`List[Any]`): A list of teachers for the lecture.
- `timeline` (`List[Any]`): Timeline markers for the video.
- `url` (`Optional[str]`): The URL for the lecture content.
- `urlType` (`Optional[str]`): The type of the URL.
- `videoDetails` (`Optional[VideoDetail]`): Contains detailed information about the video stream itself.
- `whiteboardType` (`Optional[str]`): The type of digital whiteboard used.
- `ytStreamKey` (`Optional[str]`): YouTube stream key, if applicable.
- `ytStreamUrl` (`Optional[str]`): YouTube stream URL, if applicable.

### Helper Class: `VideoDetail`
- `id` (`str`): The unique ID of the video.
- `createdAt` (`Optional[datetime]`): Timestamp of video creation.
- `description` (`str`): Description of the video.
- `drmProtected` (`bool`): True if the video is protected by Digital Rights Management.
- `duration` (`int`): The duration of the video in seconds.
- `findKey` (`str`): A key used for video processing.
- `image` (`str`): URL for the video's thumbnail.
- `name` (`str`): The name of the video.
- `status` (`str`): The processing status of the video.
- `types` (`List[str]`): A list of video types.
- `videoUrl` (`str`): The URL to the video manifest (e.g., MPD file).

### Helper Class: `TagDetail`
- `id` (`str`): The unique ID of the tag.
- `name` (`str`): The name of the tag.

---

## `BatchNotesDetail` & `DppNotesDetails`

These models represent class notes or DPP (Daily Practice Problems) notes, which are typically PDF files. They are populated from the `/v2/batches/{batch_name}/subject/{subject_name}/contents?contentType=notes...` and `...contentType=DppNotes...` endpoints, respectively. Both models share the same structure.

- `id` (`str`): The unique identifier for the notes entry.
- `dRoomId` (`Optional[str]`): Identifier for the discussion room.
- `date` (`Optional[datetime]`): The date the notes were published.
- `homeworks` (`List[HomeworkDetail]`): A list of homework objects, which contain the actual attachment details.
- `isBatchDoubtEnabled` (`Optional[bool]`): True if the doubt feature is enabled.
- `isDPPNotes` (`Optional[bool]`): True if this is a DPP note.
- `isFree` (`Optional[bool]`): True if the notes are free.
- `isSimulatedLecture` (`Optional[bool]`): True if the notes are from a simulated lecture.
- `startTime` (`Optional[datetime]`): The publication time of the notes.
- `status` (`Optional[str]`): The status of the notes.

### Helper Class: `HomeworkDetail`
- `id` (`str`): The unique ID of the homework entry.
- `actions` (`List[Any]`): A list of associated actions.
- `attachments` (`List[AttachmentDetail]`): A list of file attachments, which are the actual notes/DPP PDFs.
- `batchSubjectId` (`Optional[str]`): The ID of the associated batch subject.
- `note` (`Optional[str]`): A description or note for the homework.
- `solutionVideoId` (`Optional[str]`): The ID of a video that explains the solutions.
- `solutionVideoType` (`Optional[str]`): The type of the solution video.
- `solutionVideoUrl` (`Optional[str]`): The URL for the solution video.
- `topic` (`Optional[str]`): The topic of the homework.

### Helper Class: `AttachmentDetail`
- `id` (`str`): The unique ID of the attachment.
- `baseUrl` (`str`): The base URL for the file location.
- `key` (`str`): The specific path or key for the file. The full URL is `baseUrl` + `key`.
- `name` (`str`): The filename of the attachment (e.g., "Chapter 1 Notes.pdf").
- `link` (`Optional[str]`): The full, concatenated link to the downloadable file.