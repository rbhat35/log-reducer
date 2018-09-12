#!/usr/bin/python
import auparse
import audit
import logging
import sys
import os
from os import path
import json
from collections import defaultdict

from modules import FileMap, Stream, Event

log = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

class ParseError(Exception):
    pass


def get_ts(au):
    event = au.get_timestamp()
    ts = "{0}.{1}.{2}".format(event.sec, event.milli, event.serial)
    return ts

def get_rc(au):
    return au.find_field('exit')


def get_subject(au):
    pid = au.find_field('pid')
    exe = au.find_field('exe')

    subject = "{0}:{1}".format(pid, exe)
    return (subject, pid, exe)

class Parser(object):
    first = True

    def __init__(self):
        self.fmap = FileMap()
        self.in_flow = Stream("forward.csv")
        self.out_flow = Stream("backwards.csv")

    def parse_file(self, au_log):
        """Parse an audit log saved in a file."""
        au = auparse.AuParser(auparse.AUSOURCE_FILE, au_log)

        while au.parse_next_event():
            if au.get_type() == 1300:
                self.parse_syscall(au)
            au.next_record()

    def parse_syscall(self, au):
        """ Parse a audit log.

        Warning: Order of parsing matters.
        """
        sysnum = au.find_field('syscall')
        self.syscall = sys_table[sysnum]

        #XXX. First syscall is the close() before the execve() for the tracing.
        if self.first:
            self.first = False
            return

        log.debug("Parsing syscall: {0}".format(self.syscall))
        if self.syscall in ['open', 'execve']:
            event = self.handle_open(au)
            #event = (ts, subject, self.syscall, resource, i_map[resource])
        elif self.syscall in ['read', 'readv']:
            event = self.handle_read(au)
        elif self.syscall in ['write', 'writev']:
            event = 'not used.'
            #event = self.handle_write(au)
        elif self.syscall in ['close']:
            event = self.handle_close(au)
        else:
            event = "not used."

        if event and event != 'not used.':
            print event

    def handle_new(self, au):
        """ Add resource descriptor to map.

        XXX. Order of fields matter when using find_field.

        1. Adds a mapping from <pid>:fd --> inode.
        """
        fd = get_rc(au)

        if int(fd) < 0:
            return (None, None)


        items = au.find_field('items')
        subject, pid, _ = get_subject(au)

        key = "{0}:{1}".format(pid, fd)

        # Get CWD.
        au.next_record()
        cwd = au.find_field('cwd')
        au.next_record()
        name = au.find_field('name')

        if fd not in ['0', '1', '2']:
            inode = hex(int(au.find_field('inode')))
        else:
            # stdin, stdout, ...
            inode = fd

        name = name if '.' != name[0] else path.join(cwd + name[1:])
        self.fmap.add_file(pid, fd, name, inode)

        return (subject, inode)

    def handle_read(self, au):
        """syscalls: read, readv"""
        ts = get_ts(au)
        fd = au.find_field('a0')
        subject, pid, _ = get_subject(au)

        inode = self.fmap.get_inode(pid, fd)
        name = self.fmap.ino2name(inode)
        event = Event(ts, subject, self.syscall, self.fmap.get_inode(pid, fd), name)
        self.in_flow.write(event)

    def handle_write(self, au):
        """syscalls: write, writev"""
        ts = get_ts(au)
        fd = au.find_field('a0')
        subject, pid, _ = get_subject(au)

        inode = self.fmap.get_inode(pid, fd)
        name = self.ino2name(inode)
        event = Event(ts, subject, self.syscall, self.fmap.get_inode(pid, fd), name)
        self.out_flow.write(event)

    def handle_open(self, au):
        """syscalls open"""
        ts = get_ts(au)
        subject, resource = self.handle_new(au)
        if not subject:
            return None

        name = self.fmap.ino2name(resource)
        event = Event(ts, subject, self.syscall, resource, name)
        #XXX. Are opens necessary to store?
        self.in_flow.write(event)

    def handle_close(self, au):
        """syscalls open"""
        ts = get_ts(au)
        fd = au.find_field('a0')
        subject, pid, _ = get_subject(au)
        #XXX. Delete the fd related to this file.

        inode = self.fmap.get_inode(pid, fd)
        filename = self.fmap.ino2name(inode)
        #self.fmap.del_file(pid, fd)

        event = Event(ts, subject, self.syscall, inode, filename)
        self.out_flow.write(event)


def main():
    au_log = sys.argv[1]
    Parser().parse_file(au_log)

if __name__ == '__main__':
    with open('./sys_table.json') as infile:
        sys_table = json.load(infile)
    main()
