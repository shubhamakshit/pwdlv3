class Merge:
    def ffmpegMerge(self,input1,input2,output,ffmpeg_path="ffmpeg"):
        import os
        os.system(f'{ffmpeg_path} -i {input1} -i {input2} -c copy {output}')
        return output