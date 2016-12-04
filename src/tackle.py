"""Tacklebox v 0.01
Written by Omer Shapira

"""
import os
import ctypes           #for windows admin checking
import argparse

# Modules
from commands import config, mvactions


def halt_if_admin():
    """Quits if the user is admin."""
    try:
        is_admin = os.getuid() == 0
    except AttributeError:
        is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0

    if is_admin:
        exit("Tacklebox won't run under admin privilieges. You might hurt yourself.")


def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(help="Options:")

    parser_config = subparsers.add_parser('config', help="configure the project")
    parser_config.add_argument('path', type=str)
    parser_config.set_defaults(func=config.config)

    parser_hook = subparsers.add_parser('hook', help="put an asset in place, backing up the old one, if it exists")
    parser_hook.add_argument('config_name', type=str, action='store')
    parser_hook.add_argument('--path', type=str, action='store')

    parser_unhook = subparsers.add_parser('unhook', help="remove an asset, restore the previous one from backup if possible")
    parser_unhook.add_argument('config_name')

    parser_fetch = subparsers.add_parser('fetch', help="pull the latest from remote repository, point repository to head of the current branch.")

    parser_refresh = subparsers.add_parser('refresh', help="put most recent assets for all currently deployed assets, backing up current ones.")

    parser_collect = subparsers.add_parser('collect', help="adds a deployed asset into the repository and pushes to the remote repository, if exists.")

    parser_snip = subparsers.add_parser('snip', help="pastes a snippet")
    parser_clip = subparsers.add_parser('clip', help="pastes a snippet into the clipboard")

    # Read
    args = parser.parse_args()

    # Safety check
    halt_if_admin()

    # Execute!
    args.func(args)


if __name__ == "__main__":
    main()
