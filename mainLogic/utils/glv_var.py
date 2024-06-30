# defining some variables that can be used in the preferences file
import os
from mainLogic.utils.basicUtils import BasicUtils

vars = {

            # $script is the path to the folder containing the pwdl.py file
            # Since the userPrefs.py is in the startup folder,
            # we need to go one level up however we make the exception that if the pwdl.py is in the same folder as
            # the startup folder, we don't need to go one level up
            "$script": BasicUtils.abspath(os.path.dirname(__file__) + (
                '/../..' if not os.path.exists(os.path.dirname(__file__) + '../pwdl.py') else '')),
            "$home": os.path.expanduser("~"),
        }
env_file = os.getenv('PWDL_PREF_FILE')
if env_file and os.path.exists(env_file):
    print(f"Using preferences file: {env_file}")
    PREFS_FILE = env_file
else:
    print(f"Using default preferences file: {os.path.join(vars['$script'], 'defaults.json')}")
    PREFS_FILE = os.path.join(vars["$script"], 'defaults.json')

api_webdl_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../webdl'))
EXECUTABLES = ['ffmpeg', 'mp4decrypt', 'vsd']