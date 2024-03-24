from basicUtils import BasicUtils
from glv import Global
from cleanup import Clean
import os
class Main:
    def __init__(self,id,name=None,directory="./",tmpDir="/*auto*/",nm3Path='nm3',ffmpeg="ffmpeg",mp4d="mp4decrypt",verbose=True):
        self.id = id
        self.name = name if name else id
        self.directory = directory
        self.tmpDir = BasicUtils.abspath(tmpDir) if tmpDir != '/*auto*/' else BasicUtils.abspath('./tmp/')
        # craete tmp directory if it does not exist
        try:
            if not os.path.exists(self.tmpDir):
                os.makedirs(self.tmpDir)
        except:
            Global.errprint("Could not create tmp directory")
            exit(-1)
        self.nm3Path = BasicUtils.abspath(nm3Path) if nm3Path != 'nm3' else 'nm3'
        self.ffmpeg = BasicUtils.abspath(ffmpeg) if ffmpeg != 'ffmpeg' else 'ffmpeg'
        self.mp4d = BasicUtils.abspath(mp4d) if mp4d != 'mp4decrypt' else 'mp4decrypt'
        self.verbose = verbose

        if self.verbose:
            Global.hr()
            Global.dprint(f"ID: {self.id}")
            Global.dprint(f"Name: {self.name}")
            Global.dprint(f"Directory: {self.directory}")
            Global.dprint(f"TmpDir: {self.tmpDir}")
            Global.dprint(f"Nm3Path: {self.nm3Path}")
            Global.dprint(f"FFmpeg: {self.ffmpeg}")
            Global.dprint(f"MP4Decrypt: {self.mp4d}")
            Global.hr()
    
    def process(self):

        if self.verbose:
            Global.dprint("Starting Main Process... for ID: "+self.id)
        # 1. Downloadig Files
        import dl
        dl = dl.DL()
        audio , video = dl.downloadAudioAndVideo(self.id,f'{self.name}-enc',self.directory,self.tmpDir,self.nm3Path,self.ffmpeg,self.verbose)        

        # 2. Decrypting Files
        import key
        key = key.getKey(self.id,self.verbose)

        import decrypt
        decrypt = decrypt.Decrypt()

        decrypt.decryptAudio(self.directory,f'{self.name}-enc',key,mp4d=self.mp4d,verbose=self.verbose)
        decrypt.decryptVideo(self.directory,f'{self.name}-enc',key,mp4d=self.mp4d,verbose=self.verbose)

        # 3. Merging Files
        import merge
        merge = merge.Merge()
        merge.ffmpegMerge(f"{self.directory}/Video.mp4",f"{self.directory}/Audio.mp4",f"{self.directory}/{self.name}.mp4",self.ffmpeg)

        # 4. Cleanup
        clean = Clean()
        clean.remove(self.directory,f'{self.name}',self.verbose)