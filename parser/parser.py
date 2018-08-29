#!/usr/bin/python
import auparse
import audit
import sys
import os
from os import path
import json
from collections import defaultdict

class ParseError(Exception):
    pass

file_map = defaultdict(dict)
i_map = defaultdict(dict)


def get_inode(pid, fd):
    """Get inode value for pid, fd pair."""
    s = {'0': 'stdin', '1' : 'stdout', '2' : 'stderr'}

    i_map[pid].update(s)

    if fd in ['0', '1', '2']:
        return s[fd]

    key = "{0}:{1}".format(pid, fd)
    return file_map[key]


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

        print au.get_line_number()

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
            print ','.join(event)

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

        i_map[inode] = name if '.' != name[0] else path.join(cwd + name[1:])
        file_map[key] = inode

        return (subject, inode)

    def handle_read(self, au):
        """syscalls: read, readv"""
        ts = get_ts(au)
        fd = au.find_field('a0')
        subject, pid, _ = get_subject(au)
        inode = get_inode(pid, fd)
        event = (ts, subject, self.syscall, get_inode(pid, fd), i_map[inode])
        return event

    def handle_write(self, au):
        """syscalls: write, writev"""
        ts = get_ts(au)
        fd = au.find_field('a0')
        subject, pid, _ = get_subject(au)
        inode = get_inode(pid, fd)
        event = (ts, subject, self.syscall, get_inode(pid, fd), i_map[inode])
        return event

    def handle_open(self, au):
        """syscalls open"""
        ts = get_ts(au)
        subject, resource = self.handle_new(au)
        if not subject:
            return None
        event = (ts, subject, self.syscall, resource, i_map[resource])
        return event

    def handle_close(self, au):
        """syscalls open"""
        ts = get_ts(au)
        fd = au.find_field('a0')
        subject, pid, _ = get_subject(au)
        inode = get_inode(pid, fd)
        if inode not in ['stdin', 'stdout', 'stderr']:
            filename = i_map[inode]
        else:
            filename = "stdout"
        event = (ts, subject, self.syscall, inode, filename)
        return event



def main():
    au_log = sys.argv[1]
    Parser().parse_file(au_log)

if __name__ == '__main__':
    with open('./sys_table.json') as infile:
        sys_table = json.load(infile)
    main()
