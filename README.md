# gitcache

Local cache for [git] repositories to speed up working with large repositories
and multiple clones.

The basic idea of gitcache is to use a local bare mirror that is updated
when needed and used as the source repository for multiple local repositories.


## Features

  - Wrapper for the `git` command for easy integration.
  - [git-lfs] support.
  - Custom update interval of git mirrors including the possibility to
    perform updates only on explicit request.
  - Statistics available using the `gitcache` command.
  - Timeouts on all mirror-related operations using a total execution
    timeout and a timeout on the stdout/stderr output of the commands.
  - Configuration via environment variables, a global configuration file and
    a per-configuration configuration file.


## Description

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


## Mirror Update Strategy

The mirror update strategy is controlled using the so called update interval.
It gives the time between two updates of a mirror in seconds and allows you to
save network bandwidth by avoiding multiple updates at almost the same time.

In addition, updates from the `git pull` and `git fetch` commands can be
completely disabled by setting it to a negative value. This means that updates
of the mirrors are only performed if explicitly requested by a
`git update-mirrors` command. This can be useful on CI servers to control
network usage even further.


## Installation on Linux

gitcache is distributed as a single executable packaged using [pyInstaller].
So all you have to do is to download the latest executable and copy it to a
location of your choice, for example `~/bin`:

    wget https://github.com/seeraven/gitcache/releases/download/v1.0.26/gitcache_v1.0.26_Ubuntu22.04_x86_64
    mv gitcache_v1.0.26_Ubuntu22.04_x86_64 ~/bin/gitcache
    chmod +x ~/bin/gitcache

gitcache can be used as a stand-alone command, but it is much easier to use
it as a wrapper to `git`. All you have to do is to create a symlink and to
adjust the `PATH` variable so that the wrapper is found before the real
`git` command:

    ln -s gitcache ~/bin/git
    export PATH=$HOME/bin:$PATH

The `export` statement should be added to your `~/.bashrc` file to set
it permanently.


## Installation on Windows

Download the latest executable for Windows from the release page
https://github.com/seeraven/gitcache/releases. Rename the executable to
`gitcache.exe` and put it into a directory in your PATH, e.g., into
`C:\Windows`. Then create a symlink to `git.exe` by opening a console and
executing:

    cd C:\Windows
    mklink git.exe gitcache.exe

Please note that the directory you are putting the symlink into should be
stated before the real git command directory in your PATH variable!


## Installation on MacOS

A single [pyInstaller] executable has a huge startup delay on MacOS, therefore
gitcache is distributed as a tar-ball (`*.tgz` file). Download the archive and
extract it at your desired target location (the archive contains a subfolder):

    cd /my/target/destination
    tar xfz gitcache_v1.0.26_Darwin_arm64.tgz
    xattr -cr gitcache_v1.0.26_Darwin_arm64
    ls gitcache_v1.0.26_Darwin_arm64

To use the `gitcache` command, the final installation directory should be put
into your `PATH` variable. To use it as a wrapper to the `git` command, you
have to create the symlink and adjust the `PATH` variable so that the wrapper
is found bfore the real `git` command as described on the installation on Linux
section.


## Installation using the Wheel Package

You can also install gitcache using a wheel, but please note that this
distribution method is not very well tested. If you have problems with
gitcache, please test first using one of the [pyInstaller] executables
before opening a bug ticket.

The latest wheel is found on the release page
https://github.com/seeraven/gitcache/releases and is installed using pip:

    pip install gitcache-1.0.26-py3-none-any.whl

As with the other installation methods, you have to make sure to create a
symlink named `git` to the location of the `gitcache` script and ensure it
overlays the real git installation, e.g.:

    ln -s $(which gitcache) ~/bin/git
    export PATH=$HOME/bin:$PATH


## Configuration

gitcache stores all files under in the directory `~/.gitcache`. This base
directory can be changed by setting the `GITCACHE_DIR` environment variable.
When the `GITCACHE_DIR` is created, the default configuration file
`GITCACHE_DIR/config` is created and populated with the default values.

The current configuration can be shown by calling

    gitcache

For every item, you'll see a corresponding environment variable that
can be used to overwrite the setting of the configuration file.

The configuration options are:

