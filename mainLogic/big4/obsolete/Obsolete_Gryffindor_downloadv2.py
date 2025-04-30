import re

from mainLogic.error import IdNotProvided
from mainLogic.utils.glv_var import debugger
from mainLogic.utils.process import shell
from mainLogic.utils.glv import Global


def download_color_function(text):
    # ANSI escape codes for colors
    RESET = "\033[0m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"

    # Example: colorize different parts of the output
    # This is a simple example; you can enhance it based on your needs.
    text = re.sub(r'(\d+(\.\d+)?) MiB', f'{GREEN}\\1 MiB{RESET}', text)
    text = re.sub(r'(\d+)%', f'{BLUE}\\1%{RESET}', text)
    text = re.sub(r'(\d+:\d+)', f'{MAGENTA}\\1{RESET}', text)

    return text


class Download:
    """
    Gryffindor is known for its courage, determination, and taking the first step towards any challenge. Here,
    downloading the files is like venturing into the unknown, just like a Gryffindor would bravely step forward to
    start the journey.
    """

    @staticmethod
    def buildUrl(id, signature, legacy=False):
        if legacy:
            if id is None:
                IdNotProvided().exit()

            url = f"https://d1d34p8vz63oiq.cloudfront.net/{id}/master.mpd"
            return url
        else:
            return f"{id}{signature}"

    def __init__(self,
                 vsd_path,
                 url,
                 name=None,
                 tmp_path="./",
                 output_path="./",
                 cookie=None,
                 color=True,
                 verbose=False,
                 progress_callback=None):
        self.vsd_path = vsd_path
        self.url = url
        self.name = name
        self.tmp_path = tmp_path + '/' + name
        self.output_path = output_path
        self.cookie = cookie
        self.color = color
        self.verbose = verbose
        self.progress_callback = progress_callback

        if verbose:
            Global.hr()
            debugger.success("Download initialized")

    def perform_cleanup(self):
        import shutil

        video_path = self.tmp_path + "/vsd_video_master_mpd.mp4"
        audio_path = self.tmp_path + "/vsd_audio_master_mpd.mp4"
        video_enc_path = self.output_path + '/' + self.name + "-Video-enc.mp4"
        audio_enc_path = self.output_path + '/' + self.name + "-Audio-enc.mp4"

        if self.verbose:
            debugger.debug(f"Performing cleanup, moving files to {self.output_path}")

        shutil.move(audio_path, video_enc_path)
        shutil.move(video_path, audio_enc_path)

        try:
            shutil.rmtree(self.tmp_path)
            if self.verbose:
                debugger.success(f"Removed temporary directory: {self.tmp_path}")
        except Exception as e:
            debugger.error(f"Could not remove tmp directory: {e}")

        return video_enc_path, audio_enc_path

    def download(self):
        """
        Download the video file from the given URL and save it to the output path.
        """
        # Debug info about the command being run
        command = [
            f"{self.vsd_path}",
            "save",
            f"{self.url}",
            "--skip-prompts",
            "--raw-prompts",
            "--no-decrypt",
            "--cookies",
            f"{self.cookie}",
            "-d",
            f'{self.tmp_path}',
            f"-t",
            f"10"
        ]

        if self.verbose:
            debugger.success(f"Running command: {' '.join(command)}")

        # Run the command with shell
        shell(
            command,
            verbose=self.verbose,
            filter=r"^\d+\.\d+ / \d+ MiB [╸━]+ \d+(\.\d+)?% •\s+\d+/\d+ • \d+:\d+ > \d+:\d+ • \d+(\.\d+)? SEG/s • .+$",
            color_function=download_color_function if self.color else None,
            progress_callback=self.progress_callback,
            handleProgress=self.handleDownloadProgress,
            inline_progress=True,
        )

        return self.perform_cleanup()

    def handleDownloadProgress(self, progress):
        """
        Handle the progress of the download process.
        """

        output = {
            "str": progress,
        }



        # Extract percentage from the progress string using regex and convert it to float
        pattern = r"(\d+(\.\d+)?)%"
        match = re.search(pattern, progress)
        if match:
            progress_f = float(match.group(1)) * 0.8
        else:
            progress_f = 0.0

        output["progress"] = progress_f

        return output
