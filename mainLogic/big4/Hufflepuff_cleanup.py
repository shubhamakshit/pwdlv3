import os
from mainLogic.utils.glv import Global
from mainLogic.utils.glv_var import debugger


class Clean:
    """
    Hufflepuff values hard work, patience, and dedication. Merging the audio and video files requires careful
    crafting, a trait that Hufflepuff embodies through its steadfast approach to completing tasks.
    """

    def removeFile(self,file,verbose):
        from mainLogic.utils.glv_var import debugger
        try:
            os.remove(file)
            if verbose: debugger.success(f"Removed file: {file}")
        except:
            from mainLogic.utils.glv_var import debugger
            debugger.error(f"Could not remove file: {file}")

    def remove(self,path,file,verbose=True):

        audio_enc = f"{path}/{file}-Audio-enc.mp4"
        video_enc = f"{path}/{file}-Video-enc.mp4"

        audio = f"{path}/{file}-Audio.mp4"
        video = f"{path}/{file}-Video.mp4"

        if verbose:
            Global.hr()
            debugger.debug("Removing TemporaryDL Files...")
            Global.hr()

        if verbose: debugger.debug("Removing Audio...")    
        self.removeFile(audio_enc,verbose)

        if verbose: debugger.debug("Removing Video...")
        self.removeFile(video_enc,verbose)

        if verbose: debugger.debug("Removing Dncrypted Audio...")
        self.removeFile(audio,verbose)

        if verbose: debugger.debug("Removing Dncrypted Video...")
        self.removeFile(video,verbose)

        
