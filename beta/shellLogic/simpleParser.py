def parseAndRun(commandlist,command,args=[],obj=None):
    if command in commandlist: func = commandlist[command]["func"]

    if not func: return

    func(args)