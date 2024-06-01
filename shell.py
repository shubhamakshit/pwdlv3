from utils.glv import Global
from startup.checkup import CheckState
import json

glv = Global()

EXECUTABLES = glv.EXECUTABLES

def main():

    state = CheckState().checkup(EXECUTABLES,True)
    prefs = state['prefs']

    print(json.dumps(prefs,indent=4))

if __name__ == "__main__":
    main()