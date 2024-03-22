import argparse
from glv import Global
import sys
from userPrefs import PreferencesLoader
from os2 import SysFunc
import os
from main import Main
from checkup import CheckState

prefs = {}
glv = Global()
os2 = SysFunc()
EXECUTABLES = ['ffmpeg','mp4decrypt','nm3']

        

def main():
    
    global prefs
    
    # check if all dependencies are installed
    state = CheckState().checkup(EXECUTABLES)
    prefs = state['prefs']


    parser = argparse.ArgumentParser(description='PhysicsWallah M3u8 parser.')
    parser.add_argument('--csv-file', type=str, help='Input csv file. Legacy Support too.')
    parser.add_argument('--id', type=str, help='PhysicsWallh Video Id for single usage. Incompatible with --csv-file.   Must be used with --name')
    parser.add_argument('--name', type=str, help='Name for the output file. Incompatible with --csv-file.   Must be used with --url')
    parser.add_argument('--dir', type=str, help='Output Directory')
    parser.add_argument('--verbose',action='store_true',help='Verbose Output')
    args = parser.parse_args()

    # user_input is given prefernce i.e if --verbose is true it will override
    # however if --verbose is false but prefs['verbose'] is true 
    glv.vout = args.verbose
    
    if not glv.vout and prefs['verbose'] : glv.vout = prefs['verbose']

    


  
    # setting up output directory
    if args.dir: OUT_DIRECTORY = os.path.abspath(os.path.expandvars(args.dir))
    else: OUT_DIRECTORY = './'
    if glv.vout: glv.dprint(f'Output Directory: {OUT_DIRECTORY}')

    #if both csv file and (url or name) is provided then -> exit with error code 3
    if args.csv_file and ( args.id or args.name):
        print("Both csv file and id (or name) is provided. Unable to decide. Aborting! ...")
        sys.exit(3)

    # handle in case --csv-file is provided
    if args.csv_file:
        print(args.csv_file)

    # handle in case key and name is given 
    elif args.id and args.name:
        Main(id=args.id,
             name=args.name,
             directory=OUT_DIRECTORY,
             ffmpeg=state['ffmpeg'],
             nm3Path=state['nm3'],
             verbose=glv.vout).process()
    # in case neither is used 
    else:
        exit(1)

if __name__ == "__main__":
    main()