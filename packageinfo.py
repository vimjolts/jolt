#!/usr/bin/env python
# coding: utf-8

import os



def shift_path(top, dirpath, filename):
    def _shift_path(dir, file):
        if dir == top:
            return dir, file
        else:
            head, tail = os.path.split(dir)
            return _shift_path(head, os.path.join(tail, file))
    assert os.path.isabs(top)
    assert os.path.isabs(dirpath)
    return _shift_path(dirpath, filename)

def split_all(relpath):
    def _split_all(relpath):
        (head, tail) = os.path.split(relpath)
        if head == '':
            return [tail]
        else:
            return split_all(head) + [tail]
    assert not os.path.isabs(relpath)
    return _split_all(relpath)


class PackageInfo:

    class ContainAny:
        """ Always returns True for any filepath. """
        def __call__(self, f):
            return True

    class ContainSuffix:
        """ Returns True if filepath ends with given suffix. """
        def __init__(self, suffix):
            self.suffix = suffix
        def __call__(self, f):
            return f.endswith(self.suffix)

    class ContainSpecialDirs:
        """ Returns True if filepath is under the special directory. """
        def __call__(self, f):
            dirs = split_all(f)
            return dirs and dirs[0] != 'after' and PackageInfo.SPECIAL_DIR_RULES.has_key(dirs[0])

    SPECIAL_DIR_RULES = {
        'after': ContainSpecialDirs(),
        'autoload': ContainSuffix('.vim'),
        'colors': ContainSuffix('.vim'),
        'compiler': ContainSuffix('.vim'),
        # 'dict': ContainAny(),
        'doc': ContainAny(),
        'ftdetect': ContainSuffix('.vim'),
        'ftplugin': ContainSuffix('.vim'),
        'indent': ContainSuffix('.vim'),
        'keymap': ContainAny(),
        'lang': ContainAny(),
        'macros': ContainAny(),
        'plugin': ContainSuffix('.vim'),
        'spell': ContainAny(),
        'syntax': ContainSuffix('.vim'),
        # 'tools': ContainAny(),
        # 'tutor': ContainAny(),
    }
    SPECIAL_DIRS = SPECIAL_DIR_RULES.keys()

    def __init__(self, dir):
        self.dir = dir

    def files(self):
        """ Utility method to get all files under self.dir. """
        for dirpath, dirnames, filenames in os.walk(self.dir):
            for f in filenames:
                yield os.path.join(dirpath, f)

    def dirs(self):
        """ Utility method to get all directories under self.dir. """
        for dirpath, dirnames, filenames in os.walk(self.dir):
            for d in dirnames:
                yield os.path.join(dirpath, d)

    def special_dirs(self):
        """ Returns all PackageInfo.SPECIAL_DIRS in self.dir. """
        return (d
                for d in PackageInfo.SPECIAL_DIRS
                if os.path.isdir(os.path.join(self.dir, d)))

    def is_special_dir(self, dir):
        """ Returns boolean value if dir is in PackageInfo.SPECIAL_DIR_RULES. """
        return PackageInfo.SPECIAL_DIR_RULES.has_key(dir)

    def is_necessary(self, relpath):
        """ Returns boolean value if relpath is necessary file. """
        assert not os.path.isabs(relpath)

        dirs = split_all(relpath)
        if len(dirs) <= 1:
            return False

        d, f = dirs[0], apply(os.path.join, dirs[1:])
        if PackageInfo.SPECIAL_DIR_RULES.has_key(d):
            return PackageInfo.SPECIAL_DIR_RULES[d](f)
        else:
            return False

    def necessary_files(self):
        """ Returns all necessary files. """
        for dirpath, _, filenames in os.walk(self.dir):
            for f in filenames:
                _, f = shift_path(self.dir, dirpath, f)
                if self.is_necessary(f):
                    yield f

    def unnecessary_files(self):
        """ Returns all unnecessary files. """
        for dirpath, _, filenames in os.walk(self.dir):
            for f in filenames:
                _, f = shift_path(self.dir, dirpath, f)
                if not self.is_necessary(f):
                    yield f



def main():
    dir = os.path.join(os.environ['HOME'], ".vim")

    if __debug__:
        print "\n\n\n---------------------- .special_dirs() ----------------------"
        for d in PackageInfo(dir).special_dirs():
            print d

        print "\n\n\n---------------------- .necessary_files() ----------------------"
        for f in PackageInfo(dir).necessary_files():
            print f

        print "\n\n\n---------------------- .unnecessary_files() ----------------------"
        for f in PackageInfo(dir).unnecessary_files():
            print f

        print "\n\n\n---------------------- .dirs() ----------------------"
        for d in PackageInfo(dir).dirs():
            print d

        print "\n\n\n---------------------- .files() ----------------------"
        for f in PackageInfo(dir).files():
            print f


if __name__ == '__main__':
    main()
