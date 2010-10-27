#!/usr/bin/env python
# coding: utf-8

import os
import sys


def copy(src, dest):
    pass
def move(src, dest):
    pass
def remove(file):
    pass


SCRIPT_STACK = {
    'copy': copy,
    'move': move,
    'remove': remove,
}


def run(file):
    try:
        exec file in SCRIPT_STACK
    except:
        pass    # TODO: -v,--verbose options can output logging messages.
