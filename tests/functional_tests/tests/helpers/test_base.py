# -*- coding: utf-8 -*-
"""
Module for the base class of the functional tests of gitcache.

Copyright:
    2022 by Clemens Rabe <clemens.rabe@clemensrabe.de>

    All rights reserved.

    This file is part of gitcache (https://github.com/seeraven/gitcache)
    and is released under the "BSD 3-Clause License". Please see the ``LICENSE`` file
    that is included as part of this package.
"""


# -----------------------------------------------------------------------------
# Module Import
# -----------------------------------------------------------------------------
import logging
import os
import subprocess
import textwrap
from itertools import zip_longest

from .test_workspace import TestWorkspace


# -----------------------------------------------------------------------------
# Logger
# -----------------------------------------------------------------------------
LOG = logging.getLogger(__name__)


# -----------------------------------------------------------------------------
# Test Exception Class
# -----------------------------------------------------------------------------
class TestError(Exception):
    """Exception indicating an error."""


# -----------------------------------------------------------------------------
# Test Base Class
# -----------------------------------------------------------------------------
class TestBase:
    """The base class of functional tests."""

    def __init__(self):
        """Construct the test."""
        self._settings = None
        self._expected_file_prefix = None
        self._workspace = None
        self._current_test_method = None
        self._history = None

    def run(self, test_name, settings):
        """Perform the test.

        Args:
            test_name (str): The test name as given during class registration.
            settings (obj):  The settings object.

        Return:
            Returns True if the test was successfull, otherwise False is returned.
        """
        self._settings = settings
        self._expected_file_prefix = f"{test_name}_"
        clear_str = f"\r{' '*120}"
        print(f"Running {test_name} ...", end='')
        LOG.debug("Start functional test.")
        for test_method in self._get_test_methods():
            self._current_test_method = f"{test_name}.{test_method.__name__}"
            self._history = ""
            print(f"{clear_str}\rRunning {self._current_test_method} ...", end='')
            try:
                with TestWorkspace() as workspace:
                    self._workspace = workspace
                    test_method()
                    self._workspace = None
            except TestError as testerror:
                print(f"""{clear_str}\rTest {self._current_test_method} failed!

Test suite name:  {test_name}
Test class name:  {self.__class__.__name__}
Test method:      {test_method.__name__}
Test description: {test_method.__doc__}""")
                if self._history:
                    print(f"""
History of successfull tests:
{textwrap.indent(self._history,' '*4)}""")

                print(f"""
Detailed error message:
{textwrap.indent(str(testerror),' '*4)}
""")
                self._settings = None
                return False
            finally:
                LOG.debug("Finished test function %s", self._current_test_method)
                self._current_test_method = None

        self._settings = None
        self._expected_file_prefix = None
        print(f"{clear_str}\rExecuted functional test suite {test_name} successfully!")
        LOG.debug("Finished functional test.")
        return True

    def _get_test_methods(self):
        """Determine the test methods to call, that are named with a prefix 'test'.

        Return:
            Returns a list of the test methods of the child class.
        """
        method_names = [m for m in dir(self) if m.startswith('test_')]
        return [getattr(self, m) for m in method_names]

    def _run_gitcache(self, args, cwd):
        """Execute the gitcache command and return the CompletedProcess object.

        Args:
            args (list): Command line arguments to the 'gitcache' command.
            cwd (str):   Directory where to execute the command. If set to None,
                         the current working directory is used.
        """
        command = self._settings.gitcache_cmd + args
        LOG.debug("Executing command %s", command)
        # pylint: disable=subprocess-run-check
        result = subprocess.run(command,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                shell=False,
                                env=self._workspace.env,
                                cwd=cwd)
        LOG.debug("Command returned return code %d", result.returncode)

        stdout_details = f"""{'-'*30}> STDOUT <{'-'*30}
{result.stdout.decode()}""" if result.stdout else ""
        stderr_details = f"""{'-'*30}> STDERR <{'-'*30}
{result.stderr.decode()}""" if result.stderr else ""
        result.execution_details = f"""{'='*80}
Scope:            {self._current_test_method}
Executed command: {command}
Return code:      {result.returncode}
{stdout_details}{stderr_details}
{'='*80}"""

        if self._settings.print_output:
            print()
            print(result.execution_details)

        return result

    def assert_equal(self, expected, measured, name="value"):
        """Assert that the expected value is identical to the measured one.

        Args:
            expected: Expected value.
            measured: Measured value.
            name:     Name to use in the exception. Default is 'value'.
        """
        if expected != measured:
            raise TestError(f"Expected {name} {expected} but got {name} {measured} instead!")
        self._history += f"Assertion ok: {name} has expected value {expected}\n"

    def assert_not_equal(self, expected, measured, name="value"):
        """Assert that the expected value is different to the measured one.

        Args:
            expected: Expected value.
            measured: Measured value.
            name:     Name to use in the exception. Default is 'value'.
        """
        if expected == measured:
            raise TestError(f"Expected {name} to be different to {expected}!")
        self._history += f"Assertion ok: {name} has not value {expected}\n"

    def assert_gitcache_ok(self, args, cwd=None):
        """Execute the gitcache command and ensure it returns a return code of 0.

        Args:
            args (list): Command line arguments to the 'gitcache' command.
            cwd (str):   Directory where to execute the command. If set to None,
                         the current working directory is used.

        Return:
            Returns the result of the command execution.
        """
        result = self._run_gitcache(args, cwd)
        if result.returncode != 0:
            message = f"""\
gitcache command "gitcache {' '.join(args)}" failed with return code {result.returncode}!

{result.execution_details}
"""
            raise TestError(message)
        self._history += f"""\
Assertion ok: gitcache command "gitcache {' '.join(args)}" executed correctly:
{textwrap.indent(result.execution_details, ' '*4)}
"""
        return result

    def assert_gitcache_fails(self, args, cwd=None):
        """Execute the gitcache command and ensure it returns a return code of non-zero.

        Args:
            args (list): Command line arguments to the 'gitcache' command.
            cwd (str):   Directory where to execute the command. If set to None,
                         the current working directory is used.

        Return:
            Returns the result of the command execution.
        """
        result = self._run_gitcache(args, cwd)
        if result.returncode == 0:
            message = f"""\
gitcache command "gitcache {' '.join(args)}" succeeded with return code {result.returncode}!

{result.execution_details}
"""
            raise TestError(message)
        self._history += f"""\
Assertion ok: gitcache command "gitcache {' '.join(args)}" fails correctly:
{textwrap.indent(result.execution_details, ' '*4)}
"""
        return result

    # pylint: disable=too-many-locals
    def assert_gitcache_output(self, args, filename, cwd=None):
        """Execute the gitcache command and ensure it has the expected output.

        Args:
            args (list):    Command line arguments to the 'gitcache' command.
            filename (str): The filename part used to construct the files for the
                            stdout and stderr files.
            cwd (str):      Directory where to execute the command. If set to None,
                            the current working directory is used.
        """
        result = self.assert_gitcache_ok(args, cwd)
        result_stdout = result.stdout.decode().replace(self._workspace.gitcache_dir_path,
                                                       "GITCACHE_DIR")
        result_stdout = result_stdout.replace('gitcache.exe', 'gitcache')
        result_stdout = result_stdout.replace('options:', 'optional arguments:')
        result_stdout = result_stdout.replace('\r\n', '\n')
        result_stdout = result_stdout.replace('GITCACHE_DIR\\', 'GITCACHE_DIR/')

        # Note: We need to consume the extra spaces here for the 02_settings test:
        result_stdout = result_stdout.replace('/usr/bin/git        ', 'REAL_GIT_CMD')
        result_stdout = result_stdout.replace('C:\\Program Files\\Git\\cmd\\git.exe',
                                              'REAL_GIT_CMD')

        stdout_filename = os.path.join(self._settings.expected_dir,
                                       f"{self._expected_file_prefix}{filename}_stdout.txt")
        if self._settings.save_output:
            LOG.debug("Saving output to %s.", stdout_filename)
            with open(stdout_filename, 'w', encoding='utf-8') as file_handle:
                file_handle.write(result_stdout)
            self._history += """\
Assertion skipped: Can't compare outputs as we are saving the outputs to disc.\n"""
        else:
            with open(stdout_filename, 'r', encoding='utf-8') as file_handle:
                expected_stdout = file_handle.read()

            stdout_differs = (expected_stdout != result_stdout)

            if stdout_differs:
                message = f"""\
Output of command "gitcache {' '.join(args)}" differs from expected output!

"""
                left_size = max([len(line) for line in expected_stdout.split('\n')])
                message += f"{'Expected Stdout'.ljust(left_size)} | Retrieved Stdout\n"
                message += f"{'-'*(left_size*2+3)}\n"
                for left, right in zip_longest(expected_stdout.split('\n'),
                                               result_stdout.split('\n'),
                                               fillvalue='<missing>'):
                    if left.strip() != right.strip():
                        message += f"{left.ljust(left_size)}<->{right}\n"
                    else:
                        message += f"{left.ljust(left_size)} | {right}\n"

                raise TestError(message)
            self._history += f"""\
Assertion ok: Output of command "gitcache {' '.join(args)}" as expected.
"""

    def assert_gitcache_config_exists(self):
        """Assert the gitcache configuration was created."""
        config_path = os.path.join(self._workspace.gitcache_dir_path, 'config')
        if not os.path.exists(config_path):
            raise TestError(f"The gitcache configuration file {config_path} does not exist!")
        self._history += f"""\
Assertion ok: Gitcache configuration file {config_path} exists.
"""

    # pylint: disable=invalid-name
    def assert_gitcache_config_does_not_exist(self):
        """Assert the gitcache configuration was not created."""
        config_path = os.path.join(self._workspace.gitcache_dir_path, 'config')
        if os.path.exists(config_path):
            raise TestError(f"The gitcache configuration file {config_path} exists!")
        self._history += f"""\
Assertion ok: Gitcache configuration file {config_path} does not exist.
"""

    def assert_gitcache_db_exists(self):
        """Assert the gitcache database was created."""
        db_path = os.path.join(self._workspace.gitcache_dir_path, 'db')
        if not os.path.exists(db_path):
            raise TestError(f"The gitcache database file {db_path} does not exist!")
        self._history += f"""\
Assertion ok: Gitcache database file {db_path} exists.
"""

    # pylint: disable=invalid-name
    def assert_gitcache_db_does_not_exist(self):
        """Assert the gitcache database was not created."""
        db_path = os.path.join(self._workspace.gitcache_dir_path, 'db')
        if os.path.exists(db_path):
            raise TestError(f"The gitcache database file {db_path} exists!")
        self._history += f"""\
Assertion ok: Gitcache database file {db_path} does not exist.
"""

    def assert_db_field(self, field, url, expected):
        """Assert the given field of the url has a certain value.

        Args:
            field (str): The field to test, e.g., 'mirror-updates'.
            url (str):   The repository url.
            expected:    The expected value. If set to None, we expect
                         the entry to not exist at all.
        """
        db_path = os.path.join(self._workspace.gitcache_dir_path, 'db')
        database = {}
        try:
            # pylint: disable=unspecified-encoding
            with open(db_path, 'r') as file_handle:
                # pylint: disable=eval-used
                database = eval(file_handle.read())
        except FileNotFoundError:
            database = {}

        actual_value = None
        for mirror_dir in database:
            if database[mirror_dir]["url"].startswith(url):
                actual_value = database[mirror_dir][field]
                break

        if expected is None:
            if actual_value:
                message = f"The gitcache database field {field} for url {url}"
                message += f" exists with value {actual_value} although we expected it"
                message += " to not exist at all!"
                raise TestError(message)
            self._history += f"""\
Assertion ok: Gitcache database field {field} for url {url} does not exist.
"""
        else:
            if expected != actual_value:
                message = f"The gitcache database field {field} for url {url}"
                message += f" is {actual_value}, but we expected {expected}!"
                raise TestError(message)
            self._history += f"""\
Assertion ok: Gitcache database field {field} for url {url} is {actual_value}.
"""

    def assert_remote_of_clone(self, checkout_dir):
        """Assert the remote of the given checkout points to the git cache.

        Args:
            checkout_dir (str): The checkout directory.
        """
        command = ["git", "-C", checkout_dir, "remote", "get-url", "origin"]
        # pylint: disable=subprocess-run-check
        result = subprocess.run(command,
                                stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                                shell=False)
        fetch_url = result.stdout.decode().strip()
        if not fetch_url.startswith(self._workspace.gitcache_dir_path):
            message = f"The checkout {checkout_dir} has not a remote pointing to the git cache!"
            raise TestError(message)
        self._history += f"""\
Assertion ok: Checkout {checkout_dir} has a remote pointing to the git cache.
"""

    def assert_branch(self, checkout_dir, expected_branch):
        """Assert the branch of the given checkout.

        Args:
            checkout_dir (str):    The checkout directory.
            expected_branch (str): The expected branch.
        """
        command = ["git", "-C", checkout_dir, "rev-parse", "--abbrev-ref", "HEAD"]
        # pylint: disable=subprocess-run-check
        result = subprocess.run(command,
                                stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                                shell=False)
        actual_branch = result.stdout.decode().strip()
        if actual_branch != expected_branch:
            message = f"The checkout {checkout_dir} is not on the branch {expected_branch}"
            message += f" but on branch {actual_branch}!"
            raise TestError(message)
        self._history += f"""\
Assertion ok: Checkout {checkout_dir} is on branch {expected_branch}.
"""

    def assert_tag(self, checkout_dir, expected_tag):
        """Assert the tag of the given checkout.

        Args:
            checkout_dir (str): The checkout directory.
            expected_tag (str): The expected tag.
        """
        command = ["git", "-C", checkout_dir, "describe", "--tags"]
        # pylint: disable=subprocess-run-check
        result = subprocess.run(command,
                                stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                                shell=False)
        actual_tag = result.stdout.decode().strip()
        if actual_tag != expected_tag:
            message = f"The checkout {checkout_dir} is not on the tag {expected_tag}"
            message += f" but on tag {actual_tag}!"
            raise TestError(message)
        self._history += f"""\
Assertion ok: Checkout {checkout_dir} is on tag {expected_tag}.
"""

    def assert_in_file(self, needle, filename):
        """Assert the given needle is found in the given file.

        Args:
            needle (str):   The string to search in the file.
            filename (str): The file to open.
        """
        exception = None
        try:
            with open(filename, 'rb') as file_handle:
                content = file_handle.read()
                if needle.encode() not in content:
                    message = f"The string '{needle}' was not found in the file {filename}!"
                    exception = TestError(message)
                else:
                    self._history += f"""\
Assertion ok: String {needle} found in file {filename}.
"""
        except FileNotFoundError:
            message = f"The string '{needle}' was not found in {filename} as "
            message += "the file does not exist!"
            exception = TestError(message)

        if exception:
            raise exception

    def assert_not_in_file(self, needle, filename):
        """Assert the given needle is not found in the given file.

        Args:
            needle (str):   The string to search in the file.
            filename (str): The file to open.
        """
        exception = None
        try:
            with open(filename, 'rb') as file_handle:
                content = file_handle.read()
                if needle.encode() in content:
                    message = f"The string '{needle}' was found in the file {filename}!"
                    exception = TestError(message)
                else:
                    self._history += f"""\
Assertion ok: String {needle} not found in file {filename}.
"""
        except FileNotFoundError:
            message = f"The string '{needle}' was not found in {filename} as "
            message += "the file does not exist!"
            exception = TestError(message)

        if exception:
            raise exception

    def assert_file_exists(self, filename):
        """Assert the given file or directory exists.

        Args:
            filename (str): The file.
        """
        if not os.path.exists(filename):
            raise TestError(f"The file/directory {filename} does not exist!")
        self._history += f"""\
Assertion ok: File/directory {filename} exists.
"""

    def assert_file_does_not_exist(self, filename):
        """Assert the given file or directory does not exist.

        Args:
            filename (str): The file.
        """
        if os.path.exists(filename):
            raise TestError(f"The file/directory {filename} does exist!")
        self._history += f"""\
Assertion ok: File/directory {filename} does not exist.
"""

# -----------------------------------------------------------------------------
# EOF
# -----------------------------------------------------------------------------
