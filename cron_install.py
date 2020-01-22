#!/usr/bin/env python3
"""
This script will run on the host.

It will be triggered by gitlab-ci to install crontabs
"""
import argparse
import os
import subprocess
import sys
from string import Template


class OptionError(Exception):
    """Error in arguments to Command"""


class Command:
    """Handle the actual job of editing crontab
    """

    def __init__(self, marker, cron_path=None, substitutions={}, user=None, remove=False):
        self.marker = marker
        self.cron_path = cron_path
        self.substitutions = substitutions
        self.user = user
        self.remove = remove
        self.check_args()

    def check_args(self):
        if self.cron_path and self.remove:
            raise OptionError("Do not use a cronpath with remove option")
        elif not self.cron_path and not self.remove:
            raise OptionError("Provide a file to install in crontab, or activate remove option")

    @property
    def marker_start(self):
        return "# START " + self.marker

    @property
    def marker_end(self):
        return "# END " + self.marker

    def cron_cmd(self, *options):
        cmd = ["crontab"]
        if self.user:
            cmd.extend(["-u", self.user])
        cmd.extend(options)
        return cmd

    def cron_actual(self):
        result = subprocess.run(
            self.cron_cmd("-l"), stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
        lines = result.stdout.decode("utf-8").split("\n")
        return lines

    def cron_new(self, cron_actual, cron_block):
        in_block = False
        marker_start, marker_end = self.marker_start, self.marker_end
        for line in cron_actual:
            if not in_block and line == marker_start:
                in_block = True
            elif in_block and line == marker_end:
                in_block = False
            elif not in_block:
                yield line
        if not self.remove:
            # add our commands at the end
            yield self.marker_start
            for line in cron_block:
                yield line
            yield self.marker_end

    def cron_block(self):
        if not self.remove:
            substitutions = self.substitutions
            with open(self.cron_path) as f:
                for line in f:
                    line = line[:-1]  # remove final /n
                    template = Template(line)
                    yield template.substitute(substitutions)

    def cron_install(self, cron_lines):
        cron_tab = ("\n".join(cron_lines)).encode("utf-8")
        result = subprocess.run(self.cron_cmd("-"), input=cron_tab)
        return result.returncode

    def run(self):
        cron_actual = self.cron_actual()
        cron_block = list(self.cron_block())
        cron_lines = self.cron_new(cron_actual, cron_block)
        returncode = self.cron_install(cron_lines)
        return returncode


def parse(args=None):
    parser = argparse.ArgumentParser(
        description="Install commands in crontab, identifying them with a marker for later updates"
    )
    parser.add_argument(
        "-m", "--marker", required=True, help="The marker will be placed around crontab entries"
    )
    parser.add_argument("-u", "--user", help="Wich user crontab to affect")
    parser.add_argument(
        "--remove", action="store_true", help="Remove lines in crontab associated with marker"
    )
    parser.add_argument("cron_path", nargs="?", help="path of commands to update in crontab")

    return parser.parse_args(args)


if __name__ == "__main__":
    options = parse()
    try:
        runner = Command(
            marker=options.marker,
            cron_path=options.cron_path,
            substitutions=os.environ,
            user=options.user,
            remove=options.remove,
        )
        returncode = runner.run()
        if returncode != 0:
            print("Error while installing crontab !", file=sys.stderr)
    except OptionError as e:
        print("Error:", str(e), file=sys.stderr)
        returncode = -1
    exit(returncode)
