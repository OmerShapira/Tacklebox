"""
Commands for staging: hook, unhook, collect
"""
from core import fileutils
from core.configutils import UserConfigFolder

def hook(args):
    """
    Attempts to execute `hook`. Will quit upon any error before operation.
    if an error occurs upon execution, will dump errors to log, but not clean up.
    """
    config_folder = UserConfigFolder().load()
    bait_cfg = config_folder.get_bait_config(args.name)
    if not bait_cfg:
        errmsg = "A bait called %s does not exist in the active repo." % args.bait_name
        exit(errmsg)

    #check if already deployed
    if args.bait_name in config_folder.config_file['bait']:
        #TODO (OS): check bait validity
        #TODO (OS): check if already deployed, quit if --push not entered
        errmsg = "A bait called %s is marked as already deployed." % args.bait_name
        exit(errmsg)

    #check if bait knows where to go
    target_path = args.target
    if target_path and not args.push:
        """TODO (OS): this method isn't well-specified: what if this only deploys .vimrc
        inside `~/`?"""
        raise NotImplementedError("Prompt override")
    else:
        target_path = bait_cfg.config_file['target']['root']
    if not target_path:
        errmsg = "Target path for %s isn't specified" % bait_cfg.name()
        exit(errmsg)

    target_folder = fileutils.Folder(target_path)
    #check if target path can be backed up and modified
    if not fileutils.is_read_write_accessible(target_folder.path):
        errmsg = "The path %s is required to be read/write acessible to deploy `%s`" % target_folder.path, args.bait_name
        exit(errmsg)

    #check disk space for deploy
    result, err = fileutils.check_size_before_transfer(bait_cfg.folder.path,target_folder.path)
    if not result:
        exit(err)
    #if target path does not exist, quit
    #if --push, check if backup size is reasonable
    if args.push:
        result, err = fileutils.check_size_before_transfer(target_folder.path, config_folder.backup_folder_path)
        if not result:
            errmsg = "Cannot execute backup for %s : %s" % target_folder.path, err
            exit(errmsg)
            #if --push entered, back up
        else:
            raise NotImplementedError("Implement backup")

    #create all files in list, storing created files in cleanup list inside config
    # copy files, update list
    copied_files, errors = fileutils.copy_files_list_results(bait_cfg.path, target_path)
    # dump list to config
    with config_folder.config_file.mutable():
        current_copied = config_folder.config_file['bait'][args.bait_name]['paths_created'] or []
        config_folder.config_file['bait'][args.bait_name]['paths_created'] = copied_files + current_copied


def unhook(args):
    #check if bait name exists and is deployed.
    config_folder = UserConfigFolder().load()
    bait_cfg = config_folder.get_bait_config(args.name)
    if not bait_cfg:
        errmsg = "A bait called %s does not exist in the active repo." % args.bait_name
        exit(errmsg)

    #TODO (OS): check if files modified, prompt for change

    #traverse list and remove, updating bait only in the end.
    remain = fileutils.remove_files(created_paths)
    #forgive if files don't exist (reason: unhook may have failed and not updated config)
    if len(remain):
        #TODO (OS): Move to a formatting function
        import operator.add
        remain_formatted = reduce(operator.add, ["\t%s\n" % path for path in remain], "")
        errmsg = "Can't pop backup for %s: failed to remove the following paths:\n%s" % args.name, remain_formatted
        raise Exception(errmsg)
    #check if backup exists
    #TODO(OS): pop and stage backup (not asking user)

def collect(args):
    #glob new files
    #compare old files (hash?)
    #copy to repo, using a reltive path
    #git commit -am all the files
    pass
