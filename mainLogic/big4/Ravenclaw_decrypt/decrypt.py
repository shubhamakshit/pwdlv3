from mainLogic.error import CouldNotDecryptAudio, CouldNotDecryptVideo, CouldNotDownloadAudio, DependencyNotFound
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

    def decrypt(self,path,name,key,mp4d="mp4decrypt",out="None",outfile="",outdir="",verbose=True,suppress_exit=False):
        
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

        file = f'{"" if not outfile else outfile+"-" }{out}.mp4'

        file = os.path.join(
            outdir if outdir else path,
            file
        )

        _ = shell(mp4d)
        if  _ > 1 :
            debugger.error(f"{mp4d} failed with exit code {_}")
            debugger.error(DependencyNotFound("Mp4decrypt"))
            debugger.error(f'The code supplied {mp4d} does not exist. Please check your spelling and try again.')

        #decrypt_command = f'{mp4d} --key 1:{key} {path}/{name}.{extension} {file}'
        decrypt_command = [
            mp4d,
            "--key",
            "1:"+key,
            f"{path}/{name}.{extension}",
            file
        ]

        if verbose: debugger.debug(f"{out} Decryption Started..."); debugger.debug(f'{decrypt_command}')

        

        # the main part where the decryption happens

        code = shell(decrypt_command,verbose=True)

        # simple check to see if the decryption was successful or not
        if code == 0:
            debugger.debug(f"{out} Decrypted Successfully")
            return os.path.abspath(file)
        else:

            if os.path.exists(file):
                debugger.debug(f"Removing {file}...")
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
    def decryptAudio(self,path,name,key,mp4d="mp4decrypt",outfile='None',outdir=None,verbose=True,suppress_exit=False):
        return self.decrypt(path,name,key,mp4d,"Audio",outfile,outdir,verbose,suppress_exit=suppress_exit)

    # decrypts video
    def decryptVideo(self,path,name,key,mp4d="mp4decrypt",outfile='None',outdir=None,verbose=True,suppress_exit=False):
        return self.decrypt(path,name,key,mp4d,"Video",outfile,outdir,verbose,suppress_exit=suppress_exit)