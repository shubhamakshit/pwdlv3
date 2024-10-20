import os
from mainLogic.utils.glv import Global
class Clean:
    """
    Hufflepuff values hard work, patience, and dedication. Merging the audio and video files requires careful
    crafting, a trait that Hufflepuff embodies through its steadfast approach to completing tasks.
    """

    def removeFile(self,file,verbose):
        try:
            os.remove(file)
            if verbose: Global.sprint(f"Removed file: {file}")
        except:
            Global.errprint(f"Could not remove file: {file}")

    def remove(self,path,file,verbose=True):

        audio_enc = f"{path}/{file}-Audio-enc.mp4"
        video_enc = f"{path}/{file}-Video-enc.mp4"

        audio = f"{path}/{file}-Audio.mp4"
        video = f"{path}/{file}-Video.mp4"

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

        
