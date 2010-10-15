#!/usr/bin/env python
# coding: utf-8

import os
import simplejson
from jolt.util import get_vimhome, get_joltdir


def get_record(name):
    """Get meta-info from local that is stored information about the package."""
    metadir = os.path.join(get_joltdir(), "meta")
    if not os.path.isdir(metadir):
        os.makedirs(metadir)
    metafile = os.path.join(metadir, name)
    info = None
    if os.path.exists(metafile):
        try:
            with open(metafile, "rb") as f:
                info = simplejson.load(f)
        except:
            pass
    return info

def delete_record(name):
    """Delete meta-info file."""
    metadir = os.path.join(get_joltdir(), "meta")
    if not os.path.isdir(metadir):
        os.makedirs(metadir)
    metafile = os.path.join(metadir, name)
    if os.path.exists(metafile):
        os.remove(metafile)

def add_record(name, info):
    """Add meta-info file."""
    metadir = os.path.join(get_joltdir(), "meta")
    if not os.path.isdir(metadir):
        os.makedirs(metadir)
    metafile = os.path.join(metadir, name)
    with open(metafile, "wb") as f:
        simplejson.dump(info, f)
