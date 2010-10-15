#!/usr/bin/env python
# coding: utf-8

import os
import sys
import urllib
import urllib2
import simplejson
import shutil
import tempfile
import stat
import gzip
import traceback
import re
from urlparse import urlparse

from jolt.record import get_record, delete_record, add_record
from jolt.util   import get_vimhome, get_joltinfo, copytree, extract_vba, extract_tar_gz, extract_zip, invoke_custom_installer, remove_empty_dir, get_joltdir


commands = {}

def jolt_command(name):
    def _jolt_command(handler):
        global commands
        commands[name] = handler
        return handler
    return _jolt_command



def invoke_command(name, args=[]):
    global commands
    if name not in commands:
        print >>sys.stderr, sys.argv[1] + ": unknown command"
        command_help();
    commands[name](*args)



@jolt_command('uninstall')
def command_uninstall(name):
    """Delete files writen in meta-info."""
    info = get_record(name)
    if not info:
        print >>sys.stderr, "%s is not installed" % name
        return
    home = get_vimhome()
    for f in info["files"]:
        f = os.path.join(home, f)
        if os.path.exists(f):
            os.remove(f)
            remove_empty_dir(os.path.dirname(f))
    delete_record(name)

@jolt_command('install')
def command_install(name):
    """Install from remote."""
    if isinstance(name, dict):
        info = name
        name = info["name"]

    if name.startswith("git!"):
        url = name[4:]
        name = urlparse(url).path.split("/").pop()
        info = {
            "name": name,
            "url": url,
            "author": "unknown",
            "description": "%s via %s" % (name, url),
            "version": "unknown",
            "packer": "unknown",
            "requires": "unknown",
            "extractor": "git",
            "installer": "",
        }
    elif name.startswith("svn!"):
        url = name[4:]
        name = urlparse(url).path.split("/").pop()
        info = {
            "name": name,
            "url": url,
            "author": "unknown",
            "description": "%s via %s" % (name, url),
            "version": "unknown",
            "packer": "unknown",
            "requires": "unknown",
            "extractor": "svn",
            "installer": "",
        }
    elif name.startswith("http://"):
        name = urlparse(url).path.split("/").pop()
        info = {
            "name": name,
            "url": url,
            "author": "unknown",
            "description": "%s via %s" % (name, url),
            "version": "unknown",
            "packer": "unknown",
            "requires": "unknown",
            "extractor": "",
            "installer": "",
        }
    else:
        info = get_joltinfo(name)
    if not info:
        print >>sys.stderr, name + ": Jolt not found"
        return

    tmpdir = tempfile.mkdtemp()
    olddir = os.getcwd()
    try:
        os.chdir(tmpdir)

        if info["extractor"] == "git":
            os.system("git clone --depth=1 %s %s" % (info["url"], tmpdir))

            def handle_remove_readonly(func, path, exc):
                """Remove error handler. change file permission and retry delete."""
                excvalue = exc[1]
                if func in (os.rmdir, os.remove):
                    os.chmod(path, stat.S_IRWXU| stat.S_IRWXG| stat.S_IRWXO)
                    func(path)
                else:
                    raise
            shutil.rmtree(os.path.join(tmpdir, ".git"), ignore_errors=False, onerror=handle_remove_readonly)
            # TODO: fix behavior when it's not general vim's runtime path structure.
        elif info["extractor"] == "svn":
            os.system("svn export %s %s" % (info["url"], tmpdir))
        else:
            f = urllib2.urlopen(info["url"])
            filename = f.info()["Content-Disposition"].split("filename=")[1]
            with open(filename, "wb") as f:
                f.write(r.read())

            if filename.endswith(".vba"):
                extract_vba(tmpdir, filename)
                os.remove(filename)
            elif filename.endswith(".vba.gz"):
                with open(filename[:-3], "wb") as f:
                    with gzip.open(filename) as gz:
                        f.write(gz.read())
                os.remove(filename)
                filename = filename[:-3]
                extract_vba(tmpdir, filename)
                os.remove(filename)
            elif filename.endswith(".tar.gz") or filename.endswith(".tar.bz2"):
                extract_tar_gz(tmpdir, filename)
                os.remove(filename)
            elif filename.endswith(".zip"):
                extract_zip(tmpdir, filename)
                os.remove(filename)
            elif info["installer"] in ["plugin", "ftplugin", "syntax", "colors", "doc", "indent", "dict"]:
                os.makedirs(os.path.join(tmpdir, info["installer"]))
                shutil.move(filename, os.path.join(tmpdir, info["installer"], filename))
            elif info["installer"] == "custom":
                invoke_custom_installer(tmpdir, info)

        copytree(tmpdir, get_vimhome(), tmpdir)
        filelist = []
        for root, subdirs, files in os.walk(tmpdir):
            for f in files:
                filelist.append(re.sub("\\\\", "/", os.path.relpath(os.path.join(root, f), tmpdir)))
        info["files"] = filelist

        add_record(name, info)

    except RuntimeError, e:
        print >>sys.stderr, "Exception occured in %s" % tmpdir
        traceback.print_exc()
    finally:
        os.chdir(olddir)
        shutil.rmtree(tmpdir)

