gitcache
========

Local cache for [git] repositories to speed up working with large repositories
and multiple clones.

The basic idea of gitcache is to use a local bare mirror that is updated
when needed and used as the source repository for multiple local repositories.


Features
--------

  - Wrapper for the `git` command for easy integration.
  - [git-lfs] support.
  - Custom update interval of git mirrors including the possibility to
    perform updates only on explicit request.
  - Statistics available using the `gitcache` command.
  - Timeouts on all mirror-related operations using a total execution
    timeout and a timeout on the stdout/stderr output of the commands.
  - Configuration via environment variables, a global configuration file and
    a per-configuration configuration file.


Description
-----------

gitcache is designed to be used as a wrapper to git, so in the following we
show how gitcache translates the git commands for the individual operations.

When the user issues a

    git clone https://github.com/seeraven/gitcache.git

for the first time, the repository https://github.com/seeraven/gitcache.git is
cloned into a bare mirror `$GITCACHE_DIR/mirrors/github.com/seeraven/gitcache/git`
and then the git command is rewritten to

    git clone $GITCACHE_DIR/mirrors/github.com/seeraven/gitcache/git gitcache

to create the clone. In addition, the push URL of the clone is adjusted to the
upstream URL.

Whenever the user issues another `git clone` command of that repository, the
mirror is updated (if the update strategy permits it) and the local clone is
created as before.

Whenever the user performs a `git pull` or `git fetch` on that local clone,
gitcache checks whether the repository is handled by gitcache (that is the pull
URL is pointing to the mirror, the push URL is pointing to the upstream URL).
If it is, it updates the mirror first (according to the update strategy) and
executes the original command afterwards.

In addition to the git repositories, gitcache supports [git-lfs] as well and
updates of the mirror include updates of the git-lfs part. You can configure
gitcache to either use a global git-lfs storage directory or to use per mirror
storage directories (the default).

All update operations on a mirror use a lock to ensure that only one
modifies the mirror. This is crucial as simultaneous clones would easily lead
to inconsistent behaviours and ugly race conditions.


Mirror Update Strategy
----------------------

The mirror update strategy is controlled using the so called update interval.
It gives the time between two updates of a mirror in seconds and allows you to
save network bandwidth by avoiding multiple updates at almost the same time.

In addition, updates from the `git pull` and `git fetch` commands can be
completely disabled by setting it to a negative value. This means that updates
of the mirrors are only performed if explicitly requested by a
`git update-mirrors` command. This can be useful on CI servers to control
network usage even further.


Installation
------------

gitcache is distributed as a single executable packaged using [pyInstaller].
So all you have to do is to download the latest executable and copy it to a
location of your choice, for example `~/bin`:

    wget https://github.com/seeraven/gitcache/releases/download/v1.0.5/gitcache_Ubuntu18.04_amd64
    mv gitcache_Ubuntu18.04_amd64 ~/bin/gitcache
    chmod +x ~/bin/gitcache

gitcache can be used as a stand-alone command, but it is much easier to use
it as a wrapper to `git`. All you have to do is to create a symlink and to
adjust the `PATH` variable so that the wrapper is found before the real
`git` command:

    ln -s gitcache ~/bin/git
    export PATH=$HOME/bin:$PATH

The `export` statement should be added to your `~/.bashrc` file to set
it permanently.


Configuration
-------------

gitcache stores all files under in the directory `~/.gitcache`. This base
directory can be changed by setting the `GITCACHE_DIR` environment variable.
When the `GITCACHE_DIR` is created, the default configuration file
`GITCACHE_DIR/config` is created and populated with the default values.

The current configuration can be shown by calling

    gitcache

For every item, you'll see a corresponding environment variable that
can be used to overwrite the setting of the configuration file.


gitcache Command Usage
----------------------

The gitcache command provides the following options:

  - `-h`, `--help` to show the command help.
  - `-c`, `--cleanup` to remove all outdated mirrors.
  - `-u`, `--update-all` to update all mirrors ignoring the update interval.
  - `-d MIRROR`, `--delete MIRROR` to delete a mirror identified by its upstream
    URL or its path in the cache. This option can be specified multiple times.
  - `-s`, `--show-statistics` to show the statistics of gitcache.
  - `-z`, `--zero-statistics` to clear the statistics.

Without any options the gitcache command shows the current configuration.

When called as `gitcache git ...` it wraps the given git command as described in
the next section.


Handled git Commands
--------------------

The following git commands are handled specially. All other commands are
forwarded to the real git command.

  - `git cleanup` to remove all outdated mirrors.
  - `git update-mirrors` to update all mirrors ignoring the update interval.
  - `git delete-mirror` to delete a mirror identified by its upstream URL or
    its path in the cache.
  - `git ls-remote` to update the mirror and using it for the remote source
    of the ls-remote command.
  - `git clone` to create or update the mirror and clone from the mirror.
  - `git pull` to update the mirror before updating the clone.
  - `git fetch` to update the mirror before updating the clone.
  - `git lfs fetch` to update the lfs part.
  - `git submodule update` to call the gitcache for every submodule.


Debugging
---------

For debugging, set the environment variable `GITCACHE_LOGLEVEL` to `Debug`:

    GITCACHE_LOGLEVEL=Debug gitcache


Security Considerations
-----------------------

The main idea behind gitcache is to perform the caching of the git repositories
only for the current user. This means that you should not share the mirrored
git repositories with other users, as you do not know if another user would have
the permission to access the remote repository.


[git]: https://git-scm.com/
[git-lfs]: https://git-lfs.github.com/
[pyInstaller]: https://www.pyinstaller.org/