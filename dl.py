import error
from process import shell
from glv import Global
from basicUtils import BasicUtils
class DL:

    def buildUrl(self,id):
        if id == None:
            error.errorList["idNotProvided"]["func"]()
            exit(error.errorList["idNotProvided"]["code"])

        return f"https://d1d34p8vz63oiq.cloudfront.net/{id}/master.mpd"

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

        Global.hr(); Global.dprint("Downloading Audio..."); Global.hr()
        self.dlAudio(id,name,directory,tmpDir,nm3Path)

        Global.hr(); Global.dprint("Downloading Video..."); Global.hr()
        self.dlVideo(id,name,directory,tmpDir,nm3Path)
        return [f"{directory}/{name}.mp4",f"{directory}/{name}.m4a"]
    
    def dlAudio(self,id,name=None,directory="./",tmpDir="/*auto*/",nm3Path='nm3'):
        
        if id == None:
            error.errorList["idNotProvided"]["func"]()
            exit(error.errorList["idNotProvided"]["code"])

        if name == None: name = id
        

        url = self.buildUrl(id)

        # Download the audio file using the id
        code = shell(f'{nm3Path} {url} --save-dir {directory} {"--tmp-dir"+tmpDir if tmpDir != '/*auto*/' else '' } --save-name {name}  -sa best',r'^Aud')

        if code == 0:
            return True
        else:
            error.errorList["couldNotDownloadAudio"]["func"]()
            exit(error.errorList["couldNotDownloadAudio"]["code"])


    def dlVideo(self,id,name=None,directory="./",tmpDir="/*auto*/",nm3Path='nm3'):
        
        if id == None:
            error.errorList["idNotProvided"]["func"]()
            exit(error.errorList["idNotProvided"]["code"])

        if name == None: name = id
        

        url = self.buildUrl(id)

        # Download the video file using the id
        code = shell(f'{nm3Path} {url} --save-dir {directory} {"--tmp-dir"+tmpDir if tmpDir != '/*auto*/' else '' } --save-name {name}  -sv best',r'^Vid')

        if code == 0:
            return True
        else:
            error.errorList["couldNotDownloadVideo"]["func"]()
            exit(error.errorList["couldNotDownloadVideo"]["code"])
        

