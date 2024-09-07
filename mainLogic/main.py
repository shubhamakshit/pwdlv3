from mainLogic.utils.basicUtils import BasicUtils
from mainLogic.utils.os2 import SysFunc
from mainLogic.utils.glv import Global
from mainLogic.big4.cleanup import Clean
from mainLogic.big4.decrypt.key import LicenseKeyFetcher
from mainLogic.big4.downloadv2 import Download
from mainLogic.big4.decrypt.decrypt import Decrypt
from mainLogic.big4.merge import Merge
import os


class Main:
    """
    Main class to handle the processing of video and audio files including download,
    decryption, merging, and cleanup.

    Attributes:
        id (str): Identifier for the process.
        name (str): Name for the process. Defaults to the value of `id`.
        directory (str): Directory to store the files. Defaults to "./".
        tmpDir (str): Temporary directory for intermediate files. Defaults to './tmp/'.
        vsdPath (str): Path to the vsd binary. Defaults to 'vsd'.
        ffmpeg (str): Path to the ffmpeg binary. Defaults to 'ffmpeg'.
        mp4d (str): Path to the mp4decrypt binary. Defaults to 'mp4decrypt'.
        token (str): Auth Token for the process.
        verbose (bool): Flag for verbose output. Defaults to True.
        suppress_exit (bool): Flag to suppress exit on error. Defaults to False.
        progress_callback (function): Callback function to report progress. Defaults to None.
    """

    def __init__(self,
                 id,
                 name=None,
                 directory="./",
                 tmpDir="/*auto*/",
                 vsdPath='nm3',
                 ffmpeg="ffmpeg",
                 mp4d="mp4decrypt",
                 color=True,
                 token=None, random_id=None, verbose=True, suppress_exit=False, progress_callback=None):

        os2 = SysFunc()

        self.id = id
        self.name = name if name else id
        self.directory = directory
        self.tmpDir = BasicUtils.abspath(tmpDir) if tmpDir != '/*auto*/' else BasicUtils.abspath('./tmp/')

        # Create tmp directory if it does not exist
        os2.create_dir(self.tmpDir, verbose=verbose)

        self.vsd = vsdPath if vsdPath != 'vsd' else 'vsd'
        self.ffmpeg = BasicUtils.abspath(ffmpeg) if ffmpeg != 'ffmpeg' else 'ffmpeg'
        self.mp4d = BasicUtils.abspath(mp4d) if mp4d != 'mp4decrypt' else 'mp4decrypt'
        self.color = color

        self.token = token
        self.random_id = random_id
        self.verbose = verbose
        self.suppress_exit = suppress_exit
        self.progress_callback = progress_callback

    def process(self):
        """
        Main processing function to handle downloading, decrypting, merging, and cleanup of files.
        """

        if self.verbose:
            Global.dprint("Starting Main Process... for ID: " + self.id)

        TOKEN = self.token
        RANDOM_ID = self.random_id
        fetcher = LicenseKeyFetcher(TOKEN, RANDOM_ID)
        try:
            key = fetcher.get_key(self.id, verbose=self.verbose)[1]
            cookies = fetcher.cookies
        except Exception as e:
            raise TypeError(f"ID is invalid (if the token is valid) ")


        # 1. Downloading Files (New Download Method using VSD)

        audio, video = Download(self.vsd,
                                fetcher.url,
                                self.name,
                                self.tmpDir,
                                self.directory,
                                cookie=fetcher.cookies,
                                color=self.color,
                                verbose=self.verbose,
                                progress_callback=self.progress_callback).download()

        Global.sprint("Download completed.")
        if self.verbose: Global.sprint(f"Audio: {audio}\nVideo: {video}")

        # 2. Decrypting Files

        Global.sprint("Please wait while we decrypt the files...")

        decrypt = Decrypt()

        decrypt.decryptAudio(self.directory, f'{self.name}-Audio-enc', key, mp4d=self.mp4d, outfile=self.name,
                             verbose=self.verbose, suppress_exit=self.suppress_exit)
        decrypt.decryptVideo(self.directory, f'{self.name}-Video-enc', key, mp4d=self.mp4d, outfile=self.name,
                             verbose=self.verbose, suppress_exit=self.suppress_exit)

        # Call the progress callback for decryption completion
        if self.progress_callback:
            self.progress_callback({
                "progress": 90,
                "str": "decryption-completed",
                "next": "merging"
            })

        # 3. Merging Files

        merge = Merge()
        merge.ffmpegMerge(f"{self.directory}/{self.name}-Video.mp4",
                          f"{self.directory}/{self.name}-Audio.mp4",
                          f"{self.directory}/{self.name}.mp4",
                          ffmpeg_path=self.ffmpeg, verbose=self.verbose)

        # Call the progress callback for merge completion
        if self.progress_callback:
            self.progress_callback({
                "progress": 99,
                "str": "merge-completed",
                "next": "cleanup"
            })

        # 4. Cleanup
        clean = Clean()
        clean.remove(self.directory, f'{self.name}', self.verbose)

        if self.progress_callback:
            self.progress_callback({
                "progress": 100,
                "str": "cleanup-completed",
                "next": "done"
            })
