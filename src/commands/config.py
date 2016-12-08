"""Tacklebox v0.01
Written by Omer Shapira"""


import os
from core.configutils import UserConfigFolder


ERRMSG_CONFIG_EXISTS = """
User folder already has a valid configuration in place.\n
To push a backup use:\n
\t\ttackle conifg --new\n
To overwrite the current one, use:\n
\t\ttackle config --overwrite\n"""

def config(args):
    '''Handle the 'config' command'''

    # Check if path exists
    repo_path = os.path.realpath(args.repo)
    if not os.path.exists(repo_path):
        exit("Path does not exist: " + repo_path )

    config_folder = UserConfigFolder(repo_path=repo_path)

    valid, err = config_folder.is_valid()

    #if there's already a config there, exit asking for --new or --overwrite
    if valid and not (args.new or args.overwrite):
        exit(ERRMSG_CONFIG_EXISTS)

    if not valid:
        print "Error: " + err

    config_folder.create(overwrite=args.overwrite)
    exit("Created config folder for: " + repo_path)



