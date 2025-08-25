from typing import Any, Dict, List, Optional
from datetime import datetime

# Helper class for Config details
class ConfigDetail:
    def __init__(self,
                 isScientificCalculatorEnabled: bool,
                 proctoring: bool,
                 enableCatPercentile: bool,
                 enableBasicCalculator: bool):
        self.isScientificCalculatorEnabled = isScientificCalculatorEnabled
        self.proctoring = proctoring
        self.enableCatPercentile = enableCatPercentile
        self.enableBasicCalculator = enableBasicCalculator

    @staticmethod
    def from_json(json_data: Dict[str, Any]) -> 'ConfigDetail':
        return ConfigDetail(
            isScientificCalculatorEnabled=json_data.get('isScientificCalculatorEnabled'),
            proctoring=json_data.get('proctoring'),
            enableCatPercentile=json_data.get('enableCatPercentile', False),
            enableBasicCalculator=json_data.get('enableBasicCalculator')
        )


# Helper class for individual Test details
class TestDetail:
    def __init__(self,
                 _id: str,
                 type: str,
                 currentType: str,
                 name: str,
                 slug: str,
                 totalQuestions: int,
                 totalMarks: float,
                 startTime: str,
                 maxStartTime: str,
                 endTime: str,
                 resultScheduleAt: str,
                 maxDuration: float,
                 availableFor: List[str],
                 isSubjective: bool,
                 isPurchased: bool,
                 isFree: bool,
                 attempts: int,
                 testStudentMappingId: str,
                 testActivityStatus: str,
                 testSource: str,
                 fomoIntent: Any,
                 modeType: str,
                 toastMessage: Any,
                 infoMessage: Any,
                 tag1: str,
                 tag2: str,
                 isResultAwaiting: bool,
                 toastImage: Any,
                 config: ConfigDetail,
                 isDelivered: bool,
                 categoryId: str,
                 template: str,
                 enableInstructions: bool,
                 enableSyllabus: bool,
                 smartDPP: bool,
                 difficultyLevel: str):
        self.id = _id
        self.type = type
        self.currentType = currentType
        self.name = name
        self.slug = slug
        self.totalQuestions = totalQuestions
        self.totalMarks = totalMarks
        self.startTime = startTime
        self.maxStartTime = maxStartTime
        self.endTime = endTime
        self.resultScheduleAt = resultScheduleAt
        self.maxDuration = maxDuration
        self.availableFor = availableFor
        self.isSubjective = isSubjective
        self.isPurchased = isPurchased
        self.isFree = isFree
        self.attempts = attempts
        self.testStudentMappingId = testStudentMappingId
        self.testActivityStatus = testActivityStatus
        self.testSource = testSource
        self.fomoIntent = fomoIntent
        self.modeType = modeType
        self.toastMessage = toastMessage
        self.infoMessage = infoMessage
        self.tag1 = tag1
        self.tag2 = tag2
        self.isResultAwaiting = isResultAwaiting
        self.toastImage = toastImage
        self.config = config
        self.isDelivered = isDelivered
        self.categoryId = categoryId
        self.template = template
        self.enableInstructions = enableInstructions
        self.enableSyllabus = enableSyllabus
        self.smartDPP = smartDPP
        self.difficultyLevel = difficultyLevel

    @staticmethod
    def from_json(json_data: Dict[str, Any]) -> 'TestDetail':
        config = ConfigDetail.from_json(json_data.get('config', {}))
        return TestDetail(
            _id=json_data.get('_id'),
            type=json_data.get('type'),
            currentType=json_data.get('currentType'),
            name=json_data.get('name'),
            slug=json_data.get('slug'),
            totalQuestions=json_data.get('totalQuestions'),
            totalMarks=json_data.get('totalMarks'),
            startTime=json_data.get('startTime'),
            maxStartTime=json_data.get('maxStartTime'),
            endTime=json_data.get('endTime'),
            resultScheduleAt=json_data.get('resultScheduleAt'),
            maxDuration=json_data.get('maxDuration'),
            availableFor=json_data.get('availableFor', []),
            isSubjective=json_data.get('isSubjective'),
            isPurchased=json_data.get('isPurchased'),
            isFree=json_data.get('isFree'),
            attempts=json_data.get('attempts'),
            testStudentMappingId=json_data.get('testStudentMappingId'),
            testActivityStatus=json_data.get('testActivityStatus'),
            testSource=json_data.get('testSource'),
            fomoIntent=json_data.get('fomoIntent'),
            modeType=json_data.get('modeType'),
            toastMessage=json_data.get('toastMessage'),
            infoMessage=json_data.get('infoMessage'),
            tag1=json_data.get('tag1'),
            tag2=json_data.get('tag2'),
            isResultAwaiting=json_data.get('isResultAwaiting'),
            toastImage=json_data.get('toastImage'),
            config=config,
            isDelivered=json_data.get('isDelivered'),
            categoryId=json_data.get('categoryId'),
            template=json_data.get('template'),
            enableInstructions=json_data.get('enableInstructions'),
            enableSyllabus=json_data.get('enableSyllabus'),
            smartDPP=json_data.get('smartDPP'),
            difficultyLevel=json_data.get('difficultyLevel')
        )


# Root class for all test data response
class AllTestDetails:
    def __init__(self,
                 success: bool,
                 statusCode: int,
                 data: List[TestDetail]):
        self.success = success
        self.statusCode = statusCode
        self.data = data

    @staticmethod
    def from_json(json_data: Dict[str, Any]) -> 'AllTestDetails':
        return AllTestDetails(
            success=json_data.get('success'),
            statusCode=json_data.get('statusCode'),
            data=[TestDetail.from_json(test) for test in json_data.get('data', [])]
        )
