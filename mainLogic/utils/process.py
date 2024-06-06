import subprocess
import re
import sys


def shell(command, filter=None, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True, progress_callback=None):
    import os

    # Set PYTHONUNBUFFERED environment variable
    os.environ['PYTHONUNBUFFERED'] = '1'

    command = to_list(command)

    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)

    # Read and print the output in real-time
    while True:
        output = process.stdout.readline()
        if output == '' and process.poll() is not None:
            break
        if output and filter is not None and re.search(filter, output):

            # call the progress callback with the filtered output
            if progress_callback: progress_callback(output)
            print(output.strip())

    # Wait for the process to complete and get the return code
    return_code = process.poll()

    return return_code


def to_list(variable):
    if isinstance(variable, list):
        return variable
    elif variable is None:
        return []
    else:
        # Convert to string and then to list by splitting at whitespaces
        return variable.split()
