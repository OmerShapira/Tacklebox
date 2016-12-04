"""File and Folder wrappers"""
import os
from contextlib import contextmanager
from collections import MutableMapping
import shutil #used for rmtree
from time import time

import toml

from consts import consts


class FileWrapper(object):
    def __init__(self, path, mode, warn_if_created=False):
        self.warn_if_created = warn_if_created
        self.mode = mode
        self.set_path(path)
        self.handle = None

    def set_path(self, path):
        self.path = os.path.realpath(path)
        self.dirname, self.filename = os.path.split(path)

    def ensure_path_exists(self):
        if os.path.exists(self.dirname):
            return
        try:
            os.makedirs(self.dirname)
        except IOError as E: #TODO (OS): not only possible error
            raise

    def exists(self):
        return os.path.exists(self.path)

    def touch(self):
        #TODO (OS): Needed?
        if os.path.exists(self.path):
            return
        try:
            self.ensure_path_exists()
            handle = open(self.path)
            handle.close()
        except IOError as E:
            raise

    def delete(self):
        return os.remove(self.path)

    def rename(self, new_name):
        new_path = os.path.realpath (os.path.join( self.path, new_name ))
        if os.path.exists(new_path):
            raise Exception("Can't rename to existing file")
        if self.exists():
            os.rename(self.path, new_path)
        self.set_path(new_path)

    def __enter__(self):
        self.ensure_path_exists()
        if self.warn_if_created:
            print "Creating " + self.path
        self.handle = open(self.path, self.mode)
        return self.handle

    def __exit__(self, exc_type, exc_value, exc_tb):
        self.handle.close()


class Folder(object):
    def __init__(self, path):
        if os.path.isfile(path):
            raise TypeError("% is a file")
        self.path = os.path.realpath(path)

    def exists(self):
        return os.path.exists(self.path) and os.path.isdir(self.path)

    def ensure_exists(self):
        if self.exists():
            return
        try:
            os.makedirs(self.path)
        except IOError as E:
            raise

    def rename(self, new_name):
        parent = os.path.join(self.path, os.pardir)
        new_path = os.path.realpath(os.path.join(parent, new_name))
        #check that nothing in the new name exists
        if new_path == self.path:
            return
        if os.path.exists(new_path):
            #TODO (OS): Not sure which exception to raise
            raise Exception("Path Exists")
        try:
            os.rename(self.path, new_path)
            self.path = new_path
        except IOError as E:
            raise

    def delete(self):
        return shutil.rmtree(self.path) 

    def child(self, name):
        return Folder(os.path.join(self.path, name))

    def parent(self):
        return Folder(os.path.realpath(os.path.join(self.path, os.pardir)))

    def child_names(self, dirs=True, files=True):
        raw = os.listdir(self.path)
        if files and dirs:
            return raw
        l_files = [] if not files else [f for f in raw if os.path.isfile(f)]
        l_dirs  = [] if not dirs  else [d for d in raw if os.path.isdir(d)]
        return l_files + l_dirs


