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
    
    def download(self,id,name=None,type="",directory="./",tmpDir="/*auto*/",nm3Path='nm3',ffmpeg='ffmpeg',verbose=True):
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
        if verbose: Global.sprint(f"Command to download: {command}")

        # Download the audio file using the id
        code = shell(f'{command}',filter)

        if code == 0:
            return True
        else:
            error.errorList[f"couldNotDownload{type}"]["func"]()
            exit(error.errorList[f"couldNotDownload{type}"]["code"])

    def downloadAudioAndVideo(self,id,name=None,directory="./",tmpDir="/*auto*/",nm3Path='nm3',ffmpeg='ffmpeg',verbose=True):
        if id == None:
            error.errorList["idNotProvided"]["func"]()
            exit(error.errorList["idNotProvided"]["code"])

        if name == None: name = id; Global.dprint(f"Name not provided, using id as name: {name}")

        # removing limitations of relative path
        if not tmpDir == "/*auto*/": BasicUtils.abspath(tmpDir)
        directory = BasicUtils.abspath(directory)

        if verbose:
            Global.hr()
            Global.dprint(f"ID: {id}")
            Global.dprint(f"Name: {name}")
            Global.dprint(f"Directory: {directory}")
            Global.dprint(f"TmpDir: {tmpDir}")
            Global.dprint(f"Nm3Path: {nm3Path}")
            Global.hr()
            Global.dprint(f"Starting DL...")

        # section to download audio 
        Global.hr(); Global.dprint("Downloading Audio..."); Global.hr()
        self.dlAudio(id,name,directory,tmpDir,nm3Path,verbose)

        # section to download video
        Global.hr(); Global.dprint("Downloading Video..."); Global.hr()
        self.dlVideo(id,name,directory,tmpDir,nm3Path,verbose)

        # return the paths of the downloaded files
        return [f"{directory}/{name}.mp4",f"{directory}/{name}.m4a"]
    


    
    def dlAudio(self,id,name=None,directory="./",tmpDir="/*auto*/",nm3Path='nm3',verbose=True):
        self.download(id,name,"Audio",directory,tmpDir,nm3Path,verbose=verbose)
        
    def dlVideo(self,id,name=None,directory="./",tmpDir="/*auto*/",nm3Path='nm3',verbose=True):
        self.download(id,name,"Video",directory,tmpDir,nm3Path,verbose=verbose)
        

