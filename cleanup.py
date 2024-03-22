import os
from glv import Global
class Clean:

    def removeFile(self,file,verbose):
        try:
            os.remove(file)
            if verbose: Global.sprint(f"Removed file: {file}")
        except:
            Global.errprint(f"Could not remove file: {file}")

    def remove(self,path,file,verbose=True):

        audio_enc = f"{path}/{file}-enc.m4a" if os.path.exists(f"{path}/{file}-enc.m4a") else f"{path}/{file}-enc.en.m4a"
        video_enc = f"{path}/{file}-enc.mp4"

        audio = f"{path}/audio.mp4"
        video = f"{path}/video.mp4"

        if verbose:
            Global.hr()
            Global.dprint("Removing TemporaryDL Files...")
            Global.hr()

        if verbose: Global.dprint("Removing Audio...")    
        self.removeFile(audio_enc,verbose)

        if verbose: Global.dprint("Removing Video...")
        self.removeFile(video_enc,verbose)

        if verbose: Global.dprint("Removing Dncrypted Audio...")
        self.removeFile(audio,verbose)

        if verbose: Global.dprint("Removing Dncrypted Video...")
        self.removeFile(video,verbose)

        
