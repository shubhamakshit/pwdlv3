from mainLogic.error import CouldNotDecryptAudio, CouldNotDecryptVideo, CouldNotDownloadAudio
from mainLogic.utils.glv import Global
from mainLogic.utils.glv_var import debugger
from mainLogic.utils.process import shell
from mainLogic.utils.basicUtils import BasicUtils
from mainLogic import error
import os

class Decrypt:
    """
    Ravenclaw represents wisdom, intellect, and problem-solving skills. Decrypting the files requires cleverness and
    understanding, much like a Ravenclaw unraveling the mysteries and hidden secrets.
    """

    def decrypt(self,path,name,key,mp4d="mp4decrypt",out="None",outfile="",verbose=True,suppress_exit=False):
        
        Global.hr()

        # making path absolute if not already absolute
        path = BasicUtils.abspath(path)
        debugger.debug(f"Decrypting {out}...")

        # during various tests
        # it was found that the decrypted audio file is named as <name>.en.m4a 
        # hence a simple logic to work around this issue is to check if the file exists
        # if not os.path.exists(f'{path}/{name}.m4a') and out == "Audio":
        #     name = name + ".en"

        # setting extension based on out
        # i.e if out is Audio then extension is 'm4a' else 'mp4'
        # extension = "m4a" if out == "Audio" else "mp4"
        extension = "mp4" # temporary fix

        decrypt_command = f'{mp4d} --key 1:{key} {path}/{name}.{extension} {path}/{"" if not outfile else outfile+"-" }{out}.mp4'

        if verbose: debugger.debug(f"{out} Decryption Started..."); debugger.debug(f'{decrypt_command}')

        

        # the main part where the decryption happens
        code = shell(f'{decrypt_command}',stderr="",stdout="")

        # simple check to see if the decryption was successful or not
        if code == 0:
            debugger.debug(f"{out} Decrypted Successfully")
        else:

            # if decryption failed then print error message and exit
            if out == "Audio":
                debugger.error(CouldNotDecryptAudio())
            else:
                debugger.error(CouldNotDecryptVideo())

            if not suppress_exit:

                if out == "Audio":
                    CouldNotDecryptAudio().exit()
                else:
                    CouldNotDecryptVideo().exit()

        

    # decrypts audio
    def decryptAudio(self,path,name,key,mp4d="mp4decrypt",outfile='None',verbose=True,suppress_exit=False):
        self.decrypt(path,name,key,mp4d,"Audio",outfile,verbose,suppress_exit=suppress_exit)

    # decrypts video
    def decryptVideo(self,path,name,key,mp4d="mp4decrypt",outfile='None',verbose=True,suppress_exit=False):
        self.decrypt(path,name,key,mp4d,"Video",outfile,verbose,suppress_exit=suppress_exit)