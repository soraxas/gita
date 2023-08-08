[![PyPi version](https://img.shields.io/pypi/v/gita.svg?color=blue)](https://pypi.org/project/gita/)
[![Build Status](https://travis-ci.org/nosarthur/gita.svg?branch=master)](https://travis-ci.org/nosarthur/gita)
[![codecov](https://codecov.io/gh/nosarthur/gita/branch/master/graph/badge.svg)](https://codecov.io/gh/nosarthur/gita)
[![licence](https://img.shields.io/pypi/l/gita.svg)](https://github.com/nosarthur/gita/blob/master/LICENSE)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/gita.svg)](https://pypistats.org/packages/gita)
[![Gitter](https://badges.gitter.im/nosarthur/gita.svg)](https://gitter.im/nosarthur/gita?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge)
[![Chinese](https://img.shields.io/badge/-中文-lightgrey.svg)](https://github.com/nosarthur/gita/blob/master/doc/README_CN.md)

```
 _______________________________
(  ____ \__   __|__   __(  ___  )
| (    \/  ) (     ) (  | (   ) |
| |        | |     | |  | (___) |
| | ____   | |     | |  |  ___  |
| | \_  )  | |     | |  | (   ) |
| (___) |__) (___  | |  | )   ( |
(_______)_______/  )_(  |/     \|   v0.16
```

# Gita: a command-line tool to manage multiple git repos

This tool has two main features

- display the status of multiple git repos such as branch, modification, commit message side by side
- (batch) delegate git commands/aliases and shell commands on repos from any working directory

![gita screenshot](https://github.com/nosarthur/gita/raw/master/doc/screenshot.png)

In this screenshot, the `gita ll` command displays the status of all repos.
The `gita remote dotfiles` command translates to `git remote -v`
for the `dotfiles` repo, even though we are not in the repo.
The `gita fetch` command fetches from all repos and two of them have updates.
To see the pre-defined commands, run `gita -h` or take a look at
[cmds.json](https://github.com/nosarthur/gita/blob/master/gita/cmds.json).
To add your own commands, see the [customization section](#custom).
To run arbitrary `git` command, see the [superman mode section](#superman).
To run arbitrary shell command, see the [shell mode section](#shell).

I also made a youtube video to demonstrate the common usages
[![Img alt text](https://github.com/nosarthur/gita/raw/master/doc/video-outline.png)](https://www.youtube.com/watch?v=ySWbwQcbhqI)

The branch color distinguishes 5 situations between local and remote branches:

color | meaning
---|---
 white| local has no remote
 green| local is the same as remote
 red| local has diverged from remote
 purple| local is ahead of remote (good for push)
 yellow| local is behind remote (good for merge)

The choice of purple for ahead and yellow for behind is motivated by
[blueshift](https://en.wikipedia.org/wiki/Blueshift) and [redshift](https://en.wikipedia.org/wiki/Redshift),
using green as baseline.
You can change the color scheme using the `gita color` command.
See the [customization section](#custom).

The additional status symbols denote

symbol | meaning
---|---
 `+`| staged changes
 `*`| unstaged changes
 `?`| untracked files/folders
 `$`| stashed contents

The bookkeeping sub-commands are

- `gita add <repo-path(s)> [-g <groupname>]`: add repo(s) to `gita`, optionally into an existing group
- `gita add -a <repo-parent-path(s)>`: add repo(s) in <repo-parent-path(s)> recursively
  and automatically generate hierarchical groups. See the [customization section](#custom) for more details.
- `gita add -b <bare-repo-path(s)>`: add bare repo(s) to `gita`. See the [customization section](#custom) for more details on setting custom worktree.
- `gita add -r <repo-parent-path(s)>`: add repo(s) in <repo-parent-path(s)> recursively
- `gita clear`: remove all groups and repos
- `gita clone <URL>`: clone repo from `URL` at current working directory
- `gita clone <URL> -C <directory>`: change to `directory` and then clone repo
- `gita clone -f <config-file>`: clone repos in `config-file` (generated by `gita freeze`) to current directory.
- `gita clone -p -f <config-file>`: clone repos in `config-file` to prescribed paths.
- `gita context`: context sub-command
    - `gita context`: show current context
    - `gita context <group-name>`: set context to `group-name`, all operations then only apply to repos in this group
    - `gita context auto`: set context automatically according to the current working directory
    - `gita context none`: remove context
- `gita color`: color sub-command
    - `gita color [ll]`: Show available colors and the current coloring scheme
    - `gita color reset`: Reset to the default coloring scheme
    - `gita color set <situation> <color>`: Use the specified color for the local-remote situation
- `gita flags`: flags sub-command
    - `gita flags set <repo-name> <flags>`: add custom `flags` to repo
    - `gita flags [ll]`: display repos with custom flags
- `gita freeze`: print information of all repos such as URL, name, and path. Use with
  `gita clone`.
- `gita group`: group sub-command
    - `gita group add <repo-name(s)> -n <group-name>`: add repo(s) to a new or existing group
    - `gita group [ll]`: display existing groups with repos
    - `gita group ls`: display existing group names
    - `gita group rename <group-name> <new-name>`: change group name
    - `gita group rm <group-name(s)>`: delete group(s)
    - `gita group rmrepo <repo-name(s)> -n <group-name>`: remove repo(s) from existing group
- `gita info`: info sub-command
    - `gita info [ll]`: display the used and unused information items
    - `gita info add <info-item>`: enable information item
    - `gita info rm <info-item>`: disable information item
- `gita ll`: display the status of all repos
- `gita ll <group-name>`: display the status of repos in a group
- `gita ll -g`: display the repo summaries by groups
- `gita ls`: display the names of all repos
- `gita ls <repo-name>`: display the absolute path of one repo
- `gita rename <repo-name> <new-name>`: rename a repo
- `gita rm <repo-name(s)>`: remove repo(s) from `gita` (won't remove files on disk)
- `gita -v`: display gita version

The `git` delegating sub-commands are of two formats

- `gita <sub-command> [repo-name(s) or group-name(s)]`:
  optional repo or group input, and **no input means all repos**.
- `gita <sub-command> <repo-name(s) or groups-name(s)>`:
  required repo name(s) or group name(s) input

They translate to `git <sub-command>` for the corresponding repos.
By default, only `fetch` and `pull` take optional input. In other words,
`gita fetch` and `gita pull` apply to all repos.
To see the pre-defined sub-commands, run `gita -h` or take a look at
[cmds.json](https://github.com/nosarthur/gita/blob/master/gita/cmds.json).
To add your own sub-commands or override the default behaviors, see the [customization section](#custom).
To run arbitrary `git` command, see the [superman mode section](#superman).

If more than one repos are specified, the `git` command runs asynchronously,
with the exception of `log`, `difftool` and `mergetool`,
which require non-trivial user input.

Repo configuration global is saved in `$XDG_CONFIG_HOME/gita/repos.csv`
(most likely `~/.config/gita/repos.csv`) or if you prefered at project configuration add environment variable `GITA_PROJECT_HOME`.

## Installation

To install the latest version, run

```
pip3 install -U gita
```

If you prefer development mode, download the source code and run

```
pip3 install -e <gita-source-folder>
```

In either case, calling `gita` in terminal may not work,
then put the following line in the `.bashrc` file.

```
alias gita="python3 -m gita"
```

Windows users may need to enable the ANSI escape sequence in terminal for
the branch color to work.
See [this stackoverflow post](https://stackoverflow.com/questions/51680709/colored-text-output-in-powershell-console-using-ansi-vt100-codes) for details.

## Auto-completion

Download
[.gita-completion.bash](https://github.com/nosarthur/gita/blob/master/.gita-completion.bash)
or
[.gita-completion.zsh](https://github.com/nosarthur/gita/blob/master/.gita-completion.zsh)
and source it in shell.

## <a name='superman'></a> Superman mode

The superman mode delegates any `git` command or alias.
Usage:

```
gita super [repo-name(s) or group-name(s)] <any-git-command-with-or-without-options>
```

Here `repo-name(s)` or `group-name(s)` are optional, and their absence means all repos.
For example,

- `gita super checkout master` puts all repos on the master branch
- `gita super frontend-repo backend-repo commit -am 'implement a new feature'`
  executes `git commit -am 'implement a new feature'` for `frontend-repo` and `backend-repo`

## <a name='shell'></a> Shell mode

The shell mode delegates any shell command.
Usage:

```
gita shell [repo-name(s) or group-name(s)] <any-shell-command>
```

Here `repo-name(s)` or `group-name(s)` are optional, and their absence means all repos.
For example,

- `gita shell ll` lists contents for all repos
- `gita shell repo1 repo2 mkdir docs` create a new directory `docs` in `repo1` and `repo2`
- `gita shell "git describe --abbrev=0 --tags | xargs git checkout"`: check out the latest tag for all repos

## <a name='custom'></a> Customization

### define repo group and context

When the project contains several independent but related repos,
we can define a group and execute `gita` command on this group.
For example,

```
gita group add repo1 repo2 -n my-group
gita ll my-group
gita pull my-group
```

To save more typing, one can set a group as context, then any `gita` command
is scoped to the group

```
gita context my-group
gita ll
gita pull
```

The most useful context  maybe `auto`.
In this mode, the context is automatically determined from the
current working directory (CWD): the context is the group whose member repo's
path contains CWD. To set it, run

```
gita context auto
```

To remove the context, run
```
gita context none
```

It is also possible to recursively add repos within a directory and
generate hierarchical groups automatically. For example, running

```
gita add -a src
```
on the following folder structure
```
src
├── project1
│   ├── repo1
│   └── repo2
├── repo3
├── project2
│   ├── repo4
│   └── repo5
└── repo6
```
gives rise to 3 groups:
```
src:repo1,repo2,repo3,repo4,repo5,repo6
src-project1:repo1,repo2
src-project2:repo4,repo5
```

### add user-defined sub-command using json file

Custom delegating sub-commands can be defined in `$XDG_CONFIG_HOME/gita/cmds.json`
(most likely `~/.config/gita/cmds.json`)
And they shadow the default ones if name collisions exist.

Default delegating sub-commands are defined in
[cmds.json](https://github.com/nosarthur/gita/blob/master/gita/cmds.json).
For example, `gita stat <repo-name(s)>` is registered as

```json
"stat":{
  "cmd": "git diff --stat",
  "help": "show edit statistics"
}
```

which executes `git diff --stat` for the specified repo(s).

To disable asynchronous execution, set `disable_async` to be `true`.
See the `difftool` example:

```json
"difftool":{
  "cmd": "git difftool",
  "disable_async": true,
  "help": "show differences using a tool"
}
```

If you want a custom command to behave like `gita fetch`, i.e., to apply to all
repos when no repo is specified, set `allow_all` to be `true`.
For example, the following snippet creates a new command
`gita comaster [repo-name(s)]` with optional repo name input.

```json
"comaster":{
  "cmd": "checkout master",
  "allow_all": true,
  "help": "checkout the master branch"
}
```

Any command that runs in the [superman mode](#superman) mode or the
[shell mode](#shell) can be defined in this json format.
For example, the following command runs in shell mode and fetches only the
current branch from upstream.

```json
"fetchcrt":{
  "cmd": "git rev-parse --abbrev-ref HEAD | xargs git fetch --prune upstream",
  "allow_all": true,
  "shell": true,
  "help": "fetch current branch only"
}
```

### customize the local/remote relationship coloring displayed by the `gita ll` command

You can see the default color scheme and the available colors via `gita color`.
To change the color coding, use `gita color set <situation> <color>`.
The configuration is saved in `$XDG_CONFIG_HOME/gita/color.csv`.

### customize information displayed by the `gita ll` command

You can customize the information displayed by `gita ll`.
The used and unused information items are shown with `gita info`, and the
configuration is saved in `$XDG_CONFIG_HOME/gita/info.csv`.

For example, the default setting corresponds to

```csv
branch,commit_msg,commit_time
```

Here `branch` includes both branch name and status.
The status symbols are similar to the ones used in [spaceship-prompt](https://spaceship-prompt.sh/sections/git/#Git-status-git_status).

To customize these symbols, add a file in `$XDG_CONFIG_HOME/gita/symbols.csv`.
The default settings corresponds to

```csv
dirty,staged,untracked,local_ahead,remote_ahead,diverged,in_sync,no_remote
*,+,?,↑,↓,⇕,,∅
```
Only the symbols to be overridden need to be defined.
You can search unicode symbols [here](https://www.compart.com/en/unicode/).

### customize git command flags

One can set custom flags to run `git` commands. For example, with

```
gita flags set my-repo --git-dir=`gita ls dotfiles` --work-tree=$HOME
```

any `git` command/alias triggered from `gita` on `dotfiles` will use these flags.
Note that the flags are applied immediately after `git`. For example,
`gita st dotfiles` translates to

```
git --git-dir=$HOME/somefolder --work-tree=$HOME status
```

running from the `dotfiles` directory.

This feature was originally added to deal with
[bare repo dotfiles](https://www.atlassian.com/git/tutorials/dotfiles).

## Requirements

Gita requires Python 3.6 or higher, due to the use of
[f-string](https://www.python.org/dev/peps/pep-0498/)
and [asyncio module](https://docs.python.org/3.6/library/asyncio.html).

Under the hood, gita uses `subprocess` to run git commands/aliases.
Thus the installed git version may matter.
I have git `1.8.3.1`, `2.17.2`, and `2.20.1` on my machines, and
their results agree.

## Tips

effect | shell command
---|---
enter `<repo>` directory|`` cd `gita ls <repo>` ``
delete repos in `<group>` | `gita group ll <group> \| xargs gita rm`

## Contributing

To contribute, you can

- report/fix bugs
- request/implement features
- star/recommend this project

Read [this article](https://www.dataschool.io/how-to-contribute-on-github/) if you have never contribute code to open source project before.

Chat room is available on [![Join the chat at https://gitter.im/nosarthur/gita](https://badges.gitter.im/nosarthur/gita.svg)](https://gitter.im/nosarthur/gita?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

To run tests locally, simply `pytest` in the source code folder.
Note that context should be set as `none`.
More implementation details are in
[design.md](https://github.com/nosarthur/gita/blob/master/doc/design.md).
A step-by-step guide to reproduce this project is [here](https://nosarthur.github.io/side%20project/2019/05/27/gita-breakdown.html).

You can also sponsor me on [GitHub](https://github.com/sponsors/nosarthur). Any amount is appreciated!

## Other multi-repo tools

I haven't tried them but I heard good things about them.

- [myrepos](https://myrepos.branchable.com/)
- [repo](https://source.android.com/setup/develop/repo)

