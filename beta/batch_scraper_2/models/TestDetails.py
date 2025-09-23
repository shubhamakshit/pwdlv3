from typing import Any, Dict, List, Optional
from datetime import datetime

# Helper classes for nested structures

class EnImage:
    def __init__(self, _id: str, name: str, baseUrl: str, key: str):
        self._id = _id
        self.name = name
        self.baseUrl = baseUrl
        self.key = key
        self.link = f"{baseUrl}/{key}"

    @staticmethod
    def from_json(json_data: Dict[str, Any]) -> 'EnImage':
        return EnImage(
            _id=json_data.get('_id', ''),
            name=json_data.get('name', ''),
            baseUrl=json_data.get('baseUrl', ''),
            key=json_data.get('key', '')
        )

class OptionTexts:
    def __init__(self, en: str):
        self.en = en

    @staticmethod
    def from_json(json_data: Dict[str, Any]) -> 'OptionTexts':
        return OptionTexts(
            en=json_data.get('en', '')
        )

class Option:
    def __init__(self, _id: str, texts: Dict[str, Any]):
        self._id = _id
        self.texts = OptionTexts.from_json(texts) if texts else None

    @staticmethod
    def from_json(json_data: Dict[str, Any]) -> 'Option':
        return Option(
            _id=json_data.get('_id', ''),
            texts=json_data.get('texts', {})
        )

class SolutionVideoDetails:
    def __init__(self, _id: str, id: str, name: str, image: str, videoUrl: str,
                 duration: str, status: str, types: List[str], createdAt: str, drmProtected: bool):
        self._id = _id
        self.id = id
        self.name = name
        self.image = image
        self.videoUrl = videoUrl
        self.duration = duration
        self.status = status
        self.types = types
        # Safely convert creation date to datetime object
        self.createdAt = datetime.fromisoformat(createdAt.replace('Z', '+00:00')) if createdAt else None
        self.drmProtected = drmProtected

    @staticmethod
    def from_json(json_data: Dict[str, Any]) -> 'SolutionVideoDetails':
        return SolutionVideoDetails(
            _id=json_data.get('_id', ''),
            id=json_data.get('id', ''),
            name=json_data.get('name', ''),
            image=json_data.get('image', ''),
            videoUrl=json_data.get('videoUrl', ''),
            duration=json_data.get('duration', ''),
            status=json_data.get('status', ''),
            types=json_data.get('types', []),
            createdAt=json_data.get('createdAt', ''),
            drmProtected=json_data.get('drmProtected', False)
        )


class SolutionDescriptionItem:
    def __init__(self, _id: str, imageIds: Dict[str, Any], videoType: str, videoDetails: Dict[str, Any]):
        self._id = _id
        self.imageIds = EnImage.from_json(imageIds.get('en', {})) if imageIds and 'en' in imageIds else None
        self.videoType = videoType
        self.videoDetails = SolutionVideoDetails.from_json(videoDetails) if videoDetails else None

    @staticmethod
    def from_json(json_data: Dict[str, Any]) -> 'SolutionDescriptionItem':
        return SolutionDescriptionItem(
            _id=json_data.get('_id', ''),
            imageIds=json_data.get('imageIds', {}),
            videoType=json_data.get('videoType', ''),
            videoDetails=json_data.get('videoDetails', {})
        )

class QuestionTopicId:
    def __init__(self, name: str, _id: str):
        self.name = name
        self._id = _id

    @staticmethod
    def from_json(json_data: Dict[str, Any]) -> 'QuestionTopicId':
        return QuestionTopicId(
            name=json_data.get('name', ''),
            _id=json_data.get('_id', '')
        )

# Core data models

class SubTopicId:
    def __init__(self, name: str, _id: str):
        self.name = name
        self._id = _id

    @staticmethod
    def from_json(json_data: Dict[str, Any]) -> 'SubTopicId':
        return SubTopicId(
            name=json_data.get('name', ''),
            _id=json_data.get('_id', '')
        )

