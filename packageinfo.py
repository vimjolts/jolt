#!/usr/bin/env python
# coding: utf-8

import os


class PackageInfo:

    SPECIAL_DIRS = [
        'after',
        'autoload',
        'colors',
        'compiler',
        # 'dict',
        'doc',
        'ftdetect',
        'ftplugin',
        'indent',
        'keymap',
        'lang',
        'macros',
        'plugin',
        'spell',
        'syntax',
        # 'tools',
        # 'tutor',
    ]

    def __init__(self, dir):
        self.dir = dir

    def walk(self):
        """ Utility method to walk self.dir """
        for w in os.walk(self.dir):
            yield w

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
            for dirpath, dirnames, filenames in os.walk(d):
                for f in filenames:
                    if f.endswith('.vim'):
                        yield os.path.join(dirpath, f)




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

    # print "\n\n\n---------------------- file ----------------------"
    # for f in PackageInfo(dir).files():
    #     print f

if __name__ == '__main__':
    main()
