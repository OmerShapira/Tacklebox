"""Tacklebox v0.01
Written by Omer Shapira"""


import os
from core.fileutils import UserConfigFolder

def config(args):
    '''Handle the 'config' command'''
    # Check if path exists
    if not os.path.exists(args.path):
        exit("Path does not exist: " + args.path )
    path = os.path.realpath(args.path)
    config_folder = UserConfigFolder(args.path)
    #if there's already a config there, exit asking for --new or --push
    valid = config_folder.is_valid()
    if valid and not ('new' in args or 'overwrite' in args):
            exit("""User folder already has a valid configuration in place.\n
            To push a backup use:\n
            \t\ttackle conifg --new\n
            To overwrite the current one, use:
            \t\ttackle config --overwrite\n
            """)
    config_folder.create()
    exit("Created config folder for: " + args.path)