class SubTopic:
    def __init__(self, totalQuestions: int, unAttemptedQuestions: int, correctQuestions: int,
                 inCorrectQuestions: int, questionsUnderReview: int, subTopicId: Dict[str, Any]):
        self.totalQuestions = totalQuestions
        self.unAttemptedQuestions = unAttemptedQuestions
        self.correctQuestions = correctQuestions
        self.inCorrectQuestions = inCorrectQuestions
        self.questionsUnderReview = questionsUnderReview
        self.subTopicId = SubTopicId.from_json(subTopicId) if subTopicId else None

    @staticmethod
    def from_json(json_data: Dict[str, Any]) -> 'SubTopic':
        return SubTopic(
            totalQuestions=json_data.get('totalQuestions', 0),
            unAttemptedQuestions=json_data.get('unAttemptedQuestions', 0),
            correctQuestions=json_data.get('correctQuestions', 0),
            inCorrectQuestions=json_data.get('inCorrectQuestions', 0),
            questionsUnderReview=json_data.get('questionsUnderReview', 0),
            subTopicId=json_data.get('subTopicId', {})
        )

class TopicId:
    def __init__(self, name: str, _id: str):
        self.name = name
        self._id = _id

    @staticmethod
    def from_json(json_data: Dict[str, Any]) -> 'TopicId':
        return TopicId(
            name=json_data.get('name', ''),
            _id=json_data.get('_id', '')
        )

class Topic:
    def __init__(self, totalQuestions: int, unAttemptedQuestions: int, correctQuestions: int,
                 inCorrectQuestions: int, questionsUnderReview: int, topicId: Dict[str, Any],
                 subTopics: List[Dict[str, Any]]):
        self.totalQuestions = totalQuestions
        self.unAttemptedQuestions = unAttemptedQuestions
        self.correctQuestions = correctQuestions
        self.inCorrectQuestions = inCorrectQuestions
        self.questionsUnderReview = questionsUnderReview
        self.topicId = TopicId.from_json(topicId) if topicId else None
        self.subTopics = [SubTopic.from_json(st) for st in subTopics if st] if subTopics else []

    @staticmethod
    def from_json(json_data: Dict[str, Any]) -> 'Topic':
        return Topic(
            totalQuestions=json_data.get('totalQuestions', 0),
            unAttemptedQuestions=json_data.get('unAttemptedQuestions', 0),
            correctQuestions=json_data.get('correctQuestions', 0),
            inCorrectQuestions=json_data.get('inCorrectQuestions', 0),
            questionsUnderReview=json_data.get('questionsUnderReview', 0),
            topicId=json_data.get('topicId', {}),
            subTopics=json_data.get('subTopics', [])
        )

class ChapterId:
    def __init__(self, name: str, _id: str):
        self.name = name
        self._id = _id

    @staticmethod
    def from_json(json_data: Dict[str, Any]) -> 'ChapterId':
        return ChapterId(
            name=json_data.get('name', ''),
            _id=json_data.get('_id', '')
        )

class Chapter:
    def __init__(self, totalQuestions: int, unAttemptedQuestions: int, correctQuestions: int,
                 inCorrectQuestions: int, questionsUnderReview: int, chapterId: Dict[str, Any],
                 topics: List[Dict[str, Any]]):
        self.totalQuestions = totalQuestions
        self.unAttemptedQuestions = unAttemptedQuestions
        self.correctQuestions = correctQuestions
        self.inCorrectQuestions = inCorrectQuestions
        self.questionsUnderReview = questionsUnderReview
        self.chapterId = ChapterId.from_json(chapterId) if chapterId else None
        self.topics = [Topic.from_json(t) for t in topics if t] if topics else []

    @staticmethod
    def from_json(json_data: Dict[str, Any]) -> 'Chapter':
        return Chapter(
            totalQuestions=json_data.get('totalQuestions', 0),
            unAttemptedQuestions=json_data.get('unAttemptedQuestions', 0),
            correctQuestions=json_data.get('correctQuestions', 0),
            inCorrectQuestions=json_data.get('inCorrectQuestions', 0),
            questionsUnderReview=json_data.get('questionsUnderReview', 0),
            chapterId=json_data.get('chapterId', {}),
            topics=json_data.get('topics', [])
        )

class SubjectId:
    def __init__(self, name: str, _id: str):
        self.name = name
        self._id = _id

    @staticmethod
    def from_json(json_data: Dict[str, Any]) -> 'SubjectId':
        return SubjectId(
            name=json_data.get('name', ''),
            _id=json_data.get('_id', '')
        )

