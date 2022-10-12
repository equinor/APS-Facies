#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys

from argparse import ArgumentParser

from aps.toolbox.bitmap_to_rms import run as run_convert_bitmap_to_rms
from aps.utils.constants.simple import Debug
from aps.utils.methods import get_specification_file, SpecificationType, get_debug_level, get_model_file_format


def get_arguments():
    parser = ArgumentParser(description="Read a rectangular piece of a bitmap (256 colors) file")
    parser.add_argument('model_file', metavar='FILE', type=str, nargs='?', default='bitmap2rms_model.xml', help="The model file to read from (default: bitmap2rms_model.xml)")
    parser.add_argument('-d', '--debug-level', type=int, default=0, help="Sets the verbosity. 0-4, where 0 is least verbose (default: 0)")
    parser.add_argument('-t', '--test', type=bool, default=False, help="Toggles whether the test script is to be run (default: False)")
    parser.add_argument('--long-help', type=bool, default=False, help="Prints an extended help message")
    return parser.parse_args()


def run(roxar=None, project=None, **kwargs):
    model_file_format = get_model_file_format(**kwargs)
    params = {
      'model_file_name': get_specification_file(_type=SpecificationType.CONVERT_BITMAP, _format=model_file_format, **kwargs),
      'debug_level': get_debug_level(**kwargs),
    }
    run_convert_bitmap_to_rms(params)

def run_cli():
    args = get_arguments()
    if args.long_help:
        print(long_help)
        sys.exit(0)

    run(
        model_file=args.model_file,
        debug_level=Debug(args.debug_level)
    )


# -------------  Main ----------------------
if __name__ == "__main__":
    run_cli()
