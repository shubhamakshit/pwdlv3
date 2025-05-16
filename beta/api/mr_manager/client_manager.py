import json
import os

from mainLogic.utils.glv import Global
from mainLogic.utils.glv_var import debugger


class ClientManager:
    def __init__(self, json_file_path):
        self.json_file_path = json_file_path
        self.clients = self.load_data()

    def load_data(self):
        if not os.path.exists(self.json_file_path):
            return {}
        try:
            with open(self.json_file_path, 'r') as file:
                return json.load(file)
        except json.JSONDecodeError:
            return {}

    def save_data(self):
        with open(self.json_file_path, 'w') as file:
            json.dump(self.clients, file, indent=4)

    def client_exists(self, client_id):
        return client_id in self.clients

    def session_exists(self, client_id, session_id):
        return client_id in self.clients and session_id in self.clients[client_id]['sessions']

    def add_client(self, client_id="anonymous",name=""):
        if client_id not in self.clients:
            self.clients[client_id] = {
                "name": "Anonymous" if client_id == "anonymous" else name,
                "client_id": client_id,
                "sessions": {}
            }
            self.save_data()
        else:
            print(f"Client with ID {client_id} already exists.")

    def remove_client(self, client_id):
        if client_id in self.clients:
            del self.clients[client_id]
            self.save_data()
        else:
            print(f"Client with ID {client_id} does not exist.")

    def set_client_name(self, client_id, name):
        if client_id in self.clients:
            self.clients[client_id]['name'] = name
            self.save_data()
        else:
            print(f"Client with ID {client_id} does not exist.")

    def add_session(self, client_id="anonymous", session_id="anonymous"):
        from mainLogic.utils.gen_utils import generate_timestamp
        if client_id in self.clients:
            if session_id not in self.clients[client_id]['sessions']:
                timestamp = generate_timestamp()
                self.clients[client_id]['sessions'][session_id] = {"tasks": {}, "name": "", "timestamp": timestamp}
                self.save_data()
            else:
                print(f"Session with ID {session_id} already exists for client {client_id}.")
        else:
            print(f"Client with ID {client_id} does not exist.")

    def remove_session(self, client_id, session_id):
        if client_id in self.clients and session_id in self.clients[client_id]['sessions']:
            del self.clients[client_id]['sessions'][session_id]
            self.save_data()
        else:
            print(f"Session with ID {session_id} does not exist for client {client_id}.")

    def add_task(self, client_id, session_id, task_id, task_info):
        if client_id in self.clients and session_id in self.clients[client_id]['sessions']:
            self.clients[client_id]['sessions'][session_id]['tasks'][task_id] = task_info
            self.save_data()
        else:
            print(f"Either client with ID {client_id} or session with ID {session_id} does not exist.")

    def get_tasks(self,client_id,session_id=None):

        # if session_id is empty return all tasks
        if not session_id:
            return self.clients[client_id]['sessions']
        else:
            return self.clients[client_id]['sessions'][session_id]['tasks']

    def get_task(self,task_id):
        for client_id in self.clients:
            for session_id in self.clients[client_id]['sessions']:
                if task_id in self.clients[client_id]['sessions'][session_id]['tasks']:
                    return self.clients[client_id]['sessions'][session_id]['tasks'][task_id]
        return None

    def update_task(self, task_info):
        client_id = task_info['client_id']
        session_id = task_info['session_id']
        task_id = task_info['task_id']
        if client_id in self.clients and session_id in self.clients[client_id]['sessions']:
            if task_id in self.clients[client_id]['sessions'][session_id]['tasks']:
                self.clients[client_id]['sessions'][session_id]['tasks'][task_id] = task_info
                self.save_data()
            else:
                print(f"Task with ID {task_id} does not exist in session {session_id} for client {client_id}.")
        else:
            print(f"Either client with ID {client_id} or session with ID {session_id} does not exist.")

    def remove_task(self, client_id, session_id, task_id):
        if client_id in self.clients and session_id in self.clients[client_id]['sessions']:
            if task_id in self.clients[client_id]['sessions'][session_id]['tasks']:
                del self.clients[client_id]['sessions'][session_id]['tasks'][task_id]
                self.save_data()
            else:
                print(f"Task with ID {task_id} does not exist in session {session_id} for client {client_id}.")
        else:
            print(f"Either client with ID {client_id} or session with ID {session_id} does not exist.")

    def get_client_info(self, client_id):
        if client_id in self.clients:
            return self.clients[client_id]
        else:
            print(f"Client with ID {client_id} does not exist.")
            return None

    def get_progress(self,task_id):
        task = self.get_task(task_id)
        if task:
            return task
        else:
            debugger.error(f"Task with ID {task_id} does not exist.")
            return None

    def set_session_name(self, client_id, session_id, name):
        if client_id in self.clients and session_id in self.clients[client_id]['sessions']:
            self.clients[client_id]['sessions'][session_id]['name'] = name
            self.save_data()
        else:
            print(f"Either client with ID {client_id} or session with ID {session_id} does not exist.")


    def delete_session(self, client_id, session_id):
        if client_id in self.clients and session_id in self.clients[client_id]['sessions']:
            del self.clients[client_id]['sessions'][session_id]
            self.save_data()
        else:
            print(f"Session with ID {session_id} does not exist for client {client_id}.")

    def merge_sessions(self, client_id, session_id_1, session_id_2):
        if client_id in self.clients and session_id_1 in self.clients[client_id]['sessions'] and session_id_2 in self.clients[client_id]['sessions']:

            # DEBUG
            Global.hr()
            print(f"Session 1: {session_id_1}")
            print(f"Session 2: {session_id_2}")
            print(f"Tasks in session 1: {json.dumps(self.clients[client_id]['sessions'][session_id_1]['tasks'], indent=4)}")
            print(f"Tasks in session 2: {json.dumps(self.clients[client_id]['sessions'][session_id_2]['tasks'], indent=4)}")
            Global.hr()

            # Create a list of task IDs to delete to avoid changing dictionary size during iteration
            tasks_to_delete = [task_id for task_id, task in self.clients[client_id]['sessions'][session_id_2]['tasks'].items()
                               if task['status'] in ['downloading', 'created', 'failed']]

            # Delete the tasks from session_id_2
            for task_id in tasks_to_delete:
                debugger.debug(f"Deleting task {task_id}")
                del self.clients[client_id]['sessions'][session_id_2]['tasks'][task_id]

            # Move tasks from session_id_2 to session_id_1
            self.clients[client_id]['sessions'][session_id_1]['tasks'].update(self.clients[client_id]['sessions'][session_id_2]['tasks'])

            # Delete session_id_2
            del self.clients[client_id]['sessions'][session_id_2]
            self.save_data()
        else:
            print(f"Either client with ID {client_id} or session with ID {session_id_1} or {session_id_2} does not exist.")


    def delete_client(self, client_id):
        if client_id in self.clients:
            del self.clients[client_id]
            self.save_data()
        else:
            print(f"Client with ID {client_id} does not exist.")
