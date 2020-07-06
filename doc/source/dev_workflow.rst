Development Workflow
====================

The main idea is inspired by the well known git-flow that follows the main principle
of keeping the `master` branch always working and performing all development in
separate branches. Only versions that can be distributed should be available on the
`master` branch.


Feature Development
-------------------

Features and bugfixes are developed in separate branches. For example, features are
developed in feature branches, that are branches of the pattern
:code:`feature/my-new-feature`. These branches can be stored on the remote server. To
create a feature branch, call::

    $ git branch feature/my-new-feature
    $ git checkout feature/my-new-feature

Then commit on this branch as you like. On the first push to the remote server,
you have to call::

    $ git push --set-upstream origin feature/my-new-feature

The feature branch can be rebased as you like. If you are modifiing already
pushed commits, you need to perform a force push::

    $ git push --force-with-lease

When you are finished with your work on your feature, you should perform
the following steps:

- Fetch the latest changes on the master branch::

      $ git checkout master
      $ git pull

- Rebase your feature branch on the head of the master branch::

      $ git checkout feature/my-new-feature
      $ git rebase master

- Test your software again.
- Squash your commits into one::

      $ git rebase -i master

- Merge your feature branch onto the master branch::

      $ git checkout master
      $ git merge feature/my-new-feature
      $ git push

- Remove your feature branch locally and remotely::

      $ git branch -d feature/my-new-feature
      $ git push origin --delete feature/my-new-feature


Release Process
---------------

At some point, you want to release the project. In an ideal world, all your
modifications were already tested and you can start creating your installers
right away.

However, if your continuous integration toolchain can not cover all aspects,
e.g., if you need a special server for testing, you have to perform a separate
release process.

The release process usually consists of the following steps:

- Define the release candidate. This is usually the head of the `master`
  branch. To document the release candidate, tag the commit with the
  upcoming version number followed by an `rc` suffix. For example, if
  the next version will be 1.2.3, you should tag the release candidate
  as `v1.2.3rc1`.
- Perform all tests. If there are problems, these should be addressed
  in bugfix branches and the process is repeated.
- If all tests are successfull, tag the release with the version tag,
  e.g., `v1.2.3` and create the installers resp. packages.
- Update your distribution channels, e.g., push your debian package
  into your debian repository.
- Inform your clients about the new release.

