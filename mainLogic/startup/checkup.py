import os
from mainLogic import error
from mainLogic.error import DependencyNotFound, TokenInvalid, TokenNotFound, CouldNotMakeDir
from mainLogic.utils import glv_var
from mainLogic.utils.glv_var import debugger
from mainLogic.utils.os2 import SysFunc
from mainLogic.utils.glv import Global


class CheckState:
    class MethodPatched(Exception):
        def __init__(self):
            self.err_str = "Method Has been patched"
            super().__init__(self.err_str)

    def __init__(self) -> None:
        self.default_random_id = "a3e290fa-ea36-4012-9124-8908794c33aa"



    def setup_tmp_dir(self, tmp_dir,verbose=True):
        """Sets up the temporary directory."""


        if not os.path.exists(tmp_dir):
            try:
                os.makedirs(tmp_dir)
                if verbose:
                    debugger.success(f"TmpDir created at {tmp_dir}")
            except OSError:
                print(CouldNotMakeDir(tmp_dir))
                debugger.error("Failed to create TmpDir, falling back to default.")
                tmp_dir = './tmp/'
        return tmp_dir

    def post_checkup(self, prefs, skip_tmp_dir=False,verbose=True):
        """
        Post Checkup Function
        1. Setting up the tmpDir
        2. Setting up the output directory
        3. Setting up the horizontal rule
        """
        # Setting up tmpDir
        tmpDir = SysFunc.modify_path(prefs.get('tmpDir', './tmp/'))

        if not skip_tmp_dir:
            tmpDir = self.setup_tmp_dir(tmpDir)


        # Setting up output directory
        if not prefs.get('dir'):
            out_dir = './'
        else:
            out_dir = prefs.get('dir')
        try:
            out_dir = os.path.expandvars(out_dir)
            if not os.path.exists(out_dir):
                os.makedirs(out_dir)
            OUT_DIRECTORY = os.path.abspath(out_dir)
            
        except Exception as e:
            debugger.error(f"Error: {e}, falling back to default output directory.")
            OUT_DIRECTORY = './'

        # Setting up horizontal rule
        Global.disable_hr = not prefs.get('hr', True)

        prefs['tmpDir'] = tmpDir
        prefs['dir'] = OUT_DIRECTORY

    def validate_token(self, token_data, verbose=False):
        """Validates and extracts token and random ID from token data."""
        import json

        # return token_data.get('token') or token_data.get('access_token'), token_data.get('random_id',self.default_random_id)
        # token = data.get('token') or data.get('access_token')
        #                 random_id = data.get('randomId', "a3e290fa-ea36-4012-9124-8908794c33aa")
        if isinstance(token_data, dict):
            pass

        elif token_data.startswith("{"):
            try:
                # this is the token data that is being passed to the json loads
                data = json.loads(token_data)
                token_data = data

            except json.JSONDecodeError as e:
                if verbose:
                    debugger.error(f"Error decoding token data: {e}")
                raise TokenInvalid()

        if "token" in token_data:
            token = token_data.get('token')
            random_id = token_data.get('randomId', self.default_random_id)

        elif "access_token" in token_data:
            token = token_data.get('access_token')
            random_id = token_data.get('randomId', self.default_random_id)

        else:
            if verbose:
                debugger.error("Invalid Token Data")
            raise TokenInvalid()

        return token, random_id



    def check_token(self, token, random_id, id="680c85b0c9d776d19b869d3f",batch_name="65d75d320531c20018ade9bb", verbose=False):
        """Checks the validity of a token using LicenseKeyFetcher."""

        if not id: id="680c85b0c9d776d19b869d3f"
        if not batch_name: batch_name="65d75d320531c20018ade9bb"

        if verbose:
            Global.hr()
            debugger.debug("Checking Token...")
            debugger.debug(f"Token: {token}")
            debugger.debug(f"Random ID: {random_id}")
            debugger.debug(f"ID: {id}")

        from mainLogic.big4.Ravenclaw_decrypt.key import LicenseKeyFetcher
        lc_fetcher = LicenseKeyFetcher(token=token, random_id=random_id)

        try:
            return lc_fetcher.get_key(id, batch_name,verbose=verbose)
        except Exception as e:
            debugger.error(f"An error occurred while getting the key: {e}")
            raise TokenInvalid()

    def checkup(self, executable, directory="./",tmp_dir=None, verbose=True, do_raise=False):
        state = {}

        if tmp_dir:
            debugger.info("Setting up tmpDir to " + tmp_dir)
            tmp_dir = self.setup_tmp_dir(tmp_dir, verbose)
            state['tmpDir'] = tmp_dir




        prefs = self.load_preferences(verbose)

        if self.is_method_patched(prefs, do_raise):
            return state



        # Check for executables
        state.update(self.check_executables(executable, prefs, verbose, do_raise))

        if not glv_var.vars.get('ig_token'):
            # Validate token

            token = prefs.get('token')
            if token:

                try:
                    token, random_id = self.validate_token(token, verbose)

                    # save the token config (which can be used to get the token)
                    prefs['token_config'] = prefs.get('token')

                    # prefs token is the actual token
                    prefs['token'] = token
                    prefs['random_id'] = random_id

                    try:
                        try:
                            video_id = prefs.get("video_id",None)
                            ##debugger.var(prefs)
                            batch_name = prefs.get("batch_name",None)
                            debugger.debug(f"Got video_id as '{video_id}' and batch_name as '{batch_name}'")
                        except Exception as e:
                            debugger.error("Failed to extract video_id or batch name")
                            debugger.error(e)
                        if id and batch_name:
                            key = self.check_token(token, random_id, verbose=verbose,id = video_id, batch_name = batch_name)
                        else:
                            key = self.check_token(token, random_id, verbose=verbose)
                        if key:
                            if verbose:
                                debugger.success("Token Valid")
                            prefs['key'] = key
                        else:
                            if verbose:
                                debugger.error("Token Invalid! Please run pwdl --login")


                    except TokenInvalid:
                        self.raise_or_exit("tokenInvalid", do_raise)

                except TokenInvalid:
                    self.raise_or_exit("tokenInvalid", do_raise)
            else:
                self.raise_or_exit("tokenNotFound", do_raise)

        else:
            debugger.error("Token not found But ignoring it")


        state['prefs'] = prefs
        prefs['dir'] = directory
        self.post_checkup(prefs, verbose)

        return state

    def load_preferences(self, verbose):
        """Loads user preferences from the PreferencesLoader."""
        from mainLogic.startup.userPrefs import PreferencesLoader
        return PreferencesLoader(verbose=verbose).prefs

    def is_method_patched(self, prefs, do_raise):
        """Checks if the method is patched based on preferences."""
        if prefs.get('patched'):
            error.errorList["methodPatched"]["func"]()
            if do_raise:
                raise self.MethodPatched()
            exit(error.errorList["methodPatched"]["code"])
        return False

    def check_executables(self, executables, prefs, verbose, do_raise):
        """Checks if the required executables are available."""
        os2 = SysFunc()
        state = {}
        not_found = []

        for exe in executables:
            if os2.which(exe) == 1:
                not_found.append(exe)
            else:
                if verbose:
                    debugger.success(f"{exe} found.")
                state[exe] = exe

        if not_found:
            self.handle_not_found_executables(not_found, prefs, state, verbose, do_raise)

        return state

    def handle_not_found_executables(self, not_found, prefs, state, verbose, do_raise):
        """Handles the case where some executables are not found."""
        if verbose:
            Global.hr()
            debugger.debug("Following dependencies were not found on path. Checking in default settings...")
            debugger.debug(not_found)
            Global.hr()

        for exe in not_found:
            if verbose:
                debugger.debug(f"Checking for {exe} in default settings...")

            exe_path = prefs.get(exe)
            if exe_path:
                exe_path = exe_path.strip()
                if not os.path.exists(exe_path):
                    debugger.error(f"{exe} not found at {exe_path}")
                    self.raise_or_exit("dependencyNotFoundInPrefs", do_raise, exe)
                if verbose:
                    debugger.success(f"{exe} found at {exe_path}")
                state[exe] = exe_path
            else:
                self.raise_or_exit("dependencyNotFoundInPrefs", do_raise, exe)
            if verbose:
                Global.hr()

    def raise_or_exit(self, error_key, do_raise, exe=None):
        """Raises an exception or exits based on the error key."""

        if error_key == "dependencyNotFoundInPrefs":
            if do_raise:
                raise DependencyNotFound(exe)
            else:
                DependencyNotFound(exe).exit()

        elif error_key == "tokenInvalid":
            if do_raise:
                raise TokenInvalid()
            else:
                TokenInvalid().exit()

        elif error_key == "tokenNotFound":
            if do_raise:
                raise TokenNotFound()
            else:
                TokenNotFound().exit()

        # if do_raise:
        #     # check if CheckState has the error_key as a method else raise the error with the error_key
        #     if hasattr(self, error_key):
        #         raise getattr(self, error_key)()
        #     else:
        #         pass
        #
        # if not exe:
        #     error.errorList[error_key]["func"]()
        # else:
        #     error.errorList[error_key]["func"](exe)
        #
        # if not do_raise:
        #     exit(error.errorList[error_key]["code"])
