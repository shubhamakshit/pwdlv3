import os
from mainLogic.error import errorList, OverwriteAbortedByUser
from mainLogic.utils.glv_var import debugger
from mainLogic.utils.process import shell
from mainLogic.utils.glv import Global
from mainLogic.utils.os2 import SysFunc
class Merge:
    """
    Slytherin is known for resourcefulness and ambition, ensuring everything is left in a state that suits their
    needs. The cleanup phase is about efficiency, leaving no trace behind, just like a Slytherin covering their tracks.
    """

    def mergeCommandBuilder(self,ffmpeg_path,input1,input2,output,overwrite=False):

    #    return f'{ffmpeg_path} {"-y" if overwrite else ""} -i {input1} -i {input2} -c copy {output}'
        return [
            ffmpeg_path,
            "-y" if overwrite else "",
            "-i", input1,
            "-i", input2,
            "-c", "copy",
            output
        ]


    def ffmpegMerge(self,input1,input2,output,ffmpeg_path="ffmpeg",verbose=False):

        input1,input2,output = SysFunc.modify_path(input1),SysFunc.modify_path(input2),SysFunc.modify_path(output)

        if verbose: Global.hr();debugger.debug('Attempting ffmpeg merge')
        # if verbose: debugger.debug(f'{ffmpeg_path} -i {input1} -i {input2} -c copy {output}')

        if os.path.exists(output):

            debugger.error("Warninbg: Output file already exists. Overwriting...")
            consent = input("Do you want to continue? (y/n): ")

            if consent.lower() != 'y':
                OverwriteAbortedByUser().exit()

        if verbose:
            debugger.debug(f"Running: {self.mergeCommandBuilder(ffmpeg_path,input1,input2,output,overwrite=True)}")
            shell(self.mergeCommandBuilder(ffmpeg_path,input1,input2,output,overwrite=True),filter='.*')
        else:
            shell(self.mergeCommandBuilder(ffmpeg_path,input1,input2,output,overwrite=True), stderr="", stdout="")


        return output