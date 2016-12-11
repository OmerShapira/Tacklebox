"""
Configuration managers and helpers
"""
import consts
import os
from core.fileutils import Folder, MemoryMappedTOMLFile, is_git_repo

class UserConfigFile(MemoryMappedTOMLFile):
    '''refers to user config file only by name.
    performs atomic actions and keeps file closed.
    file is in constant place - when backing up, file will be copied into backup, and the original
    will be deleted, but the location will be saved.

    '''
    def __init__(self, config_folder, repo_path):
        self.config_folder = config_folder
        path = os.path.join( self.config_folder.folder.path, consts.USER_CONFIG_FILE_NAME)
        super(UserConfigFile, self).__init__(path)
        #TODO (OS): remove coupling
        self.repo_path = repo_path

    def create(self):
        #TODO(OS): use schema
        with self.mutable():
            self['version'] = consts.VERSION
            self['repo'] = {}
            self['repo']['active'] = 'master'
            self['repo']['master'] = {}
            self['repo']['master']['root'] = self.repo_path
            self['repo']['master']['type'] = 'git'

    def archive_to(self, abs_path_backup_folder):
        """
        Copies the file to a backup folder. Will fail if file exists.
        config file will still point to same place.
        """

    def is_valid(self):
        if not self.does_point_to_git_repo():
            return False
        try:
            pv, fv = consts.VERSION, self['version']
            assert pv == fv, "Config file version ("+fv+") does not match the program version ("+pv+")"
            root = self['repo']['master']['root']
            assert is_git_repo(root), root + " is not a git repo"
        except ( AssertionError, ) as E:
            err = "Config File Validation Error: " + str(E)
            return False, err
        except ( ValueError, KeyError ) as E:
            err =  "Config File Validation Error: Does not contiain " + str(E)
            return False, err
        except Exception as E:
            err = "Exception "+ type(E).__name__ +" during file validation: " + str(E.args)
            return False, err
        return True, ""

    def does_point_to_git_repo(self):
        """Checks only by name. If you're gonna play evil, I'm not going to catch it."""
        return is_git_repo(self.repo_path)


class BaitConfigFile(MemoryMappedTOMLFile):
    def __init__(self, path):
        # Find if is local root
        super(BaitConfigFile, self).__init__(path)


class UserConfigFolder(object):
    """Docstring for UserConfigFolder"""
    def __init__(self, repo_path):
        # The root will only be at the user root for now.
        path = os.path.join(os.path.expanduser(consts.USER_CONFIG_HOME), consts.USER_CONFIG_FOLDER_NAME)

        self.folder = Folder(path)
        self.backup_folder_name = consts.BACKUP_DIR_NAME + consts.CONFIG_EXTENSION_CURRENT
        self.config_file_name = consts.USER_CONFIG_FILE_NAME
        self.config_file = UserConfigFile(self, repo_path)

    def load(self):
        """
        Attempt to load, fail if fucked
        """
        result, err =  self.is_valid()
        if result:
            return self
        else:
            exit (err)

    def exists(self):
        """Check if:
        * Folder Exists
        * Configuration file exists
        """
        return self.folder.exists() and self.config_file.exists()

    def ensure_exists(self):
        if self.exists() and self.is_valid():
            return
        else:
            self.create()

    def is_valid(self):
        """Check if:
        * The folder, files exist
        * The git repo it is referring to exists
        * The location is read/write accessible
        TODO (OS): Improve error messages
        """
        if not self.exists():
            return False, "Config folder does not exist"
        valid, err = self.config_file.is_valid() 
        if not valid:
            return False, err
        if not os.access(self.folder.path, os.R_OK):
            return False, "Destination folder not readable"
        if not os.access(self.folder.path, os.W_OK):
            return False, "Destination folder not writeable"
        return True, ""

    def create(self, overwrite=False):
        """Crates a new folder. If an old one exists, pushes it to backup."""
        # Set up root
        self.folder.ensure_exists()
        # Clean up previous backups, if they exist
        if not overwrite:
            self.push_backup()
        # Set up backup
        self.folder.child(self.backup_folder_name).ensure_exists()
        self.config_file.create()

    def destroy(self):
        self.pop_backup()
        #TODO (OS): check if folder needs to be removed

    def push_backup(self):
        """
        If a backup folder exists, moves the configuration file into it,
        and upadtes the name to be the latest archived backup.
        Does not create new backup folder.
        """
        master = self.folder.child(self.backup_folder_name)
        if not master.exists():
            return
        #find latest
        next_archived_backup = self.find_latest_backup_number() + 1
        # move config file into backup folder
        archived_backup_folder_name = "%s.%02d" % ( consts.BACKUP_DIR_NAME, next_archived_backup )
        master.rename(archived_backup_folder_name)
        self.config_file.copy_to(
            os.path.realpath(
                os.path.join(
                    self.folder.path,
                    archived_backup_folder_name,
                    consts.USER_CONFIG_FILE_NAME
                )
            )
        )

    def pop_backup(self):
        """
        If an archived folder exists, deletes the current backup folder and configuration file,
        and replaces them with the most recent archived backup and
        configuration file inside the archived backup.
        """
        archive_num = self.find_latest_backup_number()
        if archive_num == 0:
            return

        #TODO (OS): Before moving on, remove things installed with current conig?

        archived_backup_folder_name = consts.BACKUP_DIR_NAME + "." + archive_num
        archived_backup_folder = self.folder.child(archived_backup_folder_name)
        if not archived_backup_folder.exists():
            return
        # remove current setup
        self.folder.child(self.backup_folder_name).delete()
        # make the latest one "current"
        archived_backup_folder.rename(self.backup_folder_name)
        archived_user_config_file_path = os.path.realpath(
            os.path.join(
                self.folder.child(self.backup_folder_name).path,
                consts.USER_CONFIG_FILE_NAME
            )
        )
        #replace contents of config file with arcchived version
        self.config_file.read_from(archived_user_config_file_path)
        #delete config file from popped folder
        os.remove(archived_user_config_file_path)
        # will return false if can't complete

    def find_latest_backup_number(self):
        """
        Scans the backup folders to see if previous backups exist.
        Unable to detect different versions of file and folder.
        """
        names = [n for n in self.folder.child_names(files=False)
                    if (n.startswith(consts.BACKUP_DIR_NAME)
                    and not n.endswith(consts.CONFIG_EXTENSION_CURRENT))]
        highest_num = 0
        for name in names:
            #take last string beyond point
            numstr = name.split(".")[-1]
            try:
                highest_num = max(highest_num, int(numstr))
            except:
                pass
        return highest_num

    def get_bait_config(self, bait_name):
        """Searches for a bait in the active repo. If none exist, returns `None`."""
        child = self.folder.child(bait_name)
        if not child.exists():
            return None
        bait = Bait(child.path)
        #TODO (OS): Determine if this is a legitimate 
        return bait
