import threading
import uuid

class TaskManager:
    def __init__(self, client_manager):
        self.tasks = {}
        self.lock = threading.Lock()
        self.client_manager = client_manager
        self.inactive_tasks = {}

    def handle_completion(self, task_id):
        print(f"Task {task_id} completed")
        with self.lock:
            self.tasks[task_id]['status'] = 'completed'
            self.client_manager.update_task(self.tasks[task_id])

    on_task_complete = handle_completion

    def create_task(self, client_id, session_id, target, *args, inactive=False):
        task_id = str(uuid.uuid4())
        print(f"Args: {args}")
        args_dict = args[0]
        try:
            name = args_dict['name']
            id = args_dict['id']
            out_dir = args_dict['out_dir']
        except KeyError:
            raise ValueError('name, id, and out_dir are required in args')

        client_id = args_dict.get('client_id', client_id)
        session_id = args_dict.get('session_id', session_id)

        task_info = {
            'task_id': task_id,
            'progress': {
                'progress': 0
            },
            'status': 'created' if inactive else 'running',  # Set status to 'created' if inactive
            'name': name,
            'out_dir': out_dir,
            'id': id,
            'client_id': client_id,
            'session_id': session_id
        }

        with self.lock:
            self.tasks[task_id] = task_info
            self.client_manager.add_task(client_id, session_id, task_id, task_info)

        if not inactive:
            thread = threading.Thread(target=self._run_task, args=(task_info, target, name, id, out_dir, client_id, session_id, *args[1:]))
            thread.start()
        else:
            self.inactive_tasks[task_id] = {
                'target': target,
                'args': args,
                'task_info': task_info
            }

        return task_id

    def start_task(self, task_id):
        with self.lock:
            if task_id in self.tasks:
                if self.tasks[task_id]['status'] == 'created':
                    task_info = self.tasks[task_id]
                    target = self._get_target_function(task_id)  # Replace with your actual logic to retrieve the target function
                    thread = threading.Thread(target=self._run_task, args=(task_info, target, task_info['name'], task_info['id'], task_info['out_dir'], task_info['client_id'], task_info['session_id']))
                    thread.start()
                    self.tasks[task_id]['status'] = 'running'
                else:
                    raise ValueError(f"Task {task_id} is already running or completed.")

    def _run_task(self, task_info, target, *args):
        task_id = task_info['task_id']
        try:
            print(task_id, [*args], lambda progress: self._update_progress(task_id, progress))
            target(task_id, *args, progress_callback=lambda progress: self._update_progress(task_id, progress))
            with self.lock:
                self.tasks[task_id]['url'] = f'/get-file/{task_id}/{self.tasks[task_id]["name"]}'
                self.tasks[task_id]['status'] = 'completed'
                self.client_manager.update_task(self.tasks[task_id])
        except Exception as e:
            with self.lock:
                self.tasks[task_id]['status'] = 'failed'
                self.tasks[task_id]['error'] = str(e)
                self.client_manager.update_task(self.tasks[task_id])

    def _update_progress(self, task_id, progress):
        with self.lock:
            if task_id in self.tasks:
                self.tasks[task_id]['progress'] = progress
                self.client_manager.update_task(self.tasks[task_id])

    def get_progress(self, task_id):
        with self.lock:
            return self.tasks.get(task_id, {'status': 'not found'})

    def _get_target_function(self, task_id):
        if task_id in self.inactive_tasks:
            return self.inactive_tasks[task_id]['target']
        else:
            raise ValueError(f"Task {task_id} is not inactive.")


