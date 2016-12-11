"""
Commands for staging: hook, unhook
"""
from core.fileutils import *
from core.configutils import UserConfigFolder

def hook(args):
    #load config folder
    config_folder = UserConfigFolder().load()
    #check if bait name exists
    bait_cfg = config_folder.get_bait_config(args.name)
    if not bait_cfg:
        #TODO (OS): include active repo name
        exit("A bait called '"+args.bait_name+"' does not exist in the active repo.")
    #check if already deployed
    if args.bait_name in config_folder.config_file['bait']:
        #TODO (OS): check bait validity
        pass
    #check if target path exists, quit if --push not entered
    #TODO (OS): bait file target should be an option too
    target_path = args.target
    if not target_path:
        exit("Target path for '" + bait_cfg.name() +"' isn't specified")
    target_folder = Folder(target_path)
    #check if bait knows where to go
    #check if target path can be backed up and modified
    
    #check disk space for deploy
    # result, err = check_size_before_transfer()
    #if target path does not exist, quit
    #if --push, check if backup size is reasonable
    #if --push entered, back up
    #create all files in list, storing created files in cleanup list inside config

def unhook(args):
    #check if bait name exists and is deployed.
    #check permissions for unhook, quit if not exist
    #TODO (OS): check if files modified, prompt for change
    #traverse list and remove, updating bait only in the end.
    #forgive if files don't exist (reason: unhook may have failed and not updated config)
    #check if backup exists
    #pop and stage backup (not asking user)
    pass

def collect(args):
    #glob new files
    #compare old files (hash?)
    #copy to repo, using a reltive path
    #git commit -am all the files
    pass
