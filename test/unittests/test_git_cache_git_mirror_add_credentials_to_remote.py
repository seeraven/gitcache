#
# Copyright (c) 2026 by Audric Ackermann <audric@getsession.org>
# All rights reserved.
# This file is part of gitcache (https://github.com/seeraven/gitcache)
# and is released under the "BSD 3-Clause License". Please see the LICENSE file
# that is included as part of this package.
#
"""Unit tests of the git_cache.git_mirror module testing _add_credentials_to_remote()."""

# -----------------------------------------------------------------------------
# Module Import
# -----------------------------------------------------------------------------
from unittest import TestCase, mock

from git_cache.git_mirror import GitMirror


# -----------------------------------------------------------------------------
# Test Class
# -----------------------------------------------------------------------------
class GitCacheAddCredentialsToRemoteTest(TestCase):
    """Test the :func:`git_cache.git_mirror.GitMirror._add_credentials_to_remote` function."""

    def _mirror(self, url: str) -> GitMirror:
        mirror = GitMirror.__new__(GitMirror)
        mirror.url = url
        mirror.path = GitMirror.get_mirror_path(url)
        mirror.git_dir = f"{mirror.path}/git"
        mirror.config = mock.MagicMock()
        mirror.config.get.return_value = "git"
        mirror.database = mock.MagicMock()
        return mirror

    def _run(self, url: str, remote_url: str):
        """Run _add_credentials_to_remote() with the given remote.

        Return:
            Returns the URLs passed to 'git remote set-url' and the URLs written to the database.
        """
        mirror = self._mirror(url)
        with (
            mock.patch("git_cache.git_mirror.getstatusoutput", return_value=(0, remote_url + "\n")),
            mock.patch("git_cache.git_mirror.simple_call_command", return_value=0) as set_url,
        ):
            self.assertTrue(mirror._add_credentials_to_remote())  # pylint: disable=protected-access
        remote_urls = [call.args[0][-1] for call in set_url.call_args_list]
        database_urls = [call.args[1] for call in mirror.database.set_url.call_args_list]
        return remote_urls, database_urls

    def test_remote_lost_user_is_restored(self):
        """_add_credentials_to_remote(): Restore the user on a remote stripped by v1.0.31 to v1.0.34."""
        self.assertEqual(
            self._run("git@github.com:org/repo.git", "github.com:org/repo.git"),
            (["git@github.com:org/repo.git"], ["git@github.com:org/repo"]),
        )
        self.assertEqual(
            self._run("git@github.com:org/repo", "github.com:org/repo.git"),
            (["git@github.com:org/repo"], ["git@github.com:org/repo"]),
        )
        self.assertEqual(
            self._run("ssh://git@github.com/org/repo.git", "ssh://github.com/org/repo.git"),
            (["ssh://git@github.com/org/repo.git"], ["ssh://git@github.com/org/repo"]),
        )
        self.assertEqual(
            self._run("git@github.com:org/repo.git", "ssh://github.com/org/repo.git"),
            (["git@github.com:org/repo.git"], ["git@github.com:org/repo"]),
        )

    def test_remote_with_other_user_follows_mirror_url(self):
        """_add_credentials_to_remote(): Set the remote to the mirror URL when the ssh user differs."""
        self.assertEqual(
            self._run("bob@host:org/repo.git", "alice@host:org/repo.git"),
            (["bob@host:org/repo.git"], ["bob@host:org/repo"]),
        )
        self.assertEqual(
            self._run("ssh://bob@host/org/repo.git", "ssh://alice@host/org/repo.git"),
            (["ssh://bob@host/org/repo.git"], ["ssh://bob@host/org/repo"]),
        )

    def test_remote_with_same_user_is_left_alone(self):
        """_add_credentials_to_remote(): Keep a remote that already has the user."""
        self.assertEqual(self._run("git@github.com:org/repo.git", "git@github.com:org/repo.git"), ([], []))
        self.assertEqual(self._run("git@github.com:org/repo.git", "https://github.com/org/repo.git"), ([], []))

    def test_remote_of_other_repository_is_left_alone(self):
        """_add_credentials_to_remote(): Never point the mirror at another repository."""
        self.assertEqual(self._run("git@github.com:org/repo.git", "github.com:org/other.git"), ([], []))
        self.assertEqual(self._run("git@github.com:org/repo.git", "alice@github.com:org/other.git"), ([], []))

    def test_failed_set_url_keeps_database_url(self):
        """_add_credentials_to_remote(): Leave the database alone when 'git remote set-url' fails."""
        mirror = self._mirror("git@github.com:org/repo.git")
        with (
            mock.patch("git_cache.git_mirror.getstatusoutput", return_value=(0, "github.com:org/repo.git\n")),
            mock.patch("git_cache.git_mirror.simple_call_command", return_value=1),
        ):
            self.assertFalse(mirror._add_credentials_to_remote())  # pylint: disable=protected-access
        mirror.database.set_url.assert_not_called()

    def test_url_without_user_does_not_touch_remote(self):
        """_add_credentials_to_remote(): A URL without user has nothing to restore."""
        mirror = self._mirror("github.com:org/repo.git")
        with (
            mock.patch("git_cache.git_mirror.getstatusoutput") as get_url,
            mock.patch("git_cache.git_mirror.simple_call_command") as set_url,
        ):
            self.assertTrue(mirror._add_credentials_to_remote())  # pylint: disable=protected-access
        get_url.assert_not_called()
        set_url.assert_not_called()
        mirror.database.set_url.assert_not_called()

    def test_non_ssh_url_never_rewrites_remote(self):
        """_remote_user_differs(): Only an ssh mirror URL may set the user of the remote."""
        for url in ("https://token@github.com/org/repo.git", "git://user@github.com/org/repo.git"):
            mirror = self._mirror(url)
            with mock.patch("git_cache.git_mirror.getstatusoutput") as get_url:
                self.assertFalse(mirror._remote_user_differs(), url)  # pylint: disable=protected-access
            get_url.assert_not_called()

    def test_http_credentials_are_restored(self):
        """_add_credentials_to_remote(): Restore http credentials without reading the remote."""
        mirror = self._mirror("https://user:secret@github.com/org/repo.git")
        with (
            mock.patch("git_cache.git_mirror.getstatusoutput") as get_url,
            mock.patch("git_cache.git_mirror.simple_call_command", return_value=0) as set_url,
        ):
            self.assertTrue(mirror._add_credentials_to_remote())  # pylint: disable=protected-access
        get_url.assert_not_called()
        self.assertEqual(set_url.call_args.args[0][-1], "https://user:secret@github.com/org/repo.git")
        mirror.database.set_url.assert_not_called()
