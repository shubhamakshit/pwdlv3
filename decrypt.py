from glv import Global
from process import shell
from basicUtils import BasicUtils
import error 
import os

class Decrypt:

    def decrypt(self,path,name,key,mp4d="mp4decrypt",out="None",verbose=True):

        # making path absolute if not already absolute
        path = BasicUtils.abspath(path)
        Global.dprint(f"Decrypting {out}...")

        # during various tests
        # it was found that the decrypted audio file is named as <name>.en.m4a 
        # hence a simple logic to work around this issue is to check if the file exists
        if not os.path.exists(f'{path}/{name}.m4a') and out == "Audio":
            name = name + ".en"

        # setting extension based on out
        # i.e if out is Audio then extension is 'm4a' else 'mp4'
        extension = "m4a" if out == "Audio" else "mp4"

        decrypt_command = f'{mp4d} --key 1:{key} {path}/{name}.{extension} {path}/{out}.mp4'

        if verbose: Global.dprint(f"{out} Decryption Started..."); Global.dprint(f'{decrypt_command}')

        

        # the main part where the decryption happens
        code = shell(f'{decrypt_command}',stderr="",stdout="")

        # simple check to see if the decryption was successful or not
        if code == 0:
            Global.dprint(f"{out} Decrypted Successfully")
        else:

            # if decryption failed then print error message and exit
            error.errorList[f"couldNotDecrypt{out}"]["func"]()
            exit(error.errorList[f"couldNotDecrypt{out}"]["code"])

        Global.hr()

    # decrypts audio
    def decryptAudio(self,path,name,key,mp4d="mp4decrypt",verbose=True):
        self.decrypt(path,name,key,mp4d,"Audio",verbose)

    # decrypts video
    def decryptVideo(self,path,name,key,mp4d="mp4decrypt",verbose=True):
        self.decrypt(path,name,key,mp4d,"Video",verbose)