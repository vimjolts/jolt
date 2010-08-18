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


class PackageInfo:

    class ContainAny:
        def __call__(self, f):
            return True

    class ContainSuffix:
        def __init__(self, suffix):
            self.suffix = suffix
        def __call__(self, f):
            return f.endswith(self.suffix)

    class ContainSpecialDirs:
        def __call__(self, f):
            def split_all(relpath):
                (head, tail) = os.path.split(relpath)
                if head == '':
                    return [tail]
                else:
                    return split_all(head) + [tail]

            assert not os.path.isabs(f)
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
        """ Utility method to get all files under self.dir """
        for dirpath, dirnames, filenames in os.walk(self.dir):
            for f in filenames:
                yield os.path.join(dirpath, f)

    def dirs(self):
        """ Utility method to get all directories under self.dir """
        for dirpath, dirnames, filenames in os.walk(self.dir):
            for d in dirnames:
                yield os.path.join(dirpath, d)

    def get_special_dirs(self):
        return (d
                for d in PackageInfo.SPECIAL_DIRS
                if os.path.isdir(os.path.join(self.dir, d)))

    def is_necessary(self, sp_dir, f):
        if PackageInfo.SPECIAL_DIR_RULES.has_key(sp_dir):
            return PackageInfo.SPECIAL_DIR_RULES[sp_dir](f)
        else:
            return False

    def get_necessary_files(self):
        for sp_dir in self.get_special_dirs():
            top = os.path.join(self.dir, sp_dir)
            for dirpath, dirnames, filenames in os.walk(top):
                for f in filenames:
                    d, f = shift_path(top, dirpath, f)
                    if self.is_necessary(sp_dir, f):
                        yield os.path.join(sp_dir, f)

    def get_unnecessary_files(self):
        for sp_dir in self.get_special_dirs():
            top = os.path.join(self.dir, sp_dir)
            for dirpath, dirnames, filenames in os.walk(top):
                for f in filenames:
                    d, f = shift_path(top, dirpath, f)
                    if not self.is_necessary(sp_dir, f):
                        yield os.path.join(sp_dir, f)



def main():
    dir = os.path.join(os.environ['HOME'], ".vim")

    if __debug__:
        print "\n\n\n---------------------- .get_special_dirs() ----------------------"
        for d in PackageInfo(dir).get_special_dirs():
            print d

        print "\n\n\n---------------------- .get_necessary_files() ----------------------"
        for f in PackageInfo(dir).get_necessary_files():
            print f

        print "\n\n\n---------------------- .get_unnecessary_files() ----------------------"
        for f in PackageInfo(dir).get_unnecessary_files():
            print f

        print "\n\n\n---------------------- .dirs() ----------------------"
        for d in PackageInfo(dir).dirs():
            print d

        print "\n\n\n---------------------- .files() ----------------------"
        for f in PackageInfo(dir).files():
            print f


if __name__ == '__main__':
    main()
