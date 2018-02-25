import os
import subprocess
from functools import lru_cache


class Color:
    red = '\x1b[31m'  # local diverges
    green = '\x1b[32m'  # local == remote
    yellow = '\x1b[33m'  # local is behind
    purple = '\x1b[35m'  # local is ahead
    white = '\x1b[37m'  # no remote
    end = '\x1b[0m'


@lru_cache()
def get_repos():
    """
    :rtype: `dict` of repo name to repo absolute path
    """
    path_file = os.path.join(os.path.expanduser('~'), '.gita_path')
    if os.path.exists(path_file):
        with open(path_file) as f:
            paths = set(f.read().splitlines()[0].split(os.pathsep))
    else:
        paths = set()
    return {os.path.basename(os.path.normpath(p)):p for p in paths}


def is_git(path):
    return os.path.isdir(os.path.join(path, '.git'))


def add_repos(new_paths):
    """
    Write new repo paths to file
    """
    paths = set(get_repos().values())
    new_paths = set(os.path.abspath(p) for p in new_paths if is_git(p))
    new_paths = new_paths - paths
    if new_paths:
        print(f"new repos: {new_paths}")
        paths.update(new_paths)
        path_file = os.path.join(os.path.expanduser('~'), '.gita_path')
        with open(path_file, 'w') as f:
            f.write(os.pathsep.join(paths))


def get_head(path):
    head = os.path.join(path, '.git', 'HEAD')
    with open(head) as f:
        return os.path.basename(f.read()).rstrip()


def has_remote():
    """
    Return `True` if remote branch exists. It should be run inside the repo
    """
    result = subprocess.run(
        ['git', 'checkout'], stdout=subprocess.PIPE, universal_newlines=True)
    return bool(result.stdout)


def get_commit_msg():
    """
    """
    result = subprocess.run(
        'git show -s --format=%s'.split(),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True)
    if result.stderr:
        print(f'ERROR in getting commit message: {result.stderr}')
    return result.stdout


def exec_git(path, cmd):
    """
    Execute `cmd` in the `path` directory
    """
    os.chdir(path)
    if has_remote():
        os.system(cmd)


def _get_repo_status(path):
    """
    :param path: path to the repo

    :return: status of the repo
    """
    os.chdir(path)
    dirty = '*' if os.system('git diff --quiet') else ''
    staged = '+' if os.system('git diff --cached --quiet') else ''

    if has_remote():
        if os.system('git diff --quiet @{u} @{0}'):
            outdated = os.system(
                'git diff --quiet @{u} `git merge-base @{0} @{u}`')
            if outdated:
                diverged = os.system(
                    'git diff --quiet @{0} `git merge-base @{0} @{u}`')
                color = Color.red if diverged else Color.yellow
            else:
                color = Color.purple
        else:  # remote == local
            color = Color.green
    else:
        color = Color.white
    return dirty, staged, color


def describe(repos):
    """
    :type repos: `dict` of repo name to repo absolute path

    :rtype: `str`
    """
    output = ''
    for name, path in repos.items():
        head = get_head(path)
        dirty, staged, color = _get_repo_status(path)
        output += f'{name:<18}{color}{head+" "+dirty+staged:<10}{Color.end} {get_commit_msg()}'
    return output