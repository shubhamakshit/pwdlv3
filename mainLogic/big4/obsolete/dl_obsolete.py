import re

from mainLogic import error
from mainLogic.utils.process import shell
from mainLogic.utils.glv import Global
from mainLogic.utils.basicUtils import BasicUtils
class DL:

    @staticmethod
    def buildUrl(id):
        if id == None:
            error.errorList["idNotProvided"]["func"]()
            exit(error.errorList["idNotProvided"]["code"])

        return f"https://d1d34p8vz63oiq.cloudfront.net/{id}/master.mpd"
    
    def download(self,id,name=None,
                 type="",
                 directory="./",
                 tmpDir="/*auto*/",
                 nm3Path='nm3',
                 ffmpeg='ffmpeg',
                 verbose=True,
                 progress_callback=None):
        if id == None:
            error.errorList["idNotProvided"]["func"]()
            exit(error.errorList["idNotProvided"]["code"])

        if name == None: name = id
        

        url = DL.buildUrl(id)

        # setting identifier and filter based on type

        # identifier is used to identify the type of file
        identifier = "a" if type == "Audio" else "v" if type == "Video" else "av"

        # filter is used to filter the output of the shell command
        filter = r"^Aud" if type == "Audio" else r"^Vid" 

        # command to download the file
        command = f'{nm3Path} {url} --save-dir {directory} {"--tmp-dir "+tmpDir if not tmpDir == "/*auto*/" else "" } --save-name {name}  -s{identifier} best'
        if verbose: debugger.success(f"Command to download: {command}")

        # Download the audio file using the id
        code = shell(f'{command}',
                     filter=filter,
                     progress_callback=progress_callback,
                     handleProgress=self.handleDownloadProgress,
                     )

        if code == 0:
            return True
        else:
            error.errorList[f"couldNotDownload{type}"]["func"]()
            exit(error.errorList[f"couldNotDownload{type}"]["code"])

    def downloadAudioAndVideo(self,
                              id,
                              name=None,
                              directory="./",
                              tmpDir="/*auto*/",
                              nm3Path='nm3',
                              ffmpeg='ffmpeg',
                              verbose=True,
                              progress_callback=None):
        if id == None:
            error.errorList["idNotProvided"]["func"]()
            exit(error.errorList["idNotProvided"]["code"])

        if name == None: name = id; debugger.debug(f"Name not provided, using id as name: {name}")

        # removing limitations of relative path
        if not tmpDir == "/*auto*/": BasicUtils.abspath(tmpDir)
        directory = BasicUtils.abspath(directory)

        if verbose:
            Global.hr()
            debugger.debug(f"ID: {id}")
            debugger.debug(f"Name: {name}")
            debugger.debug(f"Directory: {directory}")
            debugger.debug(f"TmpDir: {tmpDir}")
            debugger.debug(f"Nm3Path: {nm3Path}")
            Global.hr()
            debugger.debug(f"Starting DL...")

        # section to download audio 
        Global.hr(); debugger.debug("Downloading Audio..."); Global.hr()
        self.dlAudio(id,
                     name,
                     directory,
                     tmpDir,
                     nm3Path,
                     verbose,
                     progress_callback=progress_callback)

        # section to download video
        Global.hr(); debugger.debug("Downloading Video..."); Global.hr()
        self.dlVideo(id,
                     name,
                     directory,
                     tmpDir,
                     nm3Path,
                     verbose,
                     progress_callback=progress_callback)

        if progress_callback:
            progress_callback({
                "progress": 80,
                "str": "download-completed",
                "next": "decryption"
            })

        # return the paths of the downloaded files
        return [f"{directory}/{name}.mp4",f"{directory}/{name}.m4a"]
    


    
    def dlAudio(self,id,name=None,directory="./",tmpDir="/*auto*/",nm3Path='nm3',verbose=True,progress_callback=None):
        self.download(id,
                      name,
                      "Audio",
                      directory,
                      tmpDir,
                      nm3Path,
                      verbose=verbose,
                      progress_callback=progress_callback)
        
    def dlVideo(self,id,name=None,directory="./",tmpDir="/*auto*/",nm3Path='nm3',verbose=True,progress_callback=None):
        self.download(id,
                      name,
                      "Video",
                      directory,
                      tmpDir,
                      nm3Path,
                      verbose=verbose,
                      progress_callback=progress_callback)
        

    def handleDownloadProgress(self,output):


        progress = {
            "str": output,
            "dl-progress": 0,
            "progress": 0,
            "next": "Aud"
        }

        # formats the output to get the progress
        pattern = re.compile(r"[0-9][0-9][0-9]?%")
        progress_percent = pattern.findall(output)

        if progress_percent:

            progress["dl-progress"] = int(progress_percent[0].replace("%",""))

            if "Aud" in output:
                progress["progress"] = progress["dl-progress"] * 0.4
                progress["next"] = "Vid"

            if "Vid" in output:
                progress["progress"] = progress["dl-progress"] * 0.4 + 40
                progress["next"] = "decryption"


        return progress






