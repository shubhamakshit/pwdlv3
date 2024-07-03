from beta.api.mr_manager.client_manager import ClientManager
from beta.api.mr_manager.task_manager import TaskManager
from mainLogic.utils import glv_var


class Boss:
    client_manager = ClientManager('clients.json')
    task_manager = TaskManager(client_manager)
    OUT_DIR = glv_var.api_webdl_directory
