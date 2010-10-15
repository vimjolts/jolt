#!/usr/bin/env python
# coding: utf-8

import os
import sys


config = None

def get_config():
    global config
    if not config:
        config = create_default_config()
    return config


def create_default_config():
    if sys.platform == 'win32':
        vim_home_dir = os.path.expanduser("~/vimfiles")
    else:
        vim_home_dir = os.path.expanduser("~/.vim")

    return {
        'vim_home_dir': vim_home_dir,
    }