| Category       | Config Item      | Default Value   | Environment Variable                  |
|----------------|------------------|-----------------|---------------------------------------|
| System         | realgit          | `/usr/bin/git`  | `GITCACHE_REAL_GIT`                   |
| MirrorHandling | updateinterval   | `0 s`           | `GITCACHE_UPDATE_INTERVAL`            |
| MirrorHandling | cleanupafter     | `14 days`       | `GITCACHE_CLEANUP_AFTER`              |
| Command        | checkinterval    | `2 s`           | `GITCACHE_COMMAND_CHECK_INTERVAL`     |
| Command        | locktimeout      | `1 h`           | `GITCACHE_COMMAND_LOCK_TIMEOUT`       |
| Command        | warniflockedfor  | `10 s`          | `GITCACHE_COMMAND_WARN_IF_LOCKED_FOR` |
| GC             | commandtimeout   | `1 h`           | `GITCACHE_GC_COMMAND_TIMEOUT`         |
| GC             | outputtimeout    | `5 m`           | `GITCACHE_GC_OUTPUT_TIMEOUT`          |
| GC             | retries          | `3`             | `GITCACHE_GC_RETRIES`                 |
| LFS            | commandtimeout   | `1 h`           | `GITCACHE_LFS_COMMAND_TIMEOUT`        |
| LFS            | outputtimeout    | `5 m`           | `GITCACHE_LFS_OUTPUT_TIMEOUT`         |
| LFS            | permirrorstorage | `True`          | `GITCACHE_LFS_PER_MIRROR_STORAGE`     |
| LFS            | retries          | `3`             | `GITCACHE_LFS_RETRIES`                |
| Clone          | commandtimeout   | `1 h`           | `GITCACHE_CLONE_COMMAND_TIMEOUT`      |
| Clone          | outputtimeout    | `5 m`           | `GITCACHE_CLONE_OUTPUT_TIMEOUT`       |
| Clone          | retries          | `3`             | `GITCACHE_CLONE_RETRIES`              |
| Clone          | clonestyle       | `Full`          | `GITCACHE_CLONE_STYLE`                |
| Update         | commandtimeout   | `1 h`           | `GITCACHE_UPDATE_COMMAND_TIMEOUT`     |
| Update         | outputtimeout    | `5 m`           | `GITCACHE_UPDATE_OUTPUT_TIMEOUT`      |
| Update         | retries          | `3`             | `GITCACHE_UPDATE_RETRIES`             |
| UrlPatterns    | includeregex     | `.*`            | `GITCACHE_URLPATTERNS_INCLUDE_REGEX`  |
| UrlPatterns    | excluderegex     | (empty)         | `GITCACHE_URLPATTERNS_EXCLUDE_REGEX`  |

Configuration items that expect a time support the following values:

  - Suffix `w`, `wks` or `weeks` to give the time in weeks.
  - Suffix `d`, `dys` or `days` to give the time in days.
  - Suffix `h`, `hrs` or `hours` to give the time in hours.
  - Suffix `m`, `mins` or `minutes` to give the time in minutes.
  - Suffix `s`, `secs` or `seconds` to give the time in seconds.
  - Numbers can be integer or float, e.g, `1.5 weeks`.

The following list gives a description of the configuration options:

  - _System/realgit_ (`GITCACHE_REAL_GIT`) specifies the real git command. This
    is usually `/usr/bin/git` but can be changed as you like.
  - _MirrorHandling/updateinterval_ (`GITCACHE_UPDATE_INTERVAL`) gives the
    minimum time between two mirror updates. If this is set to 0, the mirror is
    updated always when needed. If you set this to something like `10 minutes`
    then the mirror is updated only if the last update was at least 10 minutes
    ago.
  - _MirrorHandling/cleanupafter_ (`GITCACHE_CLEANUP_AFTER`) specifies how old
    mirrors are detected. This is relevant for the `gitcache -c` resp.
    `git cleanup` command which removes all old mirrors. The time given here
    specifies the time since the last update of the mirror.
  - To ensure only one command acts on the mirror, a locking mechanism is
    used that is finetuned by the settings of the _Command_ category. The
    _Command/checkinterval_ (`GITCACHE_COMMAND_CHECK_INTERVAL`) option specifies
    at what time interval a locked mirror is checked again. The option
    _Command/locktimeout_ specifies the total timeout after which to give up.
    Finally, the _Command/warniflockedfor_ gives the time after which the user
    is warned when the mirror is locked.
  - git commands initiated by gitcache that might take a long time are monitored
    to detect stalled executions. The monitoring is implemented by looking at
    the stdout/stderr output and the command is assumed to be stalled when there
    was no output received within a certain time. This timeout is given in the
    configuration options _GC/outputtimeout_ (`GITCACHE_GC_COMMAND_TIMEOUT`),
    _LFS/outputtimeout_ (`outputtimeout`), _Clone/outputtimeout_
    (`GITCACHE_CLONE_OUTPUT_TIMEOUT`) and _Update/outputtimeout_
    (`GITCACHE_UPDATE_OUTPUT_TIMEOUT`) for the corresponding git operations
    _garbage collection_, _lfs file retrieval_, _clone_ and _update_.

    In addition, a total timeout for each of these groups is given by the
    options _GC/commandtimeout_ (`GITCACHE_GC_COMMAND_TIMEOUT`),
    _LFS/commandtimeout_ (`GITCACHE_LFS_COMMAND_TIMEOUT`),
    _Clone/commandtimeout_ (`GITCACHE_CLONE_COMMAND_TIMEOUT`) and
    _Update/commandtimeout_ (`GITCACHE_UPDATE_COMMAND_TIMEOUT`).

    If an operation fails, it is retried before finally giving up. This is
    configured by the _GC/retries_ (`GITCACHE_GC_RETRIES`),
    _LFS/retries_ (`GITCACHE_LFS_RETRIES`), _Clone/retries_
    (`GITCACHE_CLONE_RETRIES`) and _Update/retries_ (`GITCACHE_UPDATE_RETRIES`)
    options.
  - Using the _Clone/clonestyle_ (`GITCACHE_CLONE_STYLE`) setting you can adjust
    the method used when cloning a remote repository into the initial bare mirror.
    The default setting is `Full` that uses a normal `git clone` command. When
    you are dealing with large repositories and experience problems cloning then,
    you can switch the method to `PartialFirst`. This will perform a shallow
    clone first, followed by a `git fetch -unshallow`.
  - _LFS/permirrorstorage_ (`GITCACHE_LFS_PER_MIRROR_STORAGE`) is a boolean
    flag that determines whether each mirror will have its own lfs storage
    directory (`True`) or whether a shared directory is used (`False`).
  - _UrlPatterns/includeregex_ (`GITCACHE_URLPATTERNS_INCLUDE_REGEX`) and
    _UrlPatterns/excluderegex_ (`GITCACHE_URLPATTERNS_EXCLUDE_REGEX`) are
    used to identify repositories to mirror. The patterns are checked against
    the remote URL of a repository and it is only mirrored if the include
    pattern matches and the exclude pattern does not. If the exclude pattern
    is empty, it is internally converted into a regex that matches nothing
    (as an empty string would actually match always which would exclude all
    URLs).


## gitcache Command Usage

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


## Handled git Commands

The following git commands are handled specially. All other commands are
forwarded to the real git command.

  - `git cleanup` to remove all outdated mirrors.
  - `git update-mirrors` to update all mirrors ignoring the update interval.
  - `git delete-mirror` to delete a mirror identified by its upstream URL or
    its path in the cache.
  - `git ls-remote` to update the mirror and using it for the remote source
    of the ls-remote command.
  - `git checkout` to perform an lfs fetch for specified refs.
  - `git clone` to create or update the mirror and clone from the mirror.
  - `git lfs fetch` to fetch the lfs handled files for the mirror.
  - `git lfs pull` to fetch the lfs handled files for the mirror.
  - `git pull` to update the mirror before updating the clone.
  - `git fetch` to update the mirror before updating the clone.
  - `git submodule init` to allow correct initialization of the submodules.
  - `git submodule update` to call the gitcache for every submodule.
  - `git remote add origin` for a delayed initialization of a git repository.


## Debugging

For debugging, set the environment variable `GITCACHE_LOGLEVEL` to `Debug`:

    GITCACHE_LOGLEVEL=Debug gitcache


## Security Considerations

The main idea behind gitcache is to perform the caching of the git repositories
only for the current user. This means that you should not share the mirrored
git repositories with other users, as you do not know if another user would have
the permission to access the remote repository.


## Development

To start development on gitcache, you have to clone this repository first including
all submodules:

    git clone https://github.com/seeraven/gitcache.git
    cd gitcache
    git submodule update --init

Using the [make4py] framework, we access all major steps using the good old `make`
command. The main make targets of interest are:

  - `make format` to format the source code
  - `make check-style` to perform a static code analysis
  - `make tests` to perform unit and functional tests

The actions are executed in a virtual environment per default. You can also use
dedicated suffixes on the targets to specify the environment to use:

  - `<target>.venv` specifies explicitly to use a virtual env.
  - `<target>.ubuntu24.04` specifies to use a Ubuntu 24.04 docker container
  - `<target>.alpine3.20` specifies to use a Alpine 3.20 docker container
  - `<target>.windows` specifies to use a vagrant machine running Windows
  - `<target>.all` specifies to run the target on all variants.

For example, if you want to execute the unit tests on Ubuntu 22.04, you can call

    make unittests.ubuntu22.04


## Notes on Releases

Releases are now automatically built if a new tag `v<major>.<minor>.<revision>`
is pushed to the repository. This changes the release process a little bit:

  - Ensure the upcoming release is fully tested. A look on the commits on github
    should be enough.
  - Modify the `CHANGELOG.md` file and insert the new version number.
  - Commit the modified `CHANGELOG.md` file and tag the commit with the new
    version number.
  - As soon as the new tag is pushed to github, the release is built. When it
    is finished, it is found as a draft on the releases page.
  - Now edit the release draft, insert the changes from the `CHANGELOG.md` file.
    Then the release can be saved as a regular release.
  - Now prepare the next version. Edit the files `Makefile`, `pyproject.toml`,
    `src/git_cache/git_cache_command.py` and `doc/source/installation.rst` and
    replace the version number:

        sed -i 's/1.0.26/1.0.27/g' Makefile pyproject.toml src/git_cache/git_cache_command.py doc/source/installation.rst


## Notes on Building a Pip-Package

To create a wheel suitable for the installation via `pip`, call the following
command:

    make build-wheel

You will then find the wheel in the `dist` directory.

To test the wheel in a separate virtual environment, call

    make functional-tests-wheel


[git]: https://git-scm.com/
[git-lfs]: https://git-lfs.github.com/
[pyInstaller]: https://www.pyinstaller.org/
[make4py]: https://github.com/seeraven/make4py