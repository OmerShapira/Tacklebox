"""Config object for Baits"""

from core import fileutils

#TODO (OS): needs to inherit MutableMapping
class Bait(object):
    """TODO (OS): fill this in"""
    def __init__(self, folder):
        assert type(folder).__name__ == "Folder", "Bait only takes 'Folder' objects as input "
        self.folder = folder
        self.name = folder.folder_name()

    def is_valid(self):
        #check folder exists
        if not self.folder.exists():
            return False, "Folder for bait named '" + self.name + "' does not exist: " + self.folder.path

        #check config file exists
        #check config file matches schema
        #TODO(OS): finish

    def create(self):
        pass
