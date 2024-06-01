from flask import Flask, request, jsonify, abort
from webdl.Tasks import Tasks
from webdl.process import Process
import threading
import uuid
import io

app = Flask(__name__)
TasksList = {}



@app.route('/get/<clientId>',methods = ['GET'])
def getOutputForClient(clientId):
    print(clientId)
    print(TasksList)
    return TasksList[clientId][0].readline()




@app.route('/')
def index():
    return 'Hello World!'

@app.route('/dl', methods=['GET', 'POST'])
def dl():
    if request.method == 'GET': pass
    if request.method == 'POST':

        try:
            raw_data = dict(request.get_json())

            # checks if clientId is present or not
            if not 'client_id' in raw_data:
                raise Exception("Client Id not specified")

            client_id = raw_data['client_id']


            # checks if names or ids is not present (in that case there is no point downloading!)
            if not 'names' in raw_data or not 'ids' in raw_data:
                raise KeyError("Check your data ~  'names' or 'ids' missing")


            vid_names = raw_data['names']
            vid_ids = raw_data['ids']

            # checks if length of names and ids mismatch
            if not len(vid_names) == len(vid_ids):
                raise Exception("Illegal! Lengths of 'names' and 'ids' array mismatch")

            print(f"Length: {len(vid_ids)}")

            for i in range(len(vid_ids)):
                t = threading.Thread(
                    lambda: Process.shell('pwdl --verbose',regex_filter=r'.*')
                )
                t.start()



        except Exception as e:
            return {
                "status"    : "400",
                "message"   : str(e),

            }



    return '200'




if __name__ == "__main__":
    app.run(debug=True)