# dependency_checker.py

# Import necessary modules
from mainLogic.startup.checkup import CheckState
from mainLogic.utils import glv_var

# List of executables required for the script to run
EXECUTABLES = glv_var.EXECUTABLES


# def check_dependencies(directory, verbose, do_raise=False):
#     """Check if all dependencies are installed."""
#     state = CheckState().checkup(EXECUTABLES, directory=directory, verbose=verbose, do_raise=do_raise)
#     prefs = state['prefs']
#     glv_var.vars['prefs'] = state['prefs']
#     return state, prefs

def re_check_dependencies(reload=True):
    """Re-check dependencies.
    Using this function to reload preferences.
    """
    state = CheckState().checkup(EXECUTABLES, directory="./", verbose=False, do_raise=True)
    prefs = state['prefs']
    glv_var.vars['prefs'] = prefs

    if reload:
        glv_var.vars['prefs'] = prefs

    return state, prefs
