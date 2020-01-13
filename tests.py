import collections
import contextlib
import tempfile
import textwrap
from unittest import mock
from unittest import TestCase

from cron_install import Command


@contextlib.contextmanager
def cronfile(content):
    with tempfile.NamedTemporaryFile(mode="w+t", prefix="test_cron_install") as f:
        f.write(content)
        f.flush()
        yield f.name


FakeResult = collections.namedtuple("FakeResult", "returncode stdout")


@contextlib.contextmanager
def cron_mock(cron_returns=["", ""]):
    results = [FakeResult(0, s.encode("utf-8")) for s in cron_returns]
    with mock.patch("subprocess.run", side_effect=results) as mocked:
        yield mocked


class CronInstallTestCase(TestCase):
    def installed_crontab(self, mocked):
        # in our scenario this should always be the input of last call
        last_call = mocked.call_args_list[-1]
        self.assertEqual(last_call[0][0][0], "crontab")
        self.assertEqual(last_call[0][0][-1], "-")
        return last_call[1]["input"].decode("utf-8")

    def test_simple_install(self):
        my_cron = textwrap.dedent(
            """
            # task 1
            22 22 * * * /usr/local/bin/test.1
            # task 1
            */10 * * * * /usr/local/bin/test.2
            """
        )
        with cronfile(my_cron) as fpath, cron_mock() as mocked:
            cmd = Command(marker="MARK", cron_path=fpath, substitutions={})
            cmd.run()
            self.assertEqual(
                self.installed_crontab(mocked), "\n# START MARK\n" + my_cron + "# END MARK",
            )

    def test_install_with_user(self):
        with cronfile("\n#nothing\n") as fpath, cron_mock() as mocked:
            cmd = Command(marker="MARK", cron_path=fpath, substitutions={}, user="bob")
            cmd.run()
            self.assertEqual(mocked.call_count, 2)
            # command always called with "-u bob"
            for args in mocked.call_args_list:
                self.assertIn("-u bob", " ".join(args[0][0]))

    def test_interpolation(self):
        my_cron = textwrap.dedent(
            """
            # task 1
            22 22 * * * /usr/local/bin/$TEST_PROGRAM $TEST_PATH $$TEST_ENV
            """
        )
        interpolated = textwrap.dedent(
            """
            # task 1
            22 22 * * * /usr/local/bin/foo bar/baz $TEST_ENV
            """
        )
        env = {"TEST_PROGRAM": "foo", "TEST_PATH": "bar/baz", "TEST_ENV": "NO!"}
        with cronfile(my_cron) as fpath, cron_mock() as mocked:
            cmd = Command(marker="INTERPOL", cron_path=fpath, substitutions=env)
            cmd.run()
            self.assertEqual(
                self.installed_crontab(mocked),
                "\n# START INTERPOL\n" + interpolated + "# END INTERPOL",
            )

    def test_interpolation_variable_miss(self):
        my_cron = textwrap.dedent(
            """
            # $UNKNOWN
            """
        )
        env = {}
        with cronfile(my_cron) as fpath, cron_mock():
            cmd = Command(marker="X", cron_path=fpath, substitutions=env)
            with self.assertRaises(KeyError) as e:
                cmd.run()
            self.assertIn("UNKNOWN", str(e.exception))

    def test_update(self):
        old_cron = textwrap.dedent(
            """
            # START MARK
            # old task
            22 22 * * * /usr/local/bin/old_prog foo
            22 24 * * * /usr/local/bin/old_prog bar
            # END MARK
            # unrelated
            0 23 1 * * /usr/bin/mail spam
            """
        )
        my_cron = textwrap.dedent(
            """
            # new task
            22 22 * * * /usr/local/bin/new_prog baz
            """
        )
        expected = textwrap.dedent(
            """
            # unrelated
            0 23 1 * * /usr/bin/mail spam

            # START MARK

            # new task
            22 22 * * * /usr/local/bin/new_prog baz
            # END MARK
            """
        ).rstrip()
        with cronfile(my_cron) as fpath, cron_mock([old_cron, ""]) as mocked:
            cmd = Command(marker="MARK", cron_path=fpath, substitutions={})
            cmd.run()
            self.assertEqual(
                self.installed_crontab(mocked), expected,
            )

    def test_update_interpolation(self):
        """Test that updating and interpolation do not mess with unrelated lines
        """
        old_cron = textwrap.dedent(
            """
            # START MARK
            22 22 * * * /usr/local/bin/old_prog foo
            # END MARK
            # unrelated
            0 23 1 * * /usr/bin/mail $SPAM $FOO
            """
        )
        my_cron = textwrap.dedent(
            """
            22 22 * * * /usr/local/bin/new_prog $ARGS $FOO
            """
        )
        expected = textwrap.dedent(
            """
            # unrelated
            0 23 1 * * /usr/bin/mail $SPAM $FOO

            # START MARK

            22 22 * * * /usr/local/bin/new_prog baz foo
            # END MARK
            """
        ).rstrip()
        env = {"ARGS": "baz", "FOO": "foo"}
        with cronfile(my_cron) as fpath, cron_mock([old_cron, ""]) as mocked:
            cmd = Command(marker="MARK", cron_path=fpath, substitutions=env)
            cmd.run()
            self.assertEqual(
                self.installed_crontab(mocked), expected,
            )
