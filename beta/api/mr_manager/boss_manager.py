from beta.api.mr_manager.client_manager import ClientManager
from beta.api.mr_manager.task_manager import TaskManager
from mainLogic.utils.glv import Global

class Boss:
    client_manager = ClientManager('clients.json')
    task_manager = TaskManager(client_manager)
    OUT_DIR = Global.api_webdl_directory