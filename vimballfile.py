"""
Read vimball files.
"""
import re


class VimballInfo:
    """Class with attributes describing each file in the vimball archive."""

    def __init__(self, filename, body):
        self.filename = filename
        self.body = body


class VimballFile:
    """ Class with methods to read, list vimball files.

    vba = VimballFile(file)

    file: Either the path to the file.
          The file will be opened and closed by VimballFile.
    """

    def __init__(self, file):
        self.file = file
        self.NameToInfo = {}    # Find file info given name
        self.filelist = []      # List of ZipInfo instances for archive

        lines = []
        with open(file, 'r') as f:
            lines = f.readlines()[3:]

        # FIXME: Check the file format.
        while len(lines) != 0:
            filename = re.sub('\t\[\[\[1\n$', '', lines[0]).replace('\\', '/')
            lnum = int(lines[1])
            body = ''.join(lines[2:lnum + 2])
            lines = lines[lnum + 2:]
            info = VimballInfo(filename, body)
            self.filelist.append(info)
            self.NameToInfo[filename] = info

    def namelist(self):
        """Return a list of file names in the archive."""
        l = []
        for data in self.filelist:
            l.append(data.filename)
        return l

    def infolist(self):
        """Return a list of class VimballInfo instances for files in the
        archive."""
        return self.filelist

    def getinfo(self, name):
        """Return the instance of VimballInfo given 'name'."""
        info = self.NameToInfo.get(name)
        if info is None:
            raise KeyError(
                'There is no item named %r in the archive' % name)

        return info
    def read(self, name):
        """Return file bytes (as a string) for name."""
        return self.NameToInfo.get(name).body

# vim:set et ts=4 sw=4:
