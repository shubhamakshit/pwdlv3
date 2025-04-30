import traceback

from mainLogic.utils.Debugger import Debugger
from mainLogic.utils.glv import Global
import colorama
from colorama import Fore, Style
import traceback

debugger = Debugger(enabled=True,show_location=True)


errorList = {
    "unknownError": {
        "code": 100,
        "func": lambda: debugger.error("Unknown error. Exiting..."),
        "message_template": "An unknown error has occurred. Please check the logs for details."
    },
    "noError": {
        "code": 0,
        "func": lambda: None,
        "message_template": "No errors detected. All systems operational."
    },
    "defaultsNotFound": {
        "code": 1,
        "func": lambda: debugger.error("defaults.json not found. Exiting..."),
        "message_template": "The configuration file defaults.json is missing. Please restore it."
    },
    "dependencyNotFound": {
        "code": 2,
        "func": lambda x=None: debugger.error(f"{'Dependency' if x is None else x} not found. Exiting..."),
        "message_template": "{dependency} is required but was not found. Please install it."
    },
    "dependencyNotFoundInPrefs": {
        "code": 3,
        "func": lambda x=None: debugger.error(f"{'Dependency' if x is None else x} not found in default settings. Exiting..."),
        "message_template": "{dependency} is not configured in the settings. Check your preferences."
    },
    "csvFileNotFound": {
        "code": 4,
        "func": lambda fileName: debugger.error(f"CSV file {fileName} not found. Exiting..."),
        "message_template": "The CSV file {fileName} is missing. Ensure it is in the correct directory."
    },
    "downloadFailed": {
        "code": 5,
        "func": lambda name, id: debugger.error(f"Download failed for {name} with id {id}. (Main.process exited) Exiting..."),
        "message_template": "Failed to download {name} (ID: {id}). Please try again."
    },
    "couldNotMakeDir": {
        "code": 6,
        "func": lambda dirName: debugger.error(f"Could not make directory {dirName}. Exiting..."),
        "message_template": "Unable to create the directory {dirName}. Check permissions."
    },
    "tokenNotFound": {
        "code": 7,
        "func": lambda: debugger.error("Token not found in default settings. Exiting..."),
        "message_template": "Authentication token not found in the configuration."
    },
    "tokenInvalid": {
        "code": 8,
        "func": lambda: debugger.error("Token invalid. Exiting..."),
        "message_template": "The provided token is invalid. Please verify your credentials."
    },
    "overWriteAbortedByUser": {
        "code": 9,
        "func": lambda: debugger.error("Overwrite aborted by user. Exiting..."),
        "message_template": "Overwrite operation was cancelled by the user."
    },
    "cantLoadFile": {
        "code": 22,
        "func": lambda fileName: debugger.error(f"Can't load file {fileName}"),
        "message_template": "Unable to load the file {fileName}. Check if it exists."
    },
    "flareNotStarted": {
        "code": 23,
        "func": lambda: debugger.error("Flare is not started. Start the flare server first."),
        "message_template": "Flare server is not running. Please start it before proceeding."
    },
    "requestFailedDueToUnknownReason": {
        "code": 24,
        "func": lambda status_code: debugger.error("Request failed due to unknown reason. Status Code: " + str(status_code)),
        "message_template": "The request encountered an unknown issue (Status Code: {status_code})."
    },
    "keyExtractionFailed": {
        "code": 25,
        "func": lambda id: debugger.error(f"Key extraction failed for id -> {id}. Exiting..."),
        "message_template": "Failed to extract key for ID: {id}. Please verify the input."
    },
    "keyNotProvided": {
        "code": 26,
        "func": lambda: debugger.error("Key not provided. Exiting..."),
        "message_template": "No key was provided for the operation. Please input a key."
    },
    "idNotProvided": {
        "code": 45,
        "func": lambda: debugger.error("ID not provided. Exiting..."),
        "message_template": "No ID was provided for the operation. Please input an ID"
    },
    "couldNotDownloadAudio": {
        "code": 27,
        "func": lambda id: debugger.error(f"Could not download audio for id -> {id} Exiting..."),
        "message_template": "Audio download failed for ID: {id}. Please check your connection."
    },
    "couldNotDownloadVideo": {
        "code": 28,
        "func": lambda id: debugger.error(f"Could not download video for id -> {id} Exiting..."),
        "message_template": "Video download failed for ID: {id}. Ensure the source is available."
    },
    "couldNotDecryptAudio": {
        "code": 29,
        "func": lambda: debugger.error("Could not Ravenclaw_decrypt audio. Exiting..."),
        "message_template": "Audio decryption failed. Check the audio file integrity."
    },
    "couldNotDecryptVideo": {
        "code": 30,
        "func": lambda: debugger.error("Could not Ravenclaw_decrypt video. Exiting..."),
        "message_template": "Video decryption failed. Ensure the video file is valid."
    },
    "methodPatched": {
        "code": 31,
        "func": lambda: debugger.error("Method is patched. Exiting..."),
        "message_template": "The method you are trying to use has been patched and is no longer available."
    },
    "couldNotExtractKey": {
        "code": 32,
        "func": lambda: debugger.error("Could not extract key. Exiting..."),
        "message_template": "Key extraction process encountered an error. Please review the input parameters."
    },
    "adaptationSetIsNotVideo": {
        "code": 33,
        "func": lambda: debugger.error("Adaptation set is not video. Exiting..."),
        "message_template": "The provided adaptation set does not contain video data."
    }
}


