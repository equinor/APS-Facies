#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Usage ./gather-python-files.py CODE_DIR APS_DIR
# Finds all Python files in CODE_DIR/src and adds them to APS_DIR/src with the same hierarchy

from os import walk, makedirs
from os.path import exists
from sys import argv
from shutil import copyfile
from pathlib import Path


def gather_files(source_dir, file_ending):
    files = []
    for dir_path, _, file_names in walk(source_dir):
        for file_name in file_names:
            if file_name.endswith(file_ending):
                files.append(dir_path + '/' + file_name)
    return files


def get_relative_paths(files, code_dir):
    return [name.replace(str(code_dir), '').strip('/') for name in files]


def copy_files(files, source_dir, target_dir):
    for file in files:
        source = str(source_dir / file)
        target = str(target_dir / file)
        target_file_dir = '/'.join(target.split('/')[:-1])
        if not exists(target_file_dir):
            makedirs(target_file_dir, exist_ok=True)
        copyfile(source, target, follow_symlinks=True)


def run():
    assert len(argv) == 3
    code_dir = Path(argv[1]).absolute()
    source_dir = str(code_dir / 'src')
    target_dir = Path(argv[2]).absolute()

    files = gather_files(source_dir, file_ending='py')
    files = get_relative_paths(files, code_dir)
    copy_files(files, code_dir, target_dir)


if __name__ == '__main__':
    run()