class UserConfigFolder(object):
    """Docstrring for UserConfigFolder"""
    def __init__(self, repo_path, path=None):
        path = os.path.expanduser(consts.USER_CONFIG_HOME)
        self.folder = Folder(path)
        self.backup_folder_name = consts.BACKUP_DIR_NAME + consts.CONFIG_EXTENSION_CURRENT
        self.config_file_name = consts.USER_CONFIG_FILE_NAME
        self.config_file = UserConfigFile(self, repo_path)

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
        """
        ret = True
        ret &= self.exists()
        ret &= self.config_file.is_valid() 
        ret &= os.access(self.folder.path, os.R_OK)
        ret &= os.access(self.folder.path, os.W_OK)
        return ret

    def create(self):
        """Crates a new folder. If an old one exists, pushes it to backup."""
        # Set up root
        self.folder.ensure_exists()
        # Clean up previous backups, if they exist
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
        # TODO (OS): move config file into backup
        archived_backup_folder_name = consts.BACKUP_DIR_NAME + "." + next_archived_backup
        master.rename(archived_backup_folder_name)

    def pop_backup(self):
        """
        If an archived folder exists, deletes the current backup folder and configuration file,
        and replaces them with the most recent archived backup and
        configuration file inside the archived backup.
        """
        archive_num = self.find_latest_backup_number()
        if archive_num == 0:
            return
        archived_backup_folder_name = consts.BACKUP_DIR_NAME + "." + archive_num
        archived_backup_folder = self.folder.child(archived_backup_folder_name)
        if not archived_backup_folder.exists():
            return
        # remove current setup
        self.folder.child(self.backup_folder_name).delete()
        # make the latest one "current"
        archived_backup_folder.rename(self.backup_folder_name)
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
            except E:
                pass
        return highest_num

## Some Decorators

def reload_if_stale(fn):
    """Decorator to reload a protected file before exposing values"""
    def fresh(self, *args):
        if self.is_stale() and not self.lock:
            self.load()
        return fn(self, *args)
    return fresh

def check_lock_mark_dirty(fn):
    """Decorator to allow protected file access"""
    def checked(self, *args):
        if self.lock:
            return ValueError("Object is locked. use .mutable instead")
        fn(self, *args)
        self.dirty = True
    return checked


class ConfigFile(MutableMapping):
    """Efficient disk-mapped TOML file wrapper"""
    def __init__(self, path):
        self.path = path
        if not os.path.exists(path):
            raise ValueError(path + "Doesn't exist")
        self.__db = {}
        self.lock = True
        self.dirty = True
        self.__last_load = .0
        self.load()

    @reload_if_stale
    def __getitem__(self, key):
        # TODO(OS): child dicts still mutable
        return self.__db.__getitem__(key)

    @reload_if_stale
    def __contains__(self, key):
        return self.__db.__contains__(key)

    @reload_if_stale
    def __len__(self):
        return self.__db.__len__()

    @reload_if_stale
    def __iter__(self):
        return self.__db.__iter__()

    @check_lock_mark_dirty
    def __setitem__(self, key, value):
        self.__db.__setitem__(key, value)

    @check_lock_mark_dirty
    def __delitem__(self, key):
        self.__db.__delitem__(key)

    def exists(self):
        return os.path.exists(self.path)

    def load(self):
        """Cache the file onto self.__db, and mark the time it was loaded"""
        with open(self.path, 'r') as f:
            self.__db = toml.load(f)
            self.__last_load = time()

    def clear(self):
        """deletes both the cache and the disk file contents. leaves an empty file
        creates an empty file if didn't exist."""
        with self.mutable():
            self.__db = {}

    def is_stale(self):
        return self.__last_load < os.path.getmtime(self.path)

    @contextmanager
    def mutable(self):
        """NOT THREAD SAFE. FFS. DON'T."""
        # First, refresh the file
        if self.is_stale():
            try:
                self.load()
            except IOError as E:
                #All this means is the file doesn't exist, we just create one
                pass
        self.lock = False
        yield self
        with open(self.path, 'w') as f:
            self.__db = toml.dump(self.__db, f)
        self.lock = True
        self.dirty = False


class BaitConfigFile(ConfigFile):
    def __init__(self, path):
        # Find if is local root
        super(BaitConfigFile, self).__init__(path)

class UserConfigFile(ConfigFile):
    '''refers to user config file only by name.
    performs atomic actions and keeps file closed.'''
    def __init__(self, config_folder, repo_path):
        path = os.path.join(
            self.path.expanduser(consts.USER_CONFIG_HOME),
            consts.USER_CONFIG_FILE_NAME)
        super(UserConfigFile, self).__init__(self, path)
        #TODO (OS): remove coupling
        self.config_folder = config_folder
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


    def is_valid(self):
        if not self.does_point_to_git_repo():
            return False
        try:
            pv, fv = consts.VERSION, self['version']
            assert pv == fv, "Config file version ("+fv+") does not match the program version ("+pv+")"
            root = self['repo']['master']['root']
            assert is_git_repo(root), root + " is not a git repo"
        except AssertionError as E:
            print "Error: " + E
            return False
        except E:
            print "Unknown Error: " + E
            return False
        return True

    def does_point_to_git_repo(self):
        """Checks only by name. If you're gonna play evil, I'm not going to catch it."""
        return is_git_repo(self.repo_path)

def is_git_repo(path):
    repo_path = os.path.join(path, ".git")
    if not os.path.exists(repo_path):
        return False
    #TODO (OS): actually check repo
    return True
