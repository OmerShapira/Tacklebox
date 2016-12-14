"""Config object for Baits"""

import os

from core.fileutils import MemoryMappedTOMLFile
from consts import consts

class BaitFolder(object):
    """TODO (OS): fill this in"""
    def __init__(self, folder):
        assert type(folder).__name__ == "Folder", "Bait only takes 'Folder' objects as input "
        #TODO (OS): check if tacklebox root exists in parent folders
        self.folder = folder
        self.name = folder.folder_name()
        self.config_file = BaitConfigFile(self.folder.path)

    def exists(self):
        return self.folder.exists() and self.config_file.exists()

    def is_valid(self):
        #check folder exists
        if not self.folder.exists():
            return False, "Folder for bait named '" + self.name + "' does not exist: " + self.folder.path

        #check config file exists
        if not self.config_file.exists():
            return False, "No config file for bait at " + self.folder.path

        #check config file matches schema
        #TODO(OS): finish
        return True, ""

    def load(self):
        if self.is_valid():
            self.config_file.load()



class BaitConfigFile(MemoryMappedTOMLFile):
    def __init__(self, folder_path):
        path = os.path.join(folder_path, consts.BAIT_FILE_NAME)
        super(BaitConfigFile, self).__init__(path)

    def create(self):
        """Deletes current configuration (if exists) and creates a new one"""
        if not self.exists():
           self.clear()
        with self.mutable():
            self['friendly_name'] = ""
            self['target'] = {"path" : ""}

    def is_valid(self):
        """TODO (OS): Make better indicator"""
        return 'path' in self['target'].keys()


