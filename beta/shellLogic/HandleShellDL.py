from mainLogic.big4.downloadv2 import Download
from mainLogic.startup.checkup import CheckState
from mainLogic.utils.glv import Global
from mainLogic.main import Main
from beta.shellLogic import simpleParser
from mainLogic.utils import glv_var
from mainLogic import downloader


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

        ch =CheckState()
        state = ch.checkup(glv_var.EXECUTABLES,verbose=False)
        prefs = state['prefs']

        Download(
            vsd_path=prefs['vsd'],
            url=Download.buildUrl(id),
            name=name,
            tmp_path=prefs['tmpDir'],
            output_path=prefs['dir'],
        ).download()

    def download(self,args=[]):
        if not args or len(args) < 2:
            print("Please provide a name and id")
            return

        name = args[0]
        id = args[1]

        downloader.main(
            id=id,
            name=name,
        )





    def parseAndRun(self,command,args=[]):
        simpleParser.parseAndRun(self.commandList, command, args)

