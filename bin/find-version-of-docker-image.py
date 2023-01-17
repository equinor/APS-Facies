#!/usr/bin/env python
# -*- coding: utf-8 -*-
# A Utility that extracts the version from a Dockerfile's label
# Written by Sindre Nistad, snis@equinor.com
# Usage: ./find-version-of-docker-image.py [folder in which the Docker file is]

from sys import argv
from os.path import abspath


def get_root_path():
    if len(argv) == 1:
        root_path = abspath('..')
    else:
        root_path = argv[1]
        if root_path[-1] == '/':
            root_path = root_path[:-1]
    return root_path + '/Dockerfile'


def get_docker_image_version(dockerfile):
    with open(dockerfile, 'r', encoding='utf-8') as f:
        for line in f:
            words = line.split()
            if words and words[0].lower() == 'label':
                label = words[1]
                version = label.lstrip('version=').strip('"').strip("'")
                return version
    return ""


def run():
    dockerfile = get_root_path()
    docker_image_version = get_docker_image_version(dockerfile)
    print(docker_image_version)


if __name__ == '__main__':
    run()
