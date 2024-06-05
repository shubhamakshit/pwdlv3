import argparse
import shlex
from mainUtils.dl import DL
from startup.checkup import CheckState
from utils.glv import Global
from main import Main
from shellLogic import simpleParser


class HandleShellDL:

    def __init__(self):
        self.commandList = {
            "edl":{
                "func": self.edownload
            },
            "dl":{
                "func": self.download
            }
        }

    def edownload(self,args=[]):
        # print(args)
        if not args or len(args) < 2:
            print("Please provide a name and id")
            return

        name = args[0]
        id = args[1]

        dl = DL()
        ch =CheckState()
        prefs = ch.checkup(Global.EXECUTABLES,verbose=False)
        dl.downloadAudioAndVideo(name=name,
                                 id=id,
                                 directory='./',
                                 nm3Path=prefs['nm3'],
                                 verbose=False if not 'verbose' in prefs else prefs['verbose'],
                                 )

    def download(self,args=[]):
        if not args or len(args) < 2:
            print("Please provide a name and id")
            return

        name = args[0]
        id = args[1]

        ch = CheckState()
        prefs = ch.checkup(Global.EXECUTABLES,verbose=False)

        Main(id=id,
             name=name,
             directory='./',
             nm3Path=prefs['nm3'],
             mp4d=prefs['mp4decrypt'],
             ffmpeg=prefs['ffmpeg']
             ).process()



    def parseAndRun(self,command,args=[]):
        simpleParser.parseAndRun(self.commandList,command,args)

