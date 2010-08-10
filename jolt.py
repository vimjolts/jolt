#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2010 VimJolts Developer Team.

import os
import sys
import re
import urllib
import urllib2
import simplejson
import tempfile
import shutil
from zipfile import ZipFile

def get_record(name):
  metadir = os.path.join(get_vimhome(), "jolts", ".meta")
  if not os.path.isdir(metadir):
    os.makedirs(metadir)
  metafile = os.path.join(metadir, name)
  if not os.path.exists(metafile):
    return None, None
  f = open(metafile, "rb")
  version = f.readline().rstrip()
  files = f.read().split("\n")
  f.close()
  return version, files

def delete_record(name):
  metadir = os.path.join(get_vimhome(), "jolts", ".meta")
  if not os.path.isdir(metadir):
    os.makedirs(metadir)
  metafile = os.path.join(metadir, name)
  if os.path.exists(metafile):
    os.remove(metafile)

def add_record(name, version, files):
  metadir = os.path.join(get_vimhome(), "jolts", ".meta")
  if not os.path.isdir(metadir):
    os.makedirs(metadir)
  metafile = os.path.join(metadir, name)
  f = open(metafile, "wb")
  f.write(version + "\n")
  f.write("\n".join(files))
  f.close()

def get_vimhome():
  if sys.platform == 'win32':
    return os.path.expanduser("~/vimfiles")
  else:
    return os.path.expanduser("~/.vim")

def get_metainfo(name):
  f = urllib2.urlopen("http://vimjolts.appspot.com/api/entry/byname/%s" % name)
  return simplejson.loads(f.read())

def copytree(src, dst):
    names = os.listdir(src)
    if not os.path.isdir(dst):
      os.makedirs(dst)
    for name in names:
        srcname = os.path.join(src, name)
        dstname = os.path.join(dst, name)
        try:
            if os.path.isdir(srcname):
                copytree(srcname, dstname)
            else:
                shutil.copy2(srcname, dstname)
        except (IOError, os.error), why:
            print "Can't copy %s to %s: %s" % (`srcname`, `dstname`, str(why))

def command_uninstall(args):
  name = args[0]
  (version, files) = get_record(name)
  if version is None:
    sys.stderr.write("%s is not installed" % name)
    return
  home = get_vimhome()
  for f in files:
    os.remove(os.path.join(home, f))
  delete_record(name)

def command_install(args):
  name = args[0]
  info = get_metainfo(name)
  if not info:
    sys.stderr.write("jolt not found")
    return

  tmpdir = tempfile.mkdtemp()
  olddir = os.getcwd()
  try:
    os.chdir(tmpdir)

    if info["installer"] == "10":
      r = urllib2.urlopen(info["url"])
      filename = r.info()["Content-Disposition"].split("filename=")[1]
      f = open(filename, "wb")
      f.write(r.read())
      f.close()

    elif info["installer"] == "20":
      r = urllib2.urlopen(info["url"])
      filename = r.info()["Content-Disposition"].split("filename=")[1]
      f = open(filename, "wb")
      f.write(r.read())
      f.close()

      zfilename = os.path.join(tmpdir, filename)
      zfile = ZipFile(zfilename, 'r')
      try:
        parent_dir = zfile.infolist()[0].filename.split("/")[0]
        if parent_dir in ["autoload", "colors", "compiler", "doc", "ftplugin", "indent", "keymap", "plugin", "syntax"]:
          for zinfo in zfile.infolist():
            zf = zinfo.filename
            zd = os.path.dirname(zf)
            if len(zd) == 0:
              continue
            if not os.path.isdir(zd):
              os.makedirs(zd)
            f = open(zf, "wb")
            f.write(zfile.read(zinfo.filename))
            f.close()
        else:
          for zinfo in zfile.infolist():
            zf = "/".join(zinfo.filename.split("/")[1:])
            zd = os.path.dirname(zf)
            if len(zd) == 0:
              continue
            if not os.path.isdir(zd):
              os.makedirs(zd)
            f = open(zf, "wb")
            f.write(zfile.read(zinfo.filename))
            f.close()
      finally:
        zfile.close()
        os.remove(zfilename)

      copytree(tmpdir, get_vimhome())

      filelist = []
      for root, subdirs, files in os.walk(tmpdir):
        for f in files:
          filelist.append("/".join(os.path.split(os.path.relpath(os.path.join(root, f), tmpdir))))
      add_record(name, info["version"], filelist)

  except Exception, e:
    print tmpdir
    print str(e)
  finally:
    os.chdir(olddir)
    shutil.rmtree(tmpdir)

def command_joltinfo(args):
  name = args[0]
  info = get_metainfo(name)
  if not info:
    sys.stderr.write("jolt not found")
    return
  print """
Name: %s
Description: %s
Version: %s
Packer: %s
Requires:
%s
""" % tuple([info[x].strip() for x in ["name", "description", "version", "packer", "requires"]]),

def command_search(args):
  word = args[0]
  f = urllib2.urlopen("http://vimjolts.appspot.com/api/search?" + urllib.urlencode({"word": word}))
  res = simplejson.loads(f.read())
  for r in res:
    print "%s: %s" % (r["name"], r["version"])

def command_metainfo(args):
  name = args[0]
  (version, files) = get_record(name)
  if version is None:
    sys.stderr.write("%s is not installed" % name)
    return
  print """
Version: %s
Files:
  %s
""" % (version, "\n  ".join(files))

def usage():
  print """
jolt : vim package manager
  your vim home: %s

  commands:
    joltinfo [package]  : show information of the package via joltserver
    metainfo [package]  : show information of the package via local cache
    install [package]   : install the package.
    uninstall [package] : uninstall the package.
    search [word]       : search packages from joltserver
""" % get_vimhome()
  sys.exit(0);

if __name__ == '__main__':
  if len(sys.argv) == 1:
    usage()
  commands = {
    "joltinfo" :  command_joltinfo,
    "metainfo" :  command_metainfo,
    "search" :    command_search,
    "install" :   command_install,
    "uninstall" : command_uninstall,
  }
  if sys.argv[1] not in commands:
    usage();
  try:
    commands[sys.argv[1]](sys.argv[2:])
  except KeyboardInterrupt:
    pass
  except:
    # TODO Show stacktrace
    sys.exit(1)

# vim:set et ts=2 sw=2:
