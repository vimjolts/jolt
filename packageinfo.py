#!/usr/bin/env python
# coding: utf-8

import os


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
            def split_all(fullpath):
                (head, tail) = os.path.split(fullpath)
                if head == '':
                    return [tail]
                else:
                    return split_all(head) + [tail]

            assert(not os.path.isabs(f))
            d = split_all(f)
            return d and os.path.isdir(d[0]) and SPECIAL_DIR_RULES.has_key(d[0])

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

    def get_vim_files(self):
        """ Get *.vim files from self.dir """
        for d in self.get_special_dirs():
            for dirpath, dirnames, filenames in os.walk(self.dir, d):
                for f in filenames:
                    if f.endswith('.vim'):
                        yield os.path.join(dirpath, f)

    def is_necessary(self, sp_dir, f):
        if PackageInfo.SPECIAL_DIR_RULES.has_key(sp_dir):
            return PackageInfo.SPECIAL_DIR_RULES[sp_dir](f)
        else:
            return False

    def get_necessary_files(self):
        for d in self.get_special_dirs():
            for dirpath, dirnames, filenames in os.walk(os.path.join(self.dir, d)):
                for f in filenames:
                    if self.is_necessary(d, f):
                        yield os.path.join(d, f)

    def get_unnecessary_files(self):
        for d in self.get_special_dirs():
            for dirpath, dirnames, filenames in os.walk(os.path.join(self.dir, d)):
                for f in filenames:
                    if not self.is_necessary(d, f):
                        yield os.path.join(d, f)



def main():
    dir = os.path.join(os.environ['HOME'], ".vim")

    # print "\n\n\n---------------------- os.walk() ----------------------"
    # for dirpath, dirnames, filenames in os.walk(PackageInfo(dir).dir):
    #     print dirpath + ":"
    #     for d in dirnames:
    #         print "  [d] " + d
    #     for f in filenames:
    #         print "  [f] " + f

    print "\n\n\n---------------------- .dirs() ----------------------"
    for d in PackageInfo(dir).dirs():
        print d

    print "\n\n\n---------------------- .get_special_dirs() ----------------------"
    for d in PackageInfo(dir).get_special_dirs():
        print d

    print "\n\n\n---------------------- .get_vim_files() ----------------------"
    for f in PackageInfo(dir).get_vim_files():
        print f

    # print "\n\n\n---------------------- file ----------------------"
    # for f in PackageInfo(dir).files():
    #     print f

if __name__ == '__main__':
    main()
