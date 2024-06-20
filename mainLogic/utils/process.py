import subprocess
import re
import sys

def shell(command, filter=None, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True, progress_callback=None, handleProgress=None, inline_progress=True):
    import os

    # Set PYTHONUNBUFFERED environment variable
    os.environ['PYTHONUNBUFFERED'] = '1'

    command = to_list(command)

    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, encoding='utf-8', universal_newlines=True)

    while True:
        try:
            output = process.stdout.readline()
            output = output.strip()

            if output == '' and process.poll() is not None:
                break

            if output:
                if filter is not None and re.search(filter, output):
                    # Call the progress callback with the filtered output
                    if progress_callback:
                        if handleProgress:
                            progress_callback(handleProgress(output))
                        else:
                            progress_callback(output)

                if inline_progress:
                    # Update progress in the same line
                    sys.stdout.write('\r' + output.strip())
                    sys.stdout.flush()
                else:
                    # Print output normally
                    print(output.strip())

        except UnicodeEncodeError:
            sys.stdout.write("\rUnicodeEncodeError")
            sys.stdout.flush()
            pass
        except Exception as e:
            print(f"Error: {e}")

    # Wait for the process to complete and get the return code
    return_code = process.wait()

    return return_code

def to_list(variable):
    if isinstance(variable, list):
        return variable
    elif variable is None:
        return []
    else:
        # Convert to string and then to list by splitting at whitespaces
        return variable.split()
