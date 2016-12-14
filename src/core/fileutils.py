"""File and Folder wrappers"""
import os
import sys
import ctypes
from contextlib import contextmanager
from collections import MutableMapping
import shutil #used for rmtree
from time import time

import toml

from consts import consts


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
        if os.path.relpath ( new_path, self.path ) == os.curdir:
            return
        if os.path.exists(new_path):
            #TODO (OS): Not sure which exception to raise
            raise Exception("Target for renaming to already exists: " + new_path)
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

    def folder_name(self):
        if not self.exists():
            return None
        return  os.path.relpath(self.path, self.parent().path)



class MemoryMappedTOMLFile(MutableMapping):
    """Efficient disk-mapped TOML file wrapper"""
    def __init__(self, path):
        self.path = path
        # if not os.path.exists(path):
            # raise ValueError(path + " Doesn't exist")
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
        if not os.path.exists(self.path):
            #TODO (OS): Figure out what to do here. 
            return
        with open(self.path, 'r') as f:
            self.__db = toml.load(f)
            self.__last_load = time()

    def save_if_dirty(self):
        if self.dirty:
            self.lock = False
            with open(self.path, 'w') as f:
                self.__db = toml.dump(self.__db, f)
                self.dirty = False
            self.lock = True

    def clear(self):
        """deletes both the cache and the disk file contents. leaves an empty file
        creates an empty file if didn't exist."""
        with self.mutable():
            #TODO (OS): Will not mark as dirty without excplicityly stating
            self.__db = {}
            self.dirty = True

    def copy_to(self, path):
        real_path = os.path.realpath(path)
        shutil.copy(self.path, real_path)

    def read_from(self,path):
        """If `path` exists, erases current file (if exists) and rewrite a new one"""
        real_path = os.path.realpath(path)
        if not (os.path.exists(real_path) and os.access(real_path, os.R_OK)):
            raise IOError(real_path + "Does not exist or is not accessible")
        if os.path.exists(self.path):
            #NOTE (OS): Will not delete directories
            os.remove(self.path)
        shutil.copyfile(real_path, self.path)

    def is_stale(self):
        if not self.exists():
            return True
        return self.__last_load < os.path.getmtime(self.path)

    @contextmanager
    def mutable(self):
        """NOT THREAD SAFE. FFS. DON'T."""
        # First, refresh the file
        if self.is_stale():
            try:
                self.load()
            except IOError:
                #All this means is the file doesn't exist, we just create one
                pass
        self.lock = False
        yield self
        self.save_if_dirty()

def is_git_repo(path):
    repo_path = os.path.join(path, ".git")
    if not os.path.exists(repo_path):
        return False
    #TODO (OS): actually check repo
    return True


def is_read_write_accessible(path):
    """Should only be used as a sanity check.
    see: https://docs.python.org/2/library/os.html
    """
    return os.access(path, os.R_OK or os.W_OK)

def get_free_disk_space_bytes(path):
    drive, _ = os.path.splitdrive(os.path.realpath(path)) 
    if os.name is 'nt':
        free_bytes_avil = ctypes.c_ulong()
        total_bytes = ctypes.c_ulong()
        total_free_bytes = ctypes.c_ulong()
        ctypes.windll.kernel32.GetFreeDiskSpaceExA(
            drive,
            ctypes.byref(free_bytes_avil),
            ctypes.byref(total_bytes),
            ctypes.byref(total_free_bytes))
        return total_free_bytes.value
    elif os.name is 'posix':
        stat = os.statvfs(drive)
        # http://stackoverflow.com/questions/787776/find-free-disk-space-in-python-on-os-x
        return (stat.f_bavail * stat.f_frsize) / 1024
    else:
        #OS not recognised?
        raise Exception ("OS not recognised")

def check_size_before_transfer(path_src, path_dst):
    """
    Check if the transfer is safe to perform.
    Will prompt the user if the file sizes exceed limits set in 'consts.py'
    Returns (result, reason) where result is boolean and reason is a message.
    """
    size_src = os.path.getsize(path_src)
    free_dst = get_free_disk_space_bytes(path_dst)
    SCALE_MB = 1<<20
    size_mb = size_src / SCALE_MB
    free_mb = free_dst / SCALE_MB
    if size_src > free_dst:
        msg = "This will require %d MB of space, but the destination drive\
        only has %d MB available" % size_mb, free_mb
        return False, msg
    if size_mb + consts.WARN_IF_DESTINATION_SPACE_AFTER_LE_MB >= free_mb:
        #TODO (OS): Should prompt here
        raise NotImplementedError
    if size_mb >= consts.WARN_IF_SIZE_GE_MB:
        #TODO (OS): SHould prompt here
        raise NotImplementedError
    return True, ""

def copy_files_list_results(src, dst):
    """Copies tree and returns a list of copied files (absolute path) and errors"""
    src = os.path.realpath(src)
    dst = os.path.realpath(dst)
    copied_files = []
    errors = []

    names = os.listdir(src)
    
    #TODO (OS): FINISH THIS

    return copied_files, errors