class Subject:
    def __init__(self, totalQuestions: int, unAttemptedQuestions: int, correctQuestions: int,
                 inCorrectQuestions: int, questionsUnderReview: int, subjectId: Dict[str, Any],
                 chapters: List[Dict[str, Any]]):
        self.totalQuestions = totalQuestions
        self.unAttemptedQuestions = unAttemptedQuestions
        self.correctQuestions = correctQuestions
        self.inCorrectQuestions = inCorrectQuestions
        self.questionsUnderReview = questionsUnderReview
        self.subjectId = SubjectId.from_json(subjectId) if subjectId else None
        self.chapters = [Chapter.from_json(c) for c in chapters if c] if chapters else []

    @staticmethod
    def from_json(json_data: Dict[str, Any]) -> 'Subject':
        return Subject(
            totalQuestions=json_data.get('totalQuestions', 0),
            unAttemptedQuestions=json_data.get('unAttemptedQuestions', 0),
            correctQuestions=json_data.get('correctQuestions', 0),
            inCorrectQuestions=json_data.get('inCorrectQuestions', 0),
            questionsUnderReview=json_data.get('questionsUnderReview', 0),
            subjectId=json_data.get('subjectId', {}),
            chapters=json_data.get('chapters', [])
        )

class SectionId:
    def __init__(self, name: str, _id: str, isOptional: bool):
        self.name = name
        self._id = _id
        self.isOptional = isOptional

    @staticmethod
    def from_json(json_data: Dict[str, Any]) -> 'SectionId':
        return SectionId(
            name=json_data.get('name', ''),
            _id=json_data.get('_id', ''),
            isOptional=json_data.get('isOptional', False)
        )

class Section:
    def __init__(self, totalQuestions: int, unAttemptedQuestions: int, correctQuestions: int,
                 inCorrectQuestions: int, questionsUnderReview: int, sectionId: Dict[str, Any],
                 subjects: List[Dict[str, Any]], isExtra: bool, selectedOptionalSection: bool):
        self.totalQuestions = totalQuestions
        self.unAttemptedQuestions = unAttemptedQuestions
        self.correctQuestions = correctQuestions
        self.inCorrectQuestions = inCorrectQuestions
        self.questionsUnderReview = questionsUnderReview
        self.sectionId = SectionId.from_json(sectionId) if sectionId else None
        self.subjects = [Subject.from_json(s) for s in subjects if s] if subjects else []
        self.isExtra = isExtra
        self.selectedOptionalSection = selectedOptionalSection

    @staticmethod
    def from_json(json_data: Dict[str, Any]) -> 'Section':
        return Section(
            totalQuestions=json_data.get('totalQuestions', 0),
            unAttemptedQuestions=json_data.get('unAttemptedQuestions', 0),
            correctQuestions=json_data.get('correctQuestions', 0),
            inCorrectQuestions=json_data.get('inCorrectQuestions', 0),
            questionsUnderReview=json_data.get('questionsUnderReview', 0),
            sectionId=json_data.get('sectionId', {}),
            subjects=json_data.get('subjects', []),
            isExtra=json_data.get('isExtra', False),
            selectedOptionalSection=json_data.get('selectedOptionalSection', False)
        )

class DifficultyLevel:
    def __init__(self, level: Optional[int], title: str):
        self.level = level
        self.title = title

    @staticmethod
    def from_json(json_data: Dict[str, Any]) -> 'DifficultyLevel':
        return DifficultyLevel(
            level=json_data.get('level', 0),
            title=json_data.get('title', '')
        )

