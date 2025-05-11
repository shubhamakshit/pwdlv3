from mainLogic.big4.Gryffindor_downloadv3 import DownloaderV3
from mainLogic.utils.basicUtils import BasicUtils
from mainLogic.utils.glv_var import debugger
from mainLogic.utils.os2 import SysFunc
from mainLogic.big4.Hufflepuff_cleanup import Clean
from mainLogic.big4.Ravenclaw_decrypt.key import LicenseKeyFetcher
from mainLogic.big4.Ravenclaw_decrypt.decrypt import Decrypt
from mainLogic.big4.Slytherin_merge import Merge
import os

from mainLogic.utils.MPDParser import MPDParser


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
        token (str): Auth Token for the process.
        verbose (bool): Flag for verbose output. Defaults to True.
        suppress_exit (bool): Flag to suppress exit on error. Defaults to False.
        progress_callback (function): Callback function to report progress. Defaults to None.
    """

    def __init__(self,
                 id,
                 name=None,
                 batch_name=None,
                 topic_name=None,
                 lecture_url=None,
                 directory="./",
                 tmpDir="/*auto*/",
                 vsdPath='nm3',
                 ffmpeg="ffmpeg",
                 mp4d="mp4decrypt",
                 tui=True,
                 token=None, random_id=None, verbose=True, suppress_exit=False, progress_callback=None):

        os2 = SysFunc()

        self.id = id
        self.name = name if name else id
        self.batch_name = batch_name
        self.topic_name = topic_name
        self.lecture_url = lecture_url
        self.directory = directory if directory else "./"
        self.tmpDir = BasicUtils.abspath(tmpDir) if tmpDir != '/*auto*/' else BasicUtils.abspath('./tmp/')

        # Create tmp directory if it does not exist
        try:
            os2.create_dir(self.tmpDir, verbose=verbose)
        except Exception as e:
            if verbose:
                debugger.error(f"Error creating tmp directory: {e}")
                self.tmpDir = "./"

        self.vsd = vsdPath if vsdPath != 'vsd' else 'vsd'
        self.ffmpeg = BasicUtils.abspath(ffmpeg) if ffmpeg != 'ffmpeg' else 'ffmpeg'
        self.mp4d = BasicUtils.abspath(mp4d) if mp4d != 'mp4decrypt' else 'mp4decrypt'
        self.tui = tui

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
            debugger.debug("Starting Main Process... for ID: " + self.id)

        TOKEN = self.token
        RANDOM_ID = self.random_id
        fetcher = LicenseKeyFetcher(TOKEN, RANDOM_ID)
        try:
            if self.verbose: debugger.debug(f"Fetching License Key for ID: {self.id} and Batch Name: {self.batch_name}")
            if self.verbose and self.topic_name:
                debugger.debug(f"Fetching License Key for Topic Name: {self.topic_name} and Lecture URL: {self.lecture_url}")
            key = fetcher.get_key(
                id=self.id,batch_name=self.batch_name,khazana_topic_name=self.topic_name,khazana_url=self.lecture_url,
                verbose=self.verbose)[1]
            cookies = fetcher.cookies
        except Exception as e:
            raise TypeError(f"ID is invalid (if the token is valid) ")

        urls = MPDParser(fetcher.url).pre_process().parse().get_segment_urls()

        # 1. Downloading Files (New Download Method using VSD)

        download_out_dir = os.path.join(self.tmpDir, self.id)

        downloader = DownloaderV3(
            tmp_dir=self.tmpDir,
            out_dir=download_out_dir,
            verbose=self.verbose,
            progress_callback=self.progress_callback,
            show_progress_bar=True,
            max_workers=16,
            audio_dir="audio",
            video_dir="video",
        )

        from tui import update_downloader_v3_with_tui

        if self.tui:
            downloader = update_downloader_v3_with_tui(downloader)
        results = downloader.download_all(urls)


        for media_type, result in results.items():
            debugger.info(f"\n{media_type.upper()} Download Summary:")
            debugger.info(f"Init file: {result.init_file}")
            debugger.info(f"Segments directory: {result.segments_dir}")
            debugger.info(f"Total segments: {result.total_segments}")
            debugger.info(f"Successfully downloaded: {result.successful_segments}")
            debugger.info(f"Failed segments: {result.failed_segments}")
            results[media_type].encoded_file = SysFunc.concatenate_mp4_segments(str(result.segments_dir),output_filename=f"{self.name}-{media_type.title()}-enc.mp4",cleanup=True)


        audio = results["audio"].encoded_file
        video = results["video"].encoded_file


        debugger.success("Download completed.")
        if self.verbose: debugger.success(f"Audio: {audio}\nVideo: {video}")



        # 2. Decrypting Files

        debugger.success("Please wait while we Ravenclaw_decrypt the files...")

        decrypt = Decrypt()

        decrypted_audio = decrypt.decryptAudio(
            results["audio"].segments_dir,
            f'{self.name}-Audio-enc',
            key, mp4d=self.mp4d, outfile=self.name,outdir=self.directory,
            verbose=self.verbose, suppress_exit=self.suppress_exit)


        decrypted_video = decrypt.decryptVideo(
            results["video"].segments_dir,
            f'{self.name}-Video-enc',
            key, mp4d=self.mp4d, outfile=self.name,outdir=self.directory,
            verbose=self.verbose, suppress_exit=self.suppress_exit)

        # Call the progress callback for decryption completion
        # if self.progress_callback:
        #     self.progress_callback({
        #         "progress": 90,
        #         "str": "decryption-completed",
        #         "next": "merging"
        #     })

        if self.verbose:
            debugger.success(f"Audio file: {decrypted_audio}")
            debugger.success(f"Video file: {decrypted_video}")

        # 3. Merging Files

        #Move files form download_out_dir/<media_type>/{self.name}-<media_type.title()>.mp4 to out dir
        try:
            import shutil
            #shutil.move(decrypted_audio, self.directory)
            #shutil.move(decrypted_video, self.directory)

            if self.verbose:
                debugger.info(f"Now removing ")
            shutil.rmtree(download_out_dir, ignore_errors=True)
        except Exception as e:
            debugger.error(f"Failed to remove temp dir {download_out_dir}")


        merge = Merge()
        merge.ffmpegMerge(f"{self.directory}/{self.name}-Video.mp4",
                          f"{self.directory}/{self.name}-Audio.mp4",
                          f"{self.directory}/{self.name}.mp4",
                          ffmpeg_path=self.ffmpeg, verbose=self.verbose)

        # Call the progress callback for merge completion
        # if self.progress_callback:
        #     self.progress_callback({
        #         "progress": 99,
        #         "str": "merge-completed",
        #         "next": "cleanup"
        #     })

        # 4. Cleanup
        clean = Clean()
        clean.remove(self.directory, f'{self.name}', self.verbose)

        # if self.progress_callback:
        #     self.progress_callback({
        #         "progress": 100,
        #         "str": "cleanup-completed",
        #         "next": "done"
        #     })
