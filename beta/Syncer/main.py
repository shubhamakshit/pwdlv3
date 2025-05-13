import random

from beta.Syncer.db_utils.DataObject import DbObject
from beta.Syncer.db_utils.Database import DB
from beta.update import UpdateJSONFile
from mainLogic.error import debugger
from mainLogic.utils import glv_var

user_schema = {
    "_id":{
        "type": str,
        "required": True,
    },
    "token":{
        "type": dict,
        "required": True,
    },
    "user_update_index":{
        "type": int,
        "required": True,
    }
}

class Syncer:
    def __init__(self):
        self.url = "mongodb+srv://tshonqkhan:writer@eminem.jsekgk2.mongodb.net/?retryWrites=true&w=majority&appName=Eminem"
        self.database = DB(self.url).set_db("pwdlv3").set_collection("users")
        self.updater = UpdateJSONFile(glv_var.PREFS_FILE)
        self.user_id = self.updater.data.get("user_id", "")
        self.user_update_index = self.updater.data.get("user_update_index", 0)

        # Initialize sync on creation
        self.sync()

    def sync(self):
        # get user id from prefs
        user_id = self.user_id
        if not user_id:
            debugger.error("No user ID found in preferences")
            return

        debugger.debug(f"User id: {user_id}")

        # check if user exists
        user = self.database.get_object({"_id": user_id}).compile()

        if user:
            debugger.debug(f"User found: {user}")

            # Get update indices
            local_update_index = self.user_update_index
            db_update_index = user.get("user_update_index", 0)

            # Check if local index is -1 (force update)
            if local_update_index == -1:
                debugger.debug("Force update requested")
                # Update local token with DB token
                self.updater.update("token", user.get("token", {}))
                # Reset local update index to match DB
                self.updater.update("user_update_index", db_update_index)
                debugger.debug(f"Token forcefully updated from DB. Update index reset to {db_update_index}")

            # Check if local index is less than DB index (DB has newer data)
            elif local_update_index < db_update_index:
                debugger.debug(f"Local update index ({local_update_index}) is less than DB index ({db_update_index})")
                # Update local token with DB token
                self.updater.update("token", user.get("token", {}))
                # Update local update index to match DB
                self.updater.update("user_update_index", db_update_index)
                debugger.debug("Token updated from DB")

            # Check if local index is greater than DB index (local has newer data)
            elif local_update_index > db_update_index:
                debugger.debug(f"Local update index ({local_update_index}) is greater than DB index ({db_update_index})")
                # Update DB token with local token
                self.update_token(user_id, self.updater.data.get("token", {}), local_update_index)

            else:
                debugger.debug(f"Update indices match ({local_update_index}). No sync needed.")
        else:
            debugger.debug("User not found")
            # create new user with initial update index of 0
            user = DbObject(user_schema) \
                .add(("_id", user_id)) \
                .add(("token", {})) \
                .add(("user_update_index", 0))
            self.database.insert(user)
            debugger.debug(f"User created: {user}")
            debugger.error(f"Since user was not found, a new user was created. Please restart the app to sync the token.")

    def update_token(self, user_id, token, update_index=None):
        # If no update index provided, increment the current one
        if update_index is None:
            update_index = self.user_update_index + 1

        # Update token in database
        self.database.update({
            "_id": user_id
        }, {
            "$set": {
                "token": token,
                "user_update_index": update_index
            }
        })

        # Update local preferences
        self.updater.update("token", token)
        self.updater.update("user_update_index", update_index)

        debugger.debug(f"Token updated in DB with update index: {update_index}")
        debugger.error(f"Token updated. Please restart the app to sync the token.")

