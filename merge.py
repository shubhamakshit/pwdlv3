from process import shell
from glv import Global
class Merge:
    def ffmpegMerge(self,input1,input2,output,ffmpeg_path="ffmpeg",verbose=False):


        if verbose: Global.hr();Global.dprint('Attempting ffmpeg merge')
        if verbose: Global.dprint(f'{ffmpeg_path} -i {input1} -i {input2} -c copy {output}')

        shell(f'{ffmpeg_path} -i {input1} -i {input2} -c copy {output}',r'^\[out#0\/mp4')

        return output