class Question:
    def __init__(self, _id: str, type: str, questionNumber: int, positiveMarks: int, positiveMarksStr: str,
                 negativeMarks: int, negativeMarksStr: str, imageIds: Dict[str, Any], options: List[Dict[str, Any]],
                 difficultyLevel: int, pyqYears: List[Any], topicId: Dict[str, Any], sectionId: str,
                 subjectId: str, chapterId: str, solutions: List[str], solutionDescription: List[Dict[str, Any]],
                 qbgSubjectId: str, qbgChapterId: str, qbgTopicId: str, qbgId: str, exam: str,
                 subTopicId: Optional[str] = None):
        self._id = _id
        self.type = type
        self.questionNumber = questionNumber
        self.positiveMarks = positiveMarks
        self.positiveMarksStr = positiveMarksStr
        self.negativeMarks = negativeMarks
        self.negativeMarksStr = negativeMarksStr
        self.imageIds = EnImage.from_json(imageIds.get('en', {})) if imageIds and 'en' in imageIds else None
        self.options = [Option.from_json(opt) for opt in options if opt] if options else []
        self.difficultyLevel = difficultyLevel
        self.pyqYears = pyqYears
        self.topicId = QuestionTopicId.from_json(topicId) if topicId else None
        self.sectionId = sectionId
        self.subjectId = subjectId
        self.chapterId = chapterId
        self.solutions = solutions
        self.solutionDescription = [SolutionDescriptionItem.from_json(sd) for sd in solutionDescription if sd] if solutionDescription else []
        self.qbgSubjectId = qbgSubjectId
        self.qbgChapterId = qbgChapterId
        self.qbgTopicId = qbgTopicId
        self.qbgId = qbgId
        self.exam = exam
        self.subTopicId = subTopicId

    @staticmethod
    def from_json(json_data: Dict[str, Any]) -> 'Question':
        return Question(
            _id=json_data.get('_id', ''),
            type=json_data.get('type', ''),
            questionNumber=json_data.get('questionNumber', 0),
            positiveMarks=json_data.get('positiveMarks', 0),
            positiveMarksStr=json_data.get('positiveMarksStr', ''),
            negativeMarks=json_data.get('negativeMarks', 0),
            negativeMarksStr=json_data.get('negativeMarksStr', ''),
            imageIds=json_data.get('imageIds', {}),
            options=json_data.get('options', []),
            difficultyLevel=json_data.get('difficultyLevel', 0),
            pyqYears=json_data.get('pyqYears', []),
            topicId=json_data.get('topicId', {}),
            sectionId=json_data.get('sectionId', ''),
            subjectId=json_data.get('subjectId', ''),
            chapterId=json_data.get('chapterId', ''),
            solutions=json_data.get('solutions', []),
            solutionDescription=json_data.get('solutionDescription', []),
            qbgSubjectId=json_data.get('qbgSubjectId', ''),
            qbgChapterId=json_data.get('qbgChapterId', ''),
            qbgTopicId=json_data.get('qbgTopicId', ''),
            qbgId=json_data.get('qbgId', ''),
            exam=json_data.get('exam', ''),
            subTopicId=json_data.get('subTopicId', '')
        )

class YourResult:
    def __init__(self, isUnderReview: bool, status: str, markedSolutions: List[str],
                 markedSolutionText: str, score: int, scoreStr: str, timeTaken: int):
        self.isUnderReview = isUnderReview
        self.status = status
        self.markedSolutions = markedSolutions
        self.markedSolutionText = markedSolutionText
        self.score = score
        self.scoreStr = scoreStr
        self.timeTaken = timeTaken

    @staticmethod
    def from_json(json_data: Dict[str, Any]) -> 'YourResult':
        return YourResult(
            isUnderReview=json_data.get('isUnderReview', False),
            status=json_data.get('status', ''),
            markedSolutions=json_data.get('markedSolutions', []),
            markedSolutionText=json_data.get('markedSolutionText', ''),
            score=json_data.get('score', 0),
            scoreStr=json_data.get('scoreStr', ''),
            timeTaken=json_data.get('timeTaken', 0)
        )

class TopperResult:
    def __init__(self, status: str, markedSolutions: List[str], markedSolutionText: str,
                 score: int, timeTaken: int):
        self.status = status
        self.markedSolutions = markedSolutions
        self.markedSolutionText = markedSolutionText
        self.score = score
        self.timeTaken = timeTaken

    @staticmethod
    def from_json(json_data: Dict[str, Any]) -> 'TopperResult':
        return TopperResult(
            status=json_data.get('status', ''),
            markedSolutions=json_data.get('markedSolutions', []),
            markedSolutionText=json_data.get('markedSolutionText', ''),
            score=json_data.get('score', 0),
            timeTaken=json_data.get('timeTaken', 0)
        )

class AverageResult:
    # This is an empty object in the schema, so it can be represented by a simple class or a dict.
    # We'll use a simple class for consistency.
    def __init__(self):
        pass

    @staticmethod
    def from_json(json_data: Dict[str, Any]) -> 'AverageResult':
        return AverageResult()

