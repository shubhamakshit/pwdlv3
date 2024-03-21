from basicUtils import BasicUtils
from glv import Global
from cleanup import Clean
class Main:
    def __init__(self,id,name=None,directory="./",tmpDir="/*auto*/",nm3Path='nm3',ffmpeg="ffmpeg",verbose=True):
        self.id = id
        self.name = name if name else id
        self.directory = directory
        self.tmpDir = tmpDir
        self.nm3Path = BasicUtils.abspath(nm3Path) if nm3Path != 'nm3' else 'nm3'
        self.ffmpeg = BasicUtils.abspath(ffmpeg) if ffmpeg != 'ffmpeg' else 'ffmpeg'
        self.verbose = verbose

        if self.verbose:
            Global.hr()
            Global.dprint(f"ID: {self.id}")
            Global.dprint(f"Name: {self.name}")
            Global.dprint(f"Directory: {self.directory}")
            Global.dprint(f"TmpDir: {self.tmpDir}")
            Global.dprint(f"Nm3Path: {self.nm3Path}")
            Global.dprint(f"FFmpeg: {self.ffmpeg}")
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

        decrypt.decryptAudio(self.directory,f'{self.name}-enc',key)
        decrypt.decryptVideo(self.directory,f'{self.name}-enc',key)

        # 3. Merging Files
        import merge
        merge = merge.Merge()
        merge.ffmpegMerge(f"{self.directory}/video.mp4",f"{self.directory}/audio.mp4",f"{self.directory}/{self.name}.mp4",self.ffmpeg)

        # 4. Cleanup
        clean = Clean()
        clean.remove(self.directory,f'{self.name}',self.verbose)