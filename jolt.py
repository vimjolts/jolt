# -*- coding: utf-8 -*-

import sys
import re
import urllib
import simplejson

def get_metainfo(name):
  f = urllib.urlopen("http://vimjolts.appspot.com/api/entry/byname/%s" % name)
  return simplejson.loads(f.read())

def command_info(name):
  info = get_metainfo(name)
  for k in info:
    v = info[k]
    # TODO: formal print
    if v.find("\n") != -1:
      print "%s:\n%s" % (k, re.sub(info[k], "\n", "\n  "))
    else:
      print "%s: %s" % (k, info[k])

def usage():
  print """
jolt : vim package manager

  commands:
    info [package] : show information of package
"""

if __name__ == '__main__':
  try:
    {
      "info" :    command_info,
    }[sys.argv[1]](sys.argv[2])
  except KeyError:
    usage()
  except IndexError:
    usage()

# vim:set et ts=2 sw=2:
