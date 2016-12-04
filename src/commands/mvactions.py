
import os
import sys

"""
This module shall contain put/pop actions
"""
def with_permissions_checked(staged, backup):
    def checked(fn):
        #TODO: DO stuff with staged, backup
        def wrapped(*args, **kwargs):
            fn(*args, **kwargs)
        return wrapped
    return checked

def hook(cl_args):
    '''
    If destination path is alrady specified:
        * if never been used, verify it's correct
        * otherwise, proceed to execute
    Else:
        * EXIT, ask for directory
    '''
    pass

def unhook(cl_args):
    pass


def collect(cl_args):
    pass

class op_file_placement:
    def __init__(self, source_dir, backup_dir):
        pass

    def execute(self):
        """
        check if target folder can accept files
        check if target folder needs backup
        check write permissions
        acquire locks
        exchange new files
        """
        pass

    @with_permissions_checked(staged=False, backup=True)
    def move_to_backup(self):
        pass

    @with_permissions_checked(staged=True, backup=False)
    def move_from_backup(self):
        pass

    def get_backup_pointer(self):
        #filter backup folder by .tacklebait.###
        pass

