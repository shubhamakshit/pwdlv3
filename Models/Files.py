from typing import List, Any


class Files:
    class WebdlFolderData(dict):
        def __init__(self, folders=None, files=None):
            super().__init__()
            self["folders"] = folders if folders is not None else []
            self["files"] = files if files is not None else []

        @property
        def folders(self) -> List[str]:
            return self["folders"]

        @property
        def files(self) -> List[str]:
            return self["files"]
