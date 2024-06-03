from mainUtils.key import getKey
from utils.os2 import SysFunc

os2 = SysFunc()



# x is default argument
# every function should accept x as default argument (a list)
commands = {
    "cls":{
        "desc":"Clear the screen",
        "func":lambda x = [] : os2.clear()
    },
    "exit":{
        "desc":"Exit the shell",
        "func":lambda x = [] : exit(0)
    },
    "echo":{
        "desc":"Print the arguments",
        "func":lambda *x : print(' '.join(x))
    },
    "help":{
        "desc":"Print the help",
        "func":lambda x = [] : [print(f"{command} : {commands[command]['desc']}") for command in commands]
    },
    "get_key":{
        "desc" : "uses getKey from mainUtils to extract key for a given id",
        "func": lambda x = [] : print(getKey("".join(x),verbose=True)) if len(x) > 0 else print("Please provide an id")
    },
    "help":{
        "desc":"Linux inspired help command",
        "args":{
            "command":"The command for which you need help"

        }
    }


}

def help(command,args):
    print(f"{command} : {commands[command]['desc']}")
    if 'args' in commands[command]:
        print(f"Arguments: {commands[command]['args']}")