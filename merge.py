from process import shell
class Merge:
    def ffmpegMerge(self,input1,input2,output,ffmpeg_path="ffmpeg"):

        shell(f'{ffmpeg_path} -i {input1} -i {input2} -c copy {output}',r'^\[out#0\/mp4')
        return output