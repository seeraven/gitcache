gitcache
========

Synopsis
--------

gitcache [-h|--help] [-c|--cleanup] [-u|--update-all] [-d MIRROR|--delete MIRROR] [-s|--show-statistics] [-z|--zero-statistics]

gitcache git [ARGUMENTS]

git [ARGUMENTS]  (via symbolic link)


Description
-----------

The gitcache is a command line tool to wrap calls to git in order to use local
mirror repositories instead of the original upstream repositories. This allows
speeding up multiple clones or updates of the same repository.

When called as :code:`gitcache` without any arguments it shows the current
configuration.

When called as :code:`gitcache` with the first argument as :code:`git` it wraps
the git command. The same happens if using a symlink named :code:`git` pointing
to the :code:`gitcache` script.


Options of gitcache
-------------------

-h, --help                        Show the general help.
-c, --cleanup                     Remove repositories that were not updated within the last
                                  :code:`GITCACHE_CLEANUP_DAYS` days.
-u, --update-all                  Update all mirrored repositories.
-d MIRROR, --delete MIRROR        Delete the mirror identified by its upstream URL or its path
                                  in the cache. This option can be specified multiple times.
-s, --show-statistics             Show the statistics about the cache usage. Counts the
                                  number of mirrors and the number of updates of the mirrors
                                  as well as the number of clones and updates using the mirrors.
-z, --zero-statistics             Clears the statistics.


Configuration of gitcache
-------------------------

gitcache uses a base directory specified using the :code:`GITCACHE_DIR` environment
variable. If this variable is not set, the default :code:`~/.gitcache` is used.

The configuration is read from the config file :code:`$GITCACHE_DIR/config`, which is
initialized with default values when the config file does not exist. For a single
mirror, all or parts of the configuration can be changed by creating a config file
named :code:`config` under the mirror directory.

All elements of the configuration file can be overwritten using environment
variables. The individual names of the environment variables can be seen when
calling :code:`gitcache` without any arguments.


Mirror Update Strategy
----------------------

The mirror update strategy is controlled using the so called update interval.
It gives the time between two updates of a mirror in seconds and allows you to
save network bandwidth by avoiding multiple updates at almost the same time. It
is configured using the configuration item MirrorHandling/UpdateInterval or the
environment variable :code:`GITCACHE_UPDATE_INTERVAL`.

The default value of the update interval is 0, meaning that every update is
performed. By setting the update interval to a negative value, no update via
:code:`git pull` or :code:`git fetch` is performed. In this case, you can update
the mirrors only by calling :code:`git update-mirrors` or :code:`gitcache -u`.
This can be useful on CI servers to control network usage even further.


Handled git commands
--------------------

When used as a wrapper to :code:`git` the following commands are intercepted and handled
specially. All other commands are forwarded directly to :code:`git`.

:code:`git cleanup`
    Remove all outdated mirrors. A mirror is outdated if its last update time is
    older than the configured `:code:GITCACHE_CLEANUP_AFTER` time span.

:code:`git update-mirrors`
    Update all mirrors ignoring the update interval.

:code:`git delete-mirror <upstream url>|<mirror path>`
    Delete the mirror identified by its upstream URL or the mirror path.

:code:`git ls-remote ...`
    Update the mirror and redirect the ls-remote call to the mirror.

:code:`git clone <upstream url> [dst]`
    If a mirror for the upstream url does not exist yet, it is created first. Then the
    final clone of the repository is performed by cloning from the local mirror. Afterwards,
    the original upstream url is set as the push url of the repository.

:code:`git pull`
    The mirror is updated first, then the repository.

:code:`git fetch ...`
    Update the mirror before fetching the changesets from the mirror.

:code:`git lfs fetch ...`
    Fetch the lfs parts for the repository and specified ref.

:code:`git submodule update`
    Perform the submodule update by calling the individual git commands to ensure that
    the submodules are fetched by gitcache as well.


License
-------

gitcache (https://github.com/seeraven/gitcache) is released under the
"BSD 3-Clause License". Please see the LICENSE file that is included as part of this package.
