import json
import os

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

    def add_client(self, client_id="anonymous"):
        if client_id not in self.clients:
            self.clients[client_id] = {
                "name": "Anonymous" if client_id == "anonymous" else "",
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

    def add_session(self, client_id="anonymous", session_id="anonymous"):
        if client_id in self.clients:
            if session_id not in self.clients[client_id]['sessions']:
                self.clients[client_id]['sessions'][session_id] = {"tasks": {}, "name": ""}
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

    def delete_client(self, client_id):
        if client_id in self.clients:
            del self.clients[client_id]
            self.save_data()
        else:
            print(f"Client with ID {client_id} does not exist.")
