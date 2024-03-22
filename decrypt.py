from glv import Global
from process import shell
from basicUtils import BasicUtils
import error 

class Decrypt:
    def decryptAudio(self,path,name,key,mp4d="mp4decrypt",verbose=True):
        
        path = BasicUtils.abspath(path)
        Global.dprint("Decrypting Audio...")

        if verbose: Global.dprint("Audio Decryption Started..."); Global.dprint(f'{mp4d} --key 1:{key} {path}/{name}.m4a {path}/audio.mp4')

        code = shell(f'{mp4d} --key 1:{key} {path}/{name}.m4a {path}/audio.mp4 ')
        if code == 0:
            Global.dprint("Audio Decrypted Successfully")
        else:
            if code == 1:
                code = shell(f'mp4decrypt --key 1:{key} {path}/{name}.en.m4a {path}/audio.mp4 ')
                if code == 0:
                    Global.dprint("Audio Decrypted Successfully")
                else:
                    error.errorList["couldNotDecryptAudio"]["func"]()
                    exit(error.errorList["couldNotDecryptAudio"]["code"])
        Global.hr()

    def decryptVideo(self,path,name,key,mp4d="mp4decrypt",verbose=True):
            
            path = BasicUtils.abspath(path)
            Global.dprint("Decrypting Video...")

            if verbose: Global.dprint("Video Decryption Started..."); Global.dprint(f'{mp4d} --key 1:{key} {path}/{name}.mp4 {path}/video.mp4')

            code = shell(f'{mp4d} --key 1:{key} {path}/{name}.mp4 {path}/video.mp4 ',r'^Decoding')
            if code == 0:
                Global.dprint("Video Decrypted Successfully")
            else:
                error.errorList["couldNotDecryptVideo"]["func"]()
                exit(error.errorList["couldNotDecryptVideo"]["code"])
            Global.hr()