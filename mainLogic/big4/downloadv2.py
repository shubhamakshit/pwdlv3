import re

from mainLogic import error
from mainLogic.utils.process import shell
from mainLogic.utils.glv import Global


class Download:

    @staticmethod
    def buildUrl(id):
        if id == None:
            error.errorList["idNotProvided"]["func"]()
            exit(error.errorList["idNotProvided"]["code"])

        return f"https://d1d34p8vz63oiq.cloudfront.net/{id}/master.mpd"

    def __init__(self,
                 vsd_path,
                 url,
                 name=None,
                 tmp_path="./",
                 output_path="./",
                 progress_callback=None
                 ):
        self.vsd_path = vsd_path
        self.url = url
        self.name = name
        self.tmp_path = tmp_path + '/' + name
        self.output_path = output_path
        self.progress_callback = progress_callback

    def perform_cleanup(self):

        import shutil

        shutil.move(self.tmp_path + "/vsd_audio_master_mpd.mp4", self.output_path + '/' + self.name + "-Video-enc.mp4")
        shutil.move(self.tmp_path + "/vsd_video_master_mpd.mp4", self.output_path + '/' + self.name + "-Audio-enc.mp4")

        try:
            shutil.rmtree(self.tmp_path)
        except Exception as e:
            Global.errprint(f"Could not remove tmp directory : {e}")

        return (
        self.output_path + '/' + self.name + "-Video-enc.mp4", self.output_path + '/' + self.name + "-Audio-enc.mp4")

    def download(self):
        """
        Download the video file from the given URL and save it to the output path.
        """
        # Download the video file
        # Save the video file to the output path
        shell([
            f"{self.vsd_path}",
            "save",
            f"{self.url}",
            "--skip-prompts",
            "--raw-prompts",
            "-t",
            "16",
            "--no-decrypt",
            "-d",
            f'{self.tmp_path}'],
            filter=r"^\d+\.\d+ / \d+ MiB [╸━]+ \d+(\.\d+)?% •\s+\d+/\d+ • \d+:\d+ > \d+:\d+ • \d+(\.\d+)? SEG/s • .+$",
            progress_callback=self.progress_callback,
            handleProgress=self.handleDownloadProgress,
            inline_progress=True,

        )

        return self.perform_cleanup()

    def handleDownloadProgress(self, progress):
        """
        Handle the progress of the download process.
        """

        # extract percentage from the progress string (using) regex
        # and convert it to float

        output = {
            "str": progress,

        }

        pattern = r"(\d+(\.\d+)?)%"
        match = re.search(pattern, progress)
        if match:
            progress_f = float(match.group(1)) * 0.8
        else:
            progress_f = 0.0

        output["progress"] = progress_f

        return output
