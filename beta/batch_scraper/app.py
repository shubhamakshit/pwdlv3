from mainLogic.startup.checkup import CheckState
from mainLogic.utils.glv import Global
from mainLogic.utils import glv_var

from beta.batch_scraper.topics import Subject

token = CheckState().checkup(glv_var.EXECUTABLES, directory="./", verbose=False, do_raise=True)['prefs']['token']

Global.hr()

subject = Subject("complete-chemistry---12th-176538", "physical-and-organic-chemistry-by-686357", token, True)


