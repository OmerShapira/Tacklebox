# Tacklebox
Tacklebox is a configuration manager for people working on multiple computers. It handles:
* Making your local settings portable
* Updating any changes you make to your settings back into your collection
* Backing up anyone else's local settings while you work
* Searching snippets and other things you need
* Cleaning up after you're done with a computer

Tacklebox uses git as a backend. Any changes you make will be pushed back into your remote git repository.
## Usage

``` bash
tackle
# (usage)

tackle hook all
# stages all baits (packages)
tackle hook vimrc
# stages vimrc, backing up the previous one if it exists
tackle hook --overwrite vimrc
# stages vimrc without backing up previous versions.
tackle unhook vimrc
# unstages vimrc, restoring backups.

tackle fetch
# (pull changes from main repo)
tackle refresh [bait/file]
# (deploy changes)
tackle collect [bait/file]
# (collects changes to baits and pushes them)

tackle inventory
# (shows baits)

tackle bait --new NAME [PATH]
# starts a new bait with NAME in the current config.
# if PATH is added, marks any files added from local machine to be left there when done.

tackle bait --local
# tags a bait that's already inside a repo


tackle snip glsl
# (returns a list of all glsl snippets)
tackle snip glsl/noise
# (prints glsl/noise.glsl into the console)
tackle snip -c glsl/noise
tackle clip glsl/noise
# copies glsl/noise snippet to clipboard

tackle wipe 
# clear everything from the computer

```

## #Goals
Since Tacklebox was designed with a specific use case in mind, it also comes with an aesthetic. It needs to:
* Be dead simple for anyone already used to git
* Be fast and helpful, not full of obscure features.
* Support other repos, like `svn`, `dropbox`, or `http` (to allow for a repo just for your private keys, and one you share with your organization)
* Once stable, change as little as possible.
* Allow editor integration, because we all love ordering ramen through emacs.
* Be stable for as long as possible, never destroy anybody's hard drive.

## FAQs
### Why?
I work on different platforms, different computers and different editors. Spending hours reconfiguring environments has become a hassle. Asking around, I saw most people I know will go out of their way to avoid this. So I decided to help!

### Is this a new package manager?
No. There are plenty of those! Some are good. This just holds _your_ stuff, and stuff you thought you might want to hold on to but never turn into a package.

### Why Python? Why Python 2?
Tacklebox wants to run everywhere, so python seemed obvious. Also, most pipeline programmers already know python, and they're likely to need this a lot.

### This isn't terrible. Can I help?
Yes.


