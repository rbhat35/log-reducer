from collections import defaultdict
import logging
import sys

log = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

class FileMap(object):
    std = {'0': 'stdin', '1' : 'stdout', '2' : 'stderr'}
    std_r = {v : k for (k,v) in std.iteritems()}

    def __init__(self):
        self.imap = defaultdict(lambda: dict(self.std))
        self.fmap = self.std

    def get_inode(self, pid, fd):
        """Get inode value for pid, fd pair."""
        key = "{0}:{1}".format(pid, fd)
        return self.imap[pid][fd]

    def add_file(self, pid, fd, fname, inode):
        log.debug("({0}, {1} = {2})".format(pid, fd, inode))
        self.imap[pid][fd]  = inode
        self.fmap[inode] = fname


    def del_file(self, pid, fd):
        """Delete a file from filemap after it has been closed."""
        del self.imap[pid][fd]

    def ino2name(self, inode):
        log.info("inode: {0}".format(inode))
        return self.fmap[inode]
