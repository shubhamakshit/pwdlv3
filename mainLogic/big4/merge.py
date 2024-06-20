import os
from mainLogic.error import errorList
from mainLogic.utils.process import shell
from mainLogic.utils.glv import Global
class Merge:
    def ffmpegMerge(self,input1,input2,output,ffmpeg_path="ffmpeg",verbose=False):


        if verbose: Global.hr();Global.dprint('Attempting ffmpeg merge')
        if verbose: Global.dprint(f'{ffmpeg_path} -i {input1} -i {input2} -c copy {output}')

        if verbose:

            shell(f'{ffmpeg_path} -i {input1} -i {input2} -c copy {output}')

        else:

            if os.path.exists(output):

                Global.errprint("Warninbg: Output file already exists. Overwriting...")
                consent = input("Do you want to continue? (y/n): ")

                if consent.lower() != 'y':
                    errorList['overWriteAbortedByUser']['func']()
                    exit(errorList['overWriteAbortedByUser']['code'])

                else:
                    shell(f'{ffmpeg_path} -y -i {input1} -i {input2} -c copy {output}',stderr="",stdout="")

        return output