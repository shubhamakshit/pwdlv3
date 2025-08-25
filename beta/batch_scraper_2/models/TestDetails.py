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
            _id=json_data['_id'],
            name=json_data['name'],
            baseUrl=json_data['baseUrl'],
            key=json_data['key']
        )

class OptionTexts:
    def __init__(self, en: str):
        self.en = en

    @staticmethod
    def from_json(json_data: Dict[str, Any]) -> 'OptionTexts':
        return OptionTexts(
            en=json_data['en']
        )

class Option:
    def __init__(self, _id: str, texts: Dict[str, Any]):
        self._id = _id
        self.texts = OptionTexts.from_json(texts)

    @staticmethod
    def from_json(json_data: Dict[str, Any]) -> 'Option':
        return Option(
            _id=json_data['_id'],
            texts=json_data['texts']
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
            _id=json_data.get('_id', ""),
            id=json_data.get('id', ""),
            name=json_data.get('name', ""),
            image=json_data.get('image', ""),
            videoUrl=json_data.get('videoUrl', ""),
            duration=json_data.get('duration', ""),
            status=json_data.get('status', ""),
            types=json_data.get('types', ""),
            createdAt=json_data.get('createdAt', ""),
            drmProtected=json_data.get('drmProtected', False)
        )


class SolutionDescriptionItem:
    def __init__(self, _id: str, imageIds: Dict[str, Any], videoType: str, videoDetails: Dict[str, Any]):
        self._id = _id
        self.imageIds = EnImage.from_json(imageIds['en']) if 'en' in imageIds else None
        self.videoType = videoType
        self.videoDetails = SolutionVideoDetails.from_json(videoDetails)

    @staticmethod
    def from_json(json_data: Dict[str, Any]) -> 'SolutionDescriptionItem':
        return SolutionDescriptionItem(
            _id=json_data['_id'],
            imageIds=json_data['imageIds'],
            videoType=json_data['videoType'],
            videoDetails=json_data['videoDetails']
        )

class QuestionTopicId:
    def __init__(self, name: str, _id: str):
        self.name = name
        self._id = _id

    @staticmethod
    def from_json(json_data: Dict[str, Any]) -> 'QuestionTopicId':
        return QuestionTopicId(
            name=json_data['name'],
            _id=json_data['_id']
        )

# Core data models

class SubTopicId:
    def __init__(self, name: str, _id: str):
        self.name = name
        self._id = _id

    @staticmethod
    def from_json(json_data: Dict[str, Any]) -> 'SubTopicId':
        return SubTopicId(
            name=json_data['name'],
            _id=json_data['_id']
        )

class SubTopic:
    def __init__(self, totalQuestions: int, unAttemptedQuestions: int, correctQuestions: int,
                 inCorrectQuestions: int, questionsUnderReview: int, subTopicId: Dict[str, Any]):
        self.totalQuestions = totalQuestions
        self.unAttemptedQuestions = unAttemptedQuestions
        self.correctQuestions = correctQuestions
        self.inCorrectQuestions = inCorrectQuestions
        self.questionsUnderReview = questionsUnderReview
        self.subTopicId = SubTopicId.from_json(subTopicId)

    @staticmethod
    def from_json(json_data: Dict[str, Any]) -> 'SubTopic':
        return SubTopic(
            totalQuestions=json_data['totalQuestions'],
            unAttemptedQuestions=json_data['unAttemptedQuestions'],
            correctQuestions=json_data['correctQuestions'],
            inCorrectQuestions=json_data['inCorrectQuestions'],
            questionsUnderReview=json_data['questionsUnderReview'],
            subTopicId=json_data['subTopicId']
        )

