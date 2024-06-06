import threading
import time
import uuid

class TaskManager:

    def handle_completion (self, task_id):
        print(f"Task {task_id} completed")
        self.tasks[task_id]['status'] = 'completed'

    on_task_complete = handle_completion

    def __init__(self):
        self.tasks = {}
        self.lock = threading.Lock()

    def create_task(self, target, *args):
        task_id = str(uuid.uuid4())
        thread = threading.Thread(target=self._run_task, args=(task_id, target, *args))
        with self.lock:
            self.tasks[task_id] = {'progress': "0", 'status': 'running'}
        thread.start()
        return task_id

    def _run_task(self, task_id, target, *args):
        try:
            target(task_id,*args, progress_callback=lambda progress: self._update_progress(task_id, progress))
            with self.lock:
                self.tasks[task_id]['status'] = 'completed'
        except Exception as e:
            with self.lock:
                self.tasks[task_id]['status'] = 'failed'
                self.tasks[task_id]['error'] = str(e)

    def _update_progress(self, task_id, progress):
        with self.lock:
            if task_id in self.tasks:
                self.tasks[task_id]['progress'] = progress

    def get_progress(self, task_id):
        with self.lock:
            return self.tasks.get(task_id, {'status': 'not found'})