class PwdlError(Exception):
    def __init__(self, message, code=999, func=None, verbose=False):
        self.message = message
        self.code = code
        self.func = func
        self.verbose = verbose

        super().__init__(self.message)

    def __str__(self):

        # Color the output
        return f"Pwdlv3: {self.message} Failed with code {self.code}"

    def exit(self):
        debugger.error(self.__str__())
        exit(self.code)

class UnknownError(PwdlError):
    def __init__(self):
        super().__init__(errorList["unknownError"]["message_template"],
                         errorList["unknownError"]["code"],
                         errorList["unknownError"]["func"])

class NoError(PwdlError):
    def __init__(self):
        super().__init__(errorList["noError"]["message_template"],
                         errorList["noError"]["code"],
                         errorList["noError"]["func"])

class DefaultsNotFound(PwdlError):
    def __init__(self):
        super().__init__(errorList["defaultsNotFound"]["message_template"],
                         errorList["defaultsNotFound"]["code"],
                         errorList["defaultsNotFound"]["func"])

class DependencyNotFound(PwdlError):
    def __init__(self, dependency=None):
        super().__init__(errorList["dependencyNotFound"]["message_template"].format(dependency=dependency or "Dependency"),
                         errorList["dependencyNotFound"]["code"],
                         errorList["dependencyNotFound"]["func"])

class DependencyNotFoundInPrefs(PwdlError):
    def __init__(self, dependency=None):
        super().__init__(errorList["dependencyNotFoundInPrefs"]["message_template"].format(dependency=dependency or "Dependency"),
                         errorList["dependencyNotFoundInPrefs"]["code"],
                         errorList["dependencyNotFoundInPrefs"]["func"])

class CsvFileNotFound(PwdlError):
    def __init__(self, fileName):
        super().__init__(errorList["csvFileNotFound"]["message_template"].format(fileName=fileName),
                         errorList["csvFileNotFound"]["code"],
                         errorList["csvFileNotFound"]["func"])

class DownloadFailed(PwdlError):
    def __init__(self, name, id):
        super().__init__(errorList["downloadFailed"]["message_template"].format(name=name, id=id),
                         errorList["downloadFailed"]["code"],
                         errorList["downloadFailed"]["func"])

class CouldNotMakeDir(PwdlError):
    def __init__(self, dirName):
        super().__init__(errorList["couldNotMakeDir"]["message_template"].format(dirName=dirName),
                         errorList["couldNotMakeDir"]["code"],
                         errorList["couldNotMakeDir"]["func"])

class IdNotProvided(PwdlError):
    def __init__(self):
        super().__init__(errorList["idNotProvided"]["message_template"],
                         errorList["idNotProvided"]["code"],
                         errorList["idNotProvided"]["func"])