class TopicId:
    def __init__(self, name: str, _id: str):
        self.name = name
        self._id = _id

    @staticmethod
    def from_json(json_data: Dict[str, Any]) -> 'TopicId':
        return TopicId(
            name=json_data['name'],
            _id=json_data['_id']
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
        self.topicId = TopicId.from_json(topicId)
        self.subTopics = [SubTopic.from_json(st) for st in subTopics]

    @staticmethod
    def from_json(json_data: Dict[str, Any]) -> 'Topic':
        return Topic(
            totalQuestions=json_data['totalQuestions'],
            unAttemptedQuestions=json_data['unAttemptedQuestions'],
            correctQuestions=json_data['correctQuestions'],
            inCorrectQuestions=json_data['inCorrectQuestions'],
            questionsUnderReview=json_data['questionsUnderReview'],
            topicId=json_data['topicId'],
            subTopics=json_data['subTopics']
        )

class ChapterId:
    def __init__(self, name: str, _id: str):
        self.name = name
        self._id = _id

    @staticmethod
    def from_json(json_data: Dict[str, Any]) -> 'ChapterId':
        return ChapterId(
            name=json_data['name'],
            _id=json_data['_id']
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
        self.chapterId = ChapterId.from_json(chapterId)
        self.topics = [Topic.from_json(t) for t in topics]

    @staticmethod
    def from_json(json_data: Dict[str, Any]) -> 'Chapter':
        return Chapter(
            totalQuestions=json_data['totalQuestions'],
            unAttemptedQuestions=json_data['unAttemptedQuestions'],
            correctQuestions=json_data['correctQuestions'],
            inCorrectQuestions=json_data['inCorrectQuestions'],
            questionsUnderReview=json_data['questionsUnderReview'],
            chapterId=json_data['chapterId'],
            topics=json_data['topics']
        )

class SubjectId:
    def __init__(self, name: str, _id: str):
        self.name = name
        self._id = _id

    @staticmethod
    def from_json(json_data: Dict[str, Any]) -> 'SubjectId':
        return SubjectId(
            name=json_data['name'],
            _id=json_data['_id']
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
        self.subjectId = SubjectId.from_json(subjectId)
        self.chapters = [Chapter.from_json(c) for c in chapters]

    @staticmethod
    def from_json(json_data: Dict[str, Any]) -> 'Subject':
        return Subject(
            totalQuestions=json_data['totalQuestions'],
            unAttemptedQuestions=json_data['unAttemptedQuestions'],
            correctQuestions=json_data['correctQuestions'],
            inCorrectQuestions=json_data['inCorrectQuestions'],
            questionsUnderReview=json_data['questionsUnderReview'],
            subjectId=json_data['subjectId'],
            chapters=json_data['chapters']
        )

class SectionId:
    def __init__(self, name: str, _id: str, isOptional: bool):
        self.name = name
        self._id = _id
        self.isOptional = isOptional

    @staticmethod
    def from_json(json_data: Dict[str, Any]) -> 'SectionId':
        return SectionId(
            name=json_data['name'],
            _id=json_data['_id'],
            isOptional=json_data['isOptional']
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
        self.sectionId = SectionId.from_json(sectionId)
        self.subjects = [Subject.from_json(s) for s in subjects]
        self.isExtra = isExtra
        self.selectedOptionalSection = selectedOptionalSection

    @staticmethod
    def from_json(json_data: Dict[str, Any]) -> 'Section':
        return Section(
            totalQuestions=json_data['totalQuestions'],
            unAttemptedQuestions=json_data['unAttemptedQuestions'],
            correctQuestions=json_data['correctQuestions'],
            inCorrectQuestions=json_data['inCorrectQuestions'],
            questionsUnderReview=json_data['questionsUnderReview'],
            sectionId=json_data['sectionId'],
            subjects=json_data['subjects'],
            isExtra=json_data['isExtra'],
            selectedOptionalSection=json_data['selectedOptionalSection']
        )

class DifficultyLevel:
    def __init__(self, level: Optional[int], title: str):
        self.level = level
        self.title = title

    @staticmethod
    def from_json(json_data: Dict[str, Any]) -> 'DifficultyLevel':
        return DifficultyLevel(
            level=json_data.get('level'), # Level might be optional based on schema 'properties' but not 'required' list
            title=json_data['title']
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
        self.imageIds = EnImage.from_json(imageIds['en']) if 'en' in imageIds else None
        self.options = [Option.from_json(opt) for opt in options]
        self.difficultyLevel = difficultyLevel
        self.pyqYears = pyqYears
        self.topicId = QuestionTopicId.from_json(topicId)
        self.sectionId = sectionId
        self.subjectId = subjectId
        self.chapterId = chapterId
        self.solutions = solutions
        self.solutionDescription = [SolutionDescriptionItem.from_json(sd) for sd in solutionDescription]
        self.qbgSubjectId = qbgSubjectId
        self.qbgChapterId = qbgChapterId
        self.qbgTopicId = qbgTopicId
        self.qbgId = qbgId
        self.exam = exam
        self.subTopicId = subTopicId

    @staticmethod
    def from_json(json_data: Dict[str, Any]) -> 'Question':
        return Question(
            _id=json_data['_id'],
            type=json_data['type'],
            questionNumber=json_data['questionNumber'],
            positiveMarks=json_data['positiveMarks'],
            positiveMarksStr=json_data['positiveMarksStr'],
            negativeMarks=json_data['negativeMarks'],
            negativeMarksStr=json_data['negativeMarksStr'],
            imageIds=json_data['imageIds'],
            options=json_data['options'],
            difficultyLevel=json_data['difficultyLevel'],
            pyqYears=json_data['pyqYears'],
            topicId=json_data['topicId'],
            sectionId=json_data['sectionId'],
            subjectId=json_data['subjectId'],
            chapterId=json_data['chapterId'],
            solutions=json_data['solutions'],
            solutionDescription=json_data['solutionDescription'],
            qbgSubjectId=json_data['qbgSubjectId'],
            qbgChapterId=json_data['qbgChapterId'],
            qbgTopicId=json_data['qbgTopicId'],
            qbgId=json_data['qbgId'],
            exam=json_data['exam'],
            subTopicId=json_data.get('subTopicId')
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
            isUnderReview=json_data['isUnderReview'],
            status=json_data['status'],
            markedSolutions=json_data['markedSolutions'],
            markedSolutionText=json_data['markedSolutionText'],
            score=json_data['score'],
            scoreStr=json_data['scoreStr'],
            timeTaken=json_data['timeTaken']
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
            status=json_data['status'],
            markedSolutions=json_data['markedSolutions'],
            markedSolutionText=json_data['markedSolutionText'],
            score=json_data['score'],
            timeTaken=json_data['timeTaken']
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
        self.question = Question.from_json(question)
        self.yourResult = YourResult.from_json(yourResult)
        self.topperResult = TopperResult.from_json(topperResult)
        self.averageResult = AverageResult.from_json(averageResult)

    @staticmethod
    def from_json(json_data: Dict[str, Any]) -> 'QuestionItem':
        return QuestionItem(
            question=json_data['question'],
            yourResult=json_data['yourResult'],
            topperResult=json_data['topperResult'],
            averageResult=json_data['averageResult']
        )

class LanguageCode:
    def __init__(self, language: str, isSelected: bool, code: str):
        self.language = language
        self.isSelected = isSelected
        self.code = code

    @staticmethod
    def from_json(json_data: Dict[str, Any]) -> 'LanguageCode':
        return LanguageCode(
            language=json_data['language'],
            isSelected=json_data['isSelected'],
            code=json_data['code']
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
            _id=json_data['_id'],
            name=json_data['name'],
            type=json_data['type'],
            template=json_data['template']
        )

class ComprehensionData:
    def __init__(self, comprehensions: List[Any], comprehensionRanges: List[Any]):
        # The schema indicates these are empty arrays, so Any is appropriate.
        self.comprehensions = comprehensions
        self.comprehensionRanges = comprehensionRanges

    @staticmethod
    def from_json(json_data: Dict[str, Any]) -> 'ComprehensionData':
        return ComprehensionData(
            comprehensions=json_data['comprehensions'],
            comprehensionRanges=json_data['comprehensionRanges']
        )

class Data:
    def __init__(self, sections: List[Dict[str, Any]], difficultyLevels: List[Dict[str, Any]],
                 questions: List[Dict[str, Any]], languageCodes: List[Dict[str, Any]],
                 test: Dict[str, Any], isLiveAttempt: bool, comprehensionData: Dict[str, Any],
                 bookmarkEnabled: bool):
        self.sections = [Section.from_json(s) for s in sections]
        self.difficultyLevels = [DifficultyLevel.from_json(dl) for dl in difficultyLevels]
        self.questions = [QuestionItem.from_json(q) for q in questions]
        self.languageCodes = [LanguageCode.from_json(lc) for lc in languageCodes]
        self.test = Test.from_json(test)
        self.isLiveAttempt = isLiveAttempt
        self.comprehensionData = ComprehensionData.from_json(comprehensionData)
        self.bookmarkEnabled = bookmarkEnabled

    @staticmethod
    def from_json(json_data: Dict[str, Any]) -> 'Data':
        return Data(
            sections=json_data['sections'],
            difficultyLevels=json_data['difficultyLevels'],
            questions=json_data['questions'],
            languageCodes=json_data['languageCodes'],
            test=json_data['test'],
            isLiveAttempt=json_data['isLiveAttempt'],
            comprehensionData=json_data['comprehensionData'],
            bookmarkEnabled=json_data['bookmarkEnabled']
        )

class TestDetails:
    def __init__(self, success: bool, statusCode: int, data: Dict[str, Any]):
        self.success = success
        self.statusCode = statusCode
        self.data = Data.from_json(data)

    @staticmethod
    def from_json(json_data: Dict[str, Any]) -> 'Root':
        return TestDetails(
            success=json_data['success'],
            statusCode=json_data['statusCode'],
            data=json_data['data']
        )