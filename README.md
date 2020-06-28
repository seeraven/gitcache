gitcache
========

Local cache for git repositories to speed up working with large repositories
and multiple clones.

The basic idea of gitcache is to act as a wrapper for the `git` command and
use a local bare mirror as the repository source when cloning and pulling
repositories.


Requirements
------------

  - Python 3
  - git


Installation
------------

The gitcache consists only of the python script `gitcache` that should be
installed as an overlay to the `git` command. For example:

    cp gitcache ~/bin/git
    export PATH=$HOME/bin:$PATH

Note: It is recommended to use a per-user configuration to avoid security risks.


Configuration
-------------

The configuration of the gitcache is done by the following environment
variables:

  - `GITCACHE_DIR`:      The base directory to store all mirrored git
                         repositories. The default is `~/.gitcache`.
  - `GITCACHE_REAL_GIT`: The absolute path to the real git command. The default
                         is `/usr/bin/git`.

These configuration variables should be set in the users `.bashrc`, not in
system-wide settings like `/etc/profile.d/`!


Security Considerations
-----------------------

The main idea behind gitcache is to perform the caching of the git repositories
only for the current user. This means that you should not share the mirrored
git repositories with other users, as you do not know if another user would have
the permission to access the remote repository.
