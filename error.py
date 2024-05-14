from utils.glv import Global

errorList = {
    "noError": {
        "code": 0,
        "func": lambda: None,
    },
    "defaultsNotFound"  : {
        "code": 1,
        "func": lambda: Global.errprint("defaults.json not found. Exiting..."),
    },
    "dependencyNotFound": {
        "code": 2,
        "func": lambda x=None: Global.errprint(f"{'Dependency' if x == None else x } not found. Exiting..."),
    },
    "dependencyNotFoundInPrefs":
    {
        "code": 3,
        "func": lambda x=None: Global.errprint(f"{'Dependency' if x == None else x } not found in default settings. Exiting..."),
    },
    "csvFileNotFound": {
        "code": 4,
        "func": lambda fileName: Global.errprint(f"CSV file {fileName} not found. Exiting..."),
    },
    "downloadFailed": {
        "code": 5,
        "func": lambda name, id: Global.errprint(f"Download failed for {name} with id {id}. Exiting..."),
    },
    "cantLoadFile": {
        "code": 22,
        "func": lambda fileName: Global.errprint(f"Can't load file {fileName}"),
    },
    "flareNotStarted": {
        "code": 23,
        "func": lambda: Global.errprint("Flare is not started. Start the flare server first.")
    },
    "requestFailedDueToUnknownReason": {
        "code": 24,
        "func": lambda status_code: Global.errprint("Request failed due to unknown reason. Status Code: " + str(status_code))
    },
    "keyExtractionFailed": {
        "code": 25,
        "func": lambda id: Global.errprint(f"Key extraction failed for id -> {id}. Exiting...")
    },
    "keyNotProvided": {
        "code": 26,
        "func": lambda: Global.errprint("Key not provided. Exiting...")
    },
    "couldNotDownloadAudio": {
        "code": 27,
        "func": lambda id: Global.errprint(f"Could not download audio for id -> {id} Exiting...")
    },
    "couldNotDownloadVideo": {
        "code": 28,
        "func": lambda: Global.errprint(f"Could not download video for {id} Exiting...")
    },
    "couldNotDecryptAudio": {
        "code": 29,
        "func": lambda: Global.errprint("Could not decrypt audio. Exiting...")
    },
    "couldNotDecryptVideo": {
        "code": 30,
        "func": lambda: Global.errprint("Could not decrypt video. Exiting...")
    },
    "methodPatched": {
        "code": 31,
        "func": lambda: Global.errprint("Method is patched. Exiting...")
    },
    "couldNotExtractKey": {
        "code": 32,
        "func": lambda: Global.errprint("Could not extract key. Exiting...")
    },
}

