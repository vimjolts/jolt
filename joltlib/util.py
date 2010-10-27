import os
import sys
import urllib
import urllib2
import simplejson
import shutil
import tarfile
import zipfile

from joltlib import config


def get_joltinfo(name):
    """Get jolt-info from server that is stored information about the package."""
    try:
        f = urllib2.urlopen("http://vimjolts.appspot.com/api/entry/byname/%s" % name)
        return simplejson.load(f)
    except:
        return None

def copy_tree(src, dst, basedir=""):
    """Copy directory tree as overwriting. if basedir is set, it wont copy files at upper of basedir."""
    if not os.path.isdir(dst):
        os.makedirs(dst)
    for name in os.listdir(src):
        srcname = os.path.join(src, name)
        dstname = os.path.join(dst, name)
        try:
            if os.path.isdir(srcname):
                copy_tree(srcname, dstname, basedir)
            else:
                #TODO: ignore copying needless files.
                if len(basedir) == 0 or os.path.dirname(srcname) != basedir:
                    shutil.copy2(srcname, dstname)
        except (IOError, os.error), why:
            print "Can't copy %s to %s: %s" % (`srcname`, `dstname`, str(why))

def get_vimhome():
    """Get user's vim home."""
    # 'vim_home_dir' is required.
    return config.get_config()['vim_home_dir']

def get_joltdir():
    c = config.get_config()
    if 'jolt_dir' in c:
        return c['jolt_dir']
    else:
        return os.path.join(get_vimhome(), 'jolt')

def extract_vba(tmpdir, filename):
    """Extract vba file."""
    with open(filename, "rb") as f:
        lines = f.read().split("\n")[3:]
    while len(lines) > 0:
        name = lines.pop(0).split("\t")[0]
        if len(name) == 0:
            break
        td = os.path.dirname(name)
        if len(td) == 0:
            continue
        if not os.path.isdir(td):
            os.makedirs(td)
        count = int(lines.pop(0))
        data = "\n".join(lines[0:count])
        lines = lines[count:]
        with open(name, "wb") as f:
            f.write(data)

def extract_tar_gz(tmpdir, filename):
    """Extract tar.gz/tar.bz2 file."""
    with tarfile.open(filename) as tfile:
        parent_dir = tfile.getmembers()[0].name.split("/")[0]
        has_parent = parent_dir in ["autoload", "colors", "compiler", "doc", "ftplugin", "indent", "keymap", "plugin", "syntax"]
        for tinfo in tfile.getmembers():
            tf = tinfo.name
            if not has_parent:
                tf = "/".join(tf.split("/")[1:])
            td = os.path.dirname(tf)
            if len(td) == 0:
                continue
            if not os.path.isdir(td):
                os.makedirs(td)
            with open(tf, "wb") as f:
                f.write(tfile.extractfile(tinfo.name).read())

def extract_zip(tmpdir, filename):
    """Extract zip file."""
    with zipfile.ZipFile(filename, 'r') as zfile:
        parent_dir = zfile.infolist()[0].filename.split("/")[0]
        has_parent = parent_dir in ["autoload", "colors", "compiler", "doc", "ftplugin", "indent", "keymap", "plugin", "syntax"]
        for zinfo in zfile.infolist():
            zf = zinfo.filename
            if not has_parent:
                zf = "/".join(zf.split("/")[1:])
            zd = os.path.dirname(zf)
            if len(zd) == 0:
                continue
            if not os.path.isdir(zd):
                os.makedirs(zd)
            with open(zf, "wb") as f:
                f.write(zfile.read(zinfo.filename))

def invoke_custom_installer(tmpdir, info):
    """Run custom installer shell(or batch file)."""
    if sys.platform == 'win32':
        with open(os.path.join(tmpdir, "___install.bat"), "wb") as f:
            f.write("@echo off\n")
            f.write(info["installer_win32"])
        os.system("___install.bat")
        os.remove("___install.bat")
    else:
        with open(os.path.join(tmpdir, "___install.sh"), "wb") as f:
            f.write(info["installer_unix"])
            f.write(info["installer_unix"])
        os.system("sh ___install.sh")
        os.remove("___install.sh")

def remove_empty_dir(path):
    if not os.path.exists(path):
        return

    def _remove_empty_dir(path):
        if len(os.listdir(path)) == 0:
            os.rmdir(path)
            p = os.path.dirname(path)
            if p == path:    # root?
                return
            _remove_empty_dir(p)
    _remove_empty_dir(path)
