#!/usr/bin/env python
# coding: utf-8

import os
import sys

def get_vimhome():
  """Get user's vim home."""
  if os.environ.has_key('JOLT_VIM_HOME_DIR'):
    return os.environ['JOLT_VIM_HOME_DIR']
  elif sys.platform == 'win32':
    return os.path.expanduser("~/vimfiles")
  else:
    return os.path.expanduser("~/.vim")
