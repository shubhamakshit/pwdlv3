from beta.shellLogic.Plugin import Plugin
from mainLogic.big4.Ravenclaw_decrypt.key import LicenseKeyFetcher
from mainLogic.big4.obsolete.Obsolete_Gryffindor_downloadv2 import Download
from mainLogic.startup.checkup import CheckState
from mainLogic.utils import glv_var
from mainLogic import downloader


class HandleShellDL(Plugin):
    def __init__(self):
        super().__init__()
        self.commandList = {
            "edl": {
                "desc": "Enhanced download with name and ID",
                "regex": r"edl",
                "func": self.edownload
            },
            "dl": {
                "desc": "Download with name and ID",
                "regex": r"dl",
                "func": self.download
            }
        }
        self.register_commands()

    def edownload(self, args=[]):
        """
        Performs an enhanced download using the provided name and ID.
        """
        if not args or len(args) < 2:
            print("Please provide a name and id")
            return

        name = args[0]
        id = args[1]

        ch = CheckState()
        state = ch.checkup(glv_var.EXECUTABLES, verbose=False)
        prefs = state['prefs']

        token = prefs['token']
        random_id = prefs['random_id']

        fetcher = LicenseKeyFetcher(token, random_id)
        fetcher.get_key(id)

        url = fetcher.url
        cookies = fetcher.cookies


        Download(
            vsd_path=prefs['vsd'],
            url=url,
            name=name,
            cookie=cookies,
            tmp_path=prefs['tmpDir'],
            output_path=prefs['dir'],
        ).download()

    def download(self, args=[]):
        """
        Performs a basic download using the provided name and ID.
        """
        if not args or len(args) < 2:
            print("Please provide a name and id")
            return

        name = args[0]
        id = args[1]

        downloader.main(
            id=id,
            name=name,
        )