class QuestionItem:
    def __init__(self, question: Dict[str, Any], yourResult: Dict[str, Any],
                 topperResult: Dict[str, Any], averageResult: Dict[str, Any]):
        self.question = Question.from_json(question) if question else None
        self.yourResult = YourResult.from_json(yourResult) if yourResult else None
        self.topperResult = TopperResult.from_json(topperResult) if topperResult else None
        self.averageResult = AverageResult.from_json(averageResult) if averageResult else None

    @staticmethod
    def from_json(json_data: Dict[str, Any]) -> 'QuestionItem':
        return QuestionItem(
            question=json_data.get('question', {}),
            yourResult=json_data.get('yourResult', {}),
            topperResult=json_data.get('topperResult', {}),
            averageResult=json_data.get('averageResult', {})
        )

class LanguageCode:
    def __init__(self, language: str, isSelected: bool, code: str):
        self.language = language
        self.isSelected = isSelected
        self.code = code

    @staticmethod
    def from_json(json_data: Dict[str, Any]) -> 'LanguageCode':
        return LanguageCode(
            language=json_data.get('language', ''),
            isSelected=json_data.get('isSelected', False),
            code=json_data.get('code', '')
        )

class Test:
    def __init__(self, _id: str, name: str, type: str, template: str):
        self._id = _id
        self.name = name
        self.type = type
        self.template = template

    @staticmethod
    def from_json(json_data: Dict[str, Any]) -> 'Test':
        return Test(
            _id=json_data.get('_id', ''),
            name=json_data.get('name', ''),
            type=json_data.get('type', ''),
            template=json_data.get('template', '')
        )

class ComprehensionData:
    def __init__(self, comprehensions: List[Any], comprehensionRanges: List[Any]):
        # The schema indicates these are empty arrays, so Any is appropriate.
        self.comprehensions = comprehensions
        self.comprehensionRanges = comprehensionRanges

    @staticmethod
    def from_json(json_data: Dict[str, Any]) -> 'ComprehensionData':
        return ComprehensionData(
            comprehensions=json_data.get('comprehensions', []),
            comprehensionRanges=json_data.get('comprehensionRanges', [])
        )

class Data:
    def __init__(self, sections: List[Dict[str, Any]], difficultyLevels: List[Dict[str, Any]],
                 questions: List[Dict[str, Any]], languageCodes: List[Dict[str, Any]],
                 test: Dict[str, Any], isLiveAttempt: bool, comprehensionData: Dict[str, Any],
                 bookmarkEnabled: bool):
        self.sections = [Section.from_json(s) for s in sections if s] if sections else []
        self.difficultyLevels = [DifficultyLevel.from_json(dl) for dl in difficultyLevels if dl] if difficultyLevels else []
        self.questions = [QuestionItem.from_json(q) for q in questions if q] if questions else []
        self.languageCodes = [LanguageCode.from_json(lc) for lc in languageCodes if lc] if languageCodes else []
        self.test = Test.from_json(test) if test else None
        self.isLiveAttempt = isLiveAttempt
        self.comprehensionData = ComprehensionData.from_json(comprehensionData) if comprehensionData else None
        self.bookmarkEnabled = bookmarkEnabled

    @staticmethod
    def from_json(json_data: Dict[str, Any]) -> 'Data':
        return Data(
            sections=json_data.get('sections', []),
            difficultyLevels=json_data.get('difficultyLevels', []),
            questions=json_data.get('questions', []),
            languageCodes=json_data.get('languageCodes', []),
            test=json_data.get('test', {}),
            isLiveAttempt=json_data.get('isLiveAttempt', False),
            comprehensionData=json_data.get('comprehensionData', {}),
            bookmarkEnabled=json_data.get('bookmarkEnabled', False)
        )

class TestDetails:
    def __init__(self, success: bool, statusCode: int, data: Dict[str, Any]):
        self.success = success
        self.statusCode = statusCode
        self.data = Data.from_json(data) if data else None

    @staticmethod
    def from_json(json_data: Dict[str, Any]) -> 'TestDetails':
        return TestDetails(
            success=json_data.get('success', False),
            statusCode=json_data.get('statusCode', 0),
            data=json_data.get('data', {})
        )