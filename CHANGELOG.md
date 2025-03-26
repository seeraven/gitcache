# Changelog of gitcache

## Upcoming Version

- Bugfix: Fix `git remote add origin` command when not using the `-C` option.

## v1.0.26

- Bugfix: Fix command line handling when using the `git remote` command.

## v1.0.25

- Handle `git remote add origin` by cloning the remote if it was not mirrored
  before and configure the mirror for the remote origin fetch.

## v1.0.24

- To allow fetching orphaned commits, the `git fetch` command retries a failed
  command in the mirror directory.

## v1.0.23

- Added support for Ubuntu 22.04 and Ubuntu 24.04 on ARM.
- Updated pip dependencies.

## v1.0.22

- Updated README.md section "Installation on MacOS". Thanks to Ihor Dutchak for the attribute
  clearing command!
- Updated README.md section "Configuration" to include the new `CloneStyle` option.
- Added README.md section "Development".
- Bugfix in functional test with an invalid repository name.
- Moved main entry point into the module to allow building a wheel.
- Added first support in Makefile to build and test a wheel.
- Added support to the github runner to create a wheel release.

## v1.0.21

- New partial clone mode available by setting the config variable `CloneStyle` (section `Clone`) to
  `PartialFirst` or setting the environment variable `GITCACHE_CLONE_STYLE=PartialFirst`. This mode
  creates the mirror by performing a shallow clone first followed by a `git fetch -unshallow`.
  Thanks to An Darejkal for the implementation!

## v1.0.20

- Support flags `--recursive`, `--recurse-submodules` and `--remote-submodules` of `git clone`.

## v1.0.19

- Updated pip dependencies
- Added support to build Alpine binaries
- Added support to build Ubuntu 24.04 image
- Use macos-15 instead of macos-14 github runner.

## v1.0.18

- Feature: Use own implementation of rmtree that handles PermisionError whenever a directory is to be deleted.

## v1.0.17

- Feature: Added release for MacOS x86_64 (thanks to Ihor Dutchak)

## v1.0.16

- Feature: Release on MacOS is not a single executable any more but a directory. This is
  necessary as MacOS has a huge startup delay (about 5s per gitcache call!).

## v1.0.15

- Workaround: Git for Windows has a bug preventing asking for a password when stderr is redirected
  (see https://github.com/git-for-windows/git/issues/1613). As a workaround, we disable stderr
  capture (and analysis) if we find the pattern "Permission denied (publickey)." in stderr.
- Bugfix: Prevent creating mirrors from existing gitcache mirror directories.
- Bugfix: Fixed unit tests.
- Feature: Fixes to support MacOS.

## v1.0.14

- Bugfix: Fixed relative submodule URLs (thanks to Ihor Dutchak)
- Bugfix: Normalize all URLs to prevent escape of `mirrors` directory and to maximize utilization of the cache
- Note: Due to the new normalization is is recommended to clear the cache before using this new version!
- Feature: Added support for Ubuntu 24.04

## v1.0.13

- Feature: Added `CHANGELOG.md` file.
- Bugfix: Fixes functional tests on windows when using the python script (not the pyinstaller binary)
- Removed support for Ubuntu 18.04.
- Feature: Use make4py infrastructure.
- Bugfix: Support all possible remote repository specifications.

## v1.0.12

- Bugfix: Fixed a bug on windows when gitcache is called as `git.exe` instead
  of `git`.
- Feature: Updated pip dependencies.

## v1.0.11

- Bugfix: Fixed a bug that occurs when a `git clone` is aborted which prevented
  cloning the repository again.

## v1.0.10

- Feature: Updated pip dependencies.
- Feature: Update of Makefile.
- Bugfix: Bugfix in `git submodule update --init --recursive` to update the
  submodule before traversing down the tree and updating the submodules of
  that module.

## v1.0.9

- This release provides the first version of the windows port of gitcache which
  required a major rewrite of the internals:
  - Rewritten all calls of git from within gitcache to use a list of
    command arguments rather than strings, disabled the use of an extra
    shell and replaced all additional tools like grep and awk with
    python code.
  - Replaced the functional tests that were written in bash with a new
    simple framework written in python.
  - Added a more complicated version of rmtree to delete a repository
    tree. This was necessary as on Windows the default `shutils.rmtree()`
    function was not working out of the box.
  - Added a Vagrantfile to create a virtual machine suitable for building
    and testing the gitcache release for Windows.
  - Extended the Makefile to distinguish between Windows and Linux.
- Create release for Windows and Ubuntu 22.04.

## v1.0.8

- Featue: Added configuration options (and environment variables) to specify
  regex patterns to select the repositories on which gitcache should be used.
- Feature: Updated the README.md to describe the configuration options in more
  detail.

## v1.0.7

- Feature: Extended functional tests to check recursive submodule update
  checkout.
- Feature: Implemented recursive submodule update functionality.

## v1.0.6

- Feature: Reworked functional tests.
- Feature: Ensured gitcache works with and without git-lfs.
- Feature: Intercept `git lfs pull` command to perform a git lfs fetch first.
- Feature: Ensure git checkout performs a git lfs fetch only on remote refs
  (avoids ugly error messages).
- Feature: Added the version output of gitcache for the command line
  `gitcache --version`.

## v1.0.5

- Feature: New git command line parser.
- Bugfix: Fix issue #1 - git lfs fetch command is not correctly interpreted.
- Bugfix: Fix issue #2 - "git clone ... -b branch" causes error.

## v1.0.4

- Bugfix: Avoid updating LFS two times in a row when called via `git pull` and
  using the default rev.
- Bugfix regarding git submodule update.

## v1.0.3

- Bugfix: Handle ssh URLs.
- Bugfix: Handle relative URLs in submodules.

## v1.0.2

- Bugfix: Handle non-fatal garbage collection errors when updating a mirror.
- Bugfix: Set LFS storage and URL when using the `git fetch` command.

## v1.0.1

- Bugfix in `git lfs fetch` command.
- Support to build releases for Ubuntu 16.04, 18.04 and 20.04.

## v1.0.0

- Initial version.
