from mainLogic.utils.basicUtils import BasicUtils
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
        nm3Path (str): Path to the NM3 binary. Defaults to 'nm3'.
        ffmpeg (str): Path to the ffmpeg binary. Defaults to 'ffmpeg'.
        mp4d (str): Path to the mp4decrypt binary. Defaults to 'mp4decrypt'.
        flare_url (str): URL for the flare service. Defaults to 'http://localhost:8191/v1'.
        verbose (bool): Flag for verbose output. Defaults to True.
        suppress_exit (bool): Flag to suppress exit on error. Defaults to False.
    """

    def __init__(self, id, name=None, directory="./", tmpDir="/*auto*/", vsdPath='nm3', ffmpeg="ffmpeg",
                 mp4d="mp4decrypt", token=None, verbose=True, suppress_exit=False, progress_callback=None):
        """
        Initialize the Main class with the given parameters.

        Args:
            id (str): Identifier for the process.
            name (str, optional): Name for the process. Defaults to None.
            directory (str, optional): Directory to store the files. Defaults to "./".
            tmpDir (str, optional): Temporary directory for intermediate files. Defaults to '/*auto*/'.
            nm3Path (str, optional): Path to the NM3 binary. Defaults to 'nm3'.
            ffmpeg (str, optional): Path to the ffmpeg binary. Defaults to 'ffmpeg'.
            mp4d (str, optional): Path to the mp4decrypt binary. Defaults to 'mp4decrypt'.
            # flare_url (str, optional): URL for the flare service. Defaults to 'http://localhost:8191/v1'.
            verbose (bool, optional): Flag for verbose output. Defaults to True.
            suppress_exit (bool, optional): Flag to suppress exit on error. Defaults to False.
            progress_callback (function, optional): Callback function to report progress. Defaults to None.
        """
        self.id = id
        self.name = name if name else id
        self.directory = directory
        self.tmpDir = BasicUtils.abspath(tmpDir) if tmpDir != '/*auto*/' else BasicUtils.abspath('./tmp/')
        # Create tmp directory if it does not exist
        try:
            if not os.path.exists(self.tmpDir):
                os.makedirs(self.tmpDir)
        except:
            Global.errprint("Could not create tmp directory")
            exit(-1)
        # self.nm3Path = BasicUtils.abspath(nm3Path) if nm3Path != 'nm3' else 'nm3'
        self.vsd = vsdPath
        self.ffmpeg = BasicUtils.abspath(ffmpeg) if ffmpeg != 'ffmpeg' else 'ffmpeg'
        self.mp4d = BasicUtils.abspath(mp4d) if mp4d != 'mp4decrypt' else 'mp4decrypt'
        self.token = token
        self.verbose = verbose
        self.suppress_exit = suppress_exit
        self.progress_callback = progress_callback

    def process(self):
        """
        Main processing function to handle downloading, decrypting, merging, and cleanup of files.
        """

        if self.verbose:
            Global.dprint("Starting Main Process... for ID: " + self.id)

        # 1. Downloading Files (New Download Method using VSD)

        audio, video = Download(self.vsd,
                                Download.buildUrl(self.id),
                                self.name,
                                self.tmpDir,
                                self.directory,
                                progress_callback=self.progress_callback).download()

        # dl = DL()
        # audio, video = dl.downloadAudioAndVideo(self.id, f'{self.name}-enc', self.directory, self.tmpDir, self.nm3Path,
        #                                         self.ffmpeg, self.verbose, progress_callback=self.progress_callback)

        # 2. Decrypting Files

        Global.sprint("Please wait while we decrypt the files...\nFetching key may take some time.")

        TOKEN = self.token
        fetcher = LicenseKeyFetcher(TOKEN)

        key = fetcher.get_key(self.id, verbose=self.verbose)[1]

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
        merge.ffmpegMerge(f"{self.directory}/{self.name}-Video.mp4", f"{self.directory}/{self.name}-Audio.mp4",
                          f"{self.directory}/{self.name}.mp4", ffmpeg_path=self.ffmpeg, verbose=self.verbose)

        # Call the progress callback for merge completion
        if self.progress_callback:
            self.progress_callback({
                "progress": 100,
                "str": "merge-completed",
                "next": "cleanup"
            })

        # 4. Cleanup
        clean = Clean()
        clean.remove(self.directory, f'{self.name}', self.verbose)
