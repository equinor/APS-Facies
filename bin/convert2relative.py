# -*- coding: utf-8 -*-
from os.path import isdir
from os import walk
from argparse import ArgumentParser
from difflib import SequenceMatcher
"""
Converts import statements in the given file(s) to relative imports.
Useful when PYTHONPATH cannot reliably be set.
The main use will be in the .plugin zipfile for RMS 11 plugins.
"""

usage = """./convert2relative.py file [file2] [file3] ...
Where 'file' may be an actual file, or directory
"""


def _get_arguments():
    parser = ArgumentParser(description="Converts import statements to relative imports")
    parser.add_argument('files', metavar='FILE', type=str, nargs='+')
    parser.add_argument('--base-name', type=str, nargs=1, default='src')
    args = parser.parse_args()
    return args.files, args.base_name[0]


def _get_script_folder(source_file, base_name):
    path_from_root = source_file[source_file.find(base_name):]
    dir_path = '/'.join(path_from_root.split('/')[:-1])
    return dir_path


def _get_common_path(script_folder, line):
    script_folder = script_folder.replace('/', '.')
    import_path = line[len('from '):line.find(' from')]
    match = SequenceMatcher(None, script_folder, import_path).find_longest_match(0, len(script_folder), 0, len(import_path))
    return script_folder[match.a:match.a + match.size]


def convert_to_relative_imports(source_file, base_name):
    new_file_lines = []
    script_folder = _get_script_folder(source_file, base_name)
    with open(source_file, 'r') as f:
        lines = f.readlines()
    for line in lines:
        if line.startswith('from ' + base_name):
            common_path = _get_common_path(script_folder, line)
            if common_path.endswith('.'):
                levels = len(script_folder.split('/')) - len(common_path.strip('.').split('.')) + 1
                replacement = 'from ' + ''.join(['.' for _ in range(levels)])
            else:
                replacement = 'from '
            line = line.replace('from ' + common_path, replacement)
        new_file_lines.append(line)
    with open(source_file, 'w') as f:
        f.writelines(new_file_lines)


def run():
    files, base_name = _get_arguments()
    for file in files:
        if isdir(file):
            for root, dirs, file_names in walk(file):
                for source_file in file_names:
                    path = root + '/' + source_file
                    convert_to_relative_imports(path, base_name)
        else:
            convert_to_relative_imports(file, base_name)


if __name__ == '__main__':
    run()