@jolt_command('joltinfo')
def command_joltinfo(name):
    """Show jolt-info getting from vimjolts server."""
    info = get_joltinfo(name)
    if not info:
        print >>sys.stderr, "Jolt not installed"
        return
    if 'name' in info:
        print 'Name: %s' % info['name']
    if 'version' in info:
        print 'Version: %s' % info['version']
    if 'description' in info:
        print 'Description: %s' % info['description']
    if 'url' in info:
        print 'URL: %s' % info['url']
    if 'packer' in info:
        print 'Packer: %s' % info['packer']
    if 'requires' in info:
        print 'Requires:'
        for r in info['requires']:
            print '  %s' % r

@jolt_command('search')
def command_search(word):
    """Search the name of package from vimjolts server."""
    f = urllib2.urlopen("http://vimjolts.appspot.com/api/search?" + urllib.urlencode({"word": word}))
    res = simplejson.load(f)
    for r in res:
        print "%s: %s" % (r["name"], r["version"])

@jolt_command('list')
def command_list():
    """Show the names of installed packages."""
    metadir = os.path.join(get_joltdir(), "meta")
    if not os.path.isdir(metadir):
        return
    for f in os.listdir(metadir):
        info = get_record(f)
        if info:
            print "%s: %s" % (f, info["version"])

@jolt_command('update')
def command_update():
    """Update all packages installed."""
    metadir = os.path.join(get_joltdir(), "meta")
    if not os.path.isdir(metadir):
        return
    for f in os.listdir(metadir):
        print "updating %s ..." % f
        info = get_record(f)
        if info:
            command_install(info)
        else:
            command_install(f)

@jolt_command('metainfo')
def command_metainfo(name):
    """Show meta-info of installed package."""
    info = get_record(name)
    if not info:
        print >>sys.stderr, "%s is not installed" % name
        return
    print "\n".join([
        "Name: %s" % info["name"],
        "Version: %s" % info["version"],
        "Description: %s" % info["description"],
        "URL: %s" % info["url"],
        "Packer: %s" % str(info["packer"]),
        "Requires:\n  %s" % "\n  ".join(info["requires"]),
        "Files:\n %s" % "\n  ".join(info["files"])])

@jolt_command('help')
def command_help():
    """Show command usages."""
    print """
Jolt : the Vim Package Management System

commands:
    list:                 list installed packages.
    update:               update all old plugins.
    joltinfo  [package]:  show information of the package via joltserver
    metainfo  [package]:  show information of the package via local cache
    install   [package]:  install the package.
    uninstall [package]:  uninstall the package.
    search    [word]:     search packages from joltserver
"""
    sys.exit(0)