class TokenNotFound(PwdlError):
    def __init__(self):
        super().__init__(errorList["tokenNotFound"]["message_template"],
                         errorList["tokenNotFound"]["code"],
                         errorList["tokenNotFound"]["func"])

class TokenInvalid(PwdlError):
    def __init__(self):
        super().__init__(errorList["tokenInvalid"]["message_template"],
                         errorList["tokenInvalid"]["code"],
                         errorList["tokenInvalid"]["func"])

class OverwriteAbortedByUser(PwdlError):
    def __init__(self):
        super().__init__(errorList["overWriteAbortedByUser"]["message_template"],
                         errorList["overWriteAbortedByUser"]["code"],
                         errorList["overWriteAbortedByUser"]["func"])

class CantLoadFile(PwdlError):
    def __init__(self, fileName):
        super().__init__(errorList["cantLoadFile"]["message_template"].format(fileName=fileName),
                         errorList["cantLoadFile"]["code"],
                         errorList["cantLoadFile"]["func"])

class FlareNotStarted(PwdlError):
    def __init__(self):
        super().__init__(errorList["flareNotStarted"]["message_template"],
                         errorList["flareNotStarted"]["code"],
                         errorList["flareNotStarted"]["func"])

class RequestFailedDueToUnknownReason(PwdlError):
    def __init__(self, status_code):
        super().__init__(errorList["requestFailedDueToUnknownReason"]["message_template"].format(status_code=status_code),
                         errorList["requestFailedDueToUnknownReason"]["code"],
                         errorList["requestFailedDueToUnknownReason"]["func"])

class KeyExtractionFailed(PwdlError):
    def __init__(self, id):
        super().__init__(errorList["keyExtractionFailed"]["message_template"].format(id=id),
                         errorList["keyExtractionFailed"]["code"],
                         errorList["keyExtractionFailed"]["func"])

class KeyNotProvided(PwdlError):
    def __init__(self):
        super().__init__(errorList["keyNotProvided"]["message_template"],
                         errorList["keyNotProvided"]["code"],
                         errorList["keyNotProvided"]["func"])

class CouldNotDownloadAudio(PwdlError):
    def __init__(self, id):
        super().__init__(errorList["couldNotDownloadAudio"]["message_template"].format(id=id),
                         errorList["couldNotDownloadAudio"]["code"],
                         errorList["couldNotDownloadAudio"]["func"])

class CouldNotDownloadVideo(PwdlError):
    def __init__(self, id):
        super().__init__(errorList["couldNotDownloadVideo"]["message_template"].format(id=id),
                         errorList["couldNotDownloadVideo"]["code"],
                         errorList["couldNotDownloadVideo"]["func"])

class CouldNotDecryptAudio(PwdlError):
    def __init__(self):
        super().__init__(errorList["couldNotDecryptAudio"]["message_template"],
                         errorList["couldNotDecryptAudio"]["code"],
                         errorList["couldNotDecryptAudio"]["func"])

class CouldNotDecryptVideo(PwdlError):
    def __init__(self):
        super().__init__(errorList["couldNotDecryptVideo"]["message_template"],
                         errorList["couldNotDecryptVideo"]["code"],
                         errorList["couldNotDecryptVideo"]["func"])

class MethodPatched(PwdlError):
    def __init__(self):
        super().__init__(errorList["methodPatched"]["message_template"],
                         errorList["methodPatched"]["code"],
                         errorList["methodPatched"]["func"])

class CouldNotExtractKey(PwdlError):
    def __init__(self):
        super().__init__(errorList["couldNotExtractKey"]["message_template"],
                         errorList["couldNotExtractKey"]["code"],
                         errorList["couldNotExtractKey"]["func"])

class AdaptationSetIsNotVideo(PwdlError):
    def __init__(self):
        super().__init__(errorList["adaptationSetIsNotVideo"]["message_template"],
                         errorList["adaptationSetIsNotVideo"]["code"],
                         errorList["adaptationSetIsNotVideo"]["func"])

