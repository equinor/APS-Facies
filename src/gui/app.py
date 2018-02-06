#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse

from src.utils.constants.environment import get_commit_hash, get_version_tag

parser = argparse.ArgumentParser(
    prog="APS-GUI",
    description="A GUI for setting parameters to plurigaussian simulations."
)
parser.add_argument('--project', help="Starts the GUI with the given project file")
parser.add_argument(
    '--version',
    action='version',
    version='%(prog)s {version} ({hash})'.format(
        hash=get_commit_hash(),
        version=get_version_tag()
    )
)
parser.add_argument(
    '--verbosity',
    help="Sets the verbosity level. 0 is off, while 4 is the highest",
    type=int,
    choices=[0, 1, 2, 3, 4]
)
args = parser.parse_args()


def run():
    pass


if __name__ == '__main__':
    run()
