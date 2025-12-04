import os

from flask import Flask
from flask_cors import CORS


from beta.api.blueprints.admin_routes import admin
from beta.api.blueprints.api_pref_manager import api_prefs
from beta.api.blueprints.client_info_routes import client_info
from beta.api.blueprints.leagacy_create_task import legacy_create_task
from beta.api.blueprints.login import login
from beta.api.blueprints.scarper import scraper_blueprint
from beta.api.blueprints.session_lodge import session_lodge
from beta.api.blueprints.template_routes import template_blueprint
from beta.api.blueprints.while_dl_and_post_dl import dl_and_post_dl


from beta.api.blueprints.custom import custom_blueprints 

from beta.api.mr_manager.boss_manager import Boss
from mainLogic.utils.glv import Global
from mainLogic.utils.glv_var import debugger

app = Flask(__name__)
CORS(app, supports_credentials=True, origins=['*'])

# Initialize ClientManager and TaskManager
client_manager = Boss.client_manager
task_manager = Boss.task_manager
OUT_DIR = Boss.OUT_DIR

try:
    if not os.path.exists(OUT_DIR):
        os.makedirs(OUT_DIR)
except Exception as e:
    debugger.error(f"Could not create output directory {OUT_DIR}")
    debugger.success(f"Defaulting to './' ")
    debugger.error(f"Error: {e}")
    OUT_DIR = './'


app.register_blueprint(api_prefs)
app.register_blueprint(legacy_create_task)
app.register_blueprint(template_blueprint)
app.register_blueprint(session_lodge)
app.register_blueprint(dl_and_post_dl)
app.register_blueprint(client_info)
app.register_blueprint(admin)
app.register_blueprint(scraper_blueprint)
app.register_blueprint(login)

for blueprint in custom_blueprints:
    blueprint.register_blueprint(app)
if __name__ == '__main__':
    app.run(debug=True, port=7680)
