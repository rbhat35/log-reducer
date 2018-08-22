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


with open('./sys_table.json') as infile:
    sys_table = json.load(infile)


def get_subject(au):
    pid = au.find_field('pid')
    exe = au.find_field('exe')

    subject = "{0}:{1}".format(pid, exe)
    return (subject, pid, exe)

def get_ts(au):
    event = au.get_timestamp()
    ts = "{0}.{1}.{2}".format(event.sec, event.milli, event.serial)
    return ts

def get_rc(au):
    return au.find_field('exit')


def handle_new(au):
    """ Add resource descriptor to map.

    XXX. Order of fields matter when using find_field.

    1. Adds a mapping from <pid>:fd --> inode.
    """
    fd = get_rc(au)
    items = au.find_field('items')
    subject, pid, _ = get_subject(au)

    key = "{0}:{1}".format(pid, fd)
    # Get CWD.
    au.next_record()
    cwd = au.find_field('cwd')
    au.next_record()
    name = au.find_field('name')
    inode = hex(int(au.find_field('inode')))

    i_map[inode] = name if '.' != name[0] else path.join(cwd + name[1:])
    file_map[key] = inode

    return (subject, inode)


def get_inode(pid, fd):
    """Get inode value for pid, fd pair."""
    key = "{0}:{1}".format(pid, fd)
    return file_map[key]


def parse_syscall(au):
    """ Parse a audit log.

    Warning: Order of parsing matters.
    """
    sysnum = au.find_field('syscall')
    syscall = sys_table[sysnum]
    ts = get_ts(au)
    if syscall in ['open', 'execve']:
        # Create file map and inode map.
        subject, resource  = handle_new(au)
        #fd = au.find_field('exit')
        event = (ts, subject, syscall, resource, i_map[resource])
    elif syscall in ['read', 'write']:
        fd = au.find_field('a0')
        subject, pid, _ = get_subject(au)
        inode = get_inode(pid, fd)
        event = (ts, subject, syscall, get_inode(pid, fd), i_map[inode])
    else:
        return

    print ','.join(event)


def parse_file(au_log):
    au = auparse.AuParser(auparse.AUSOURCE_FILE, au_log)

    while au.parse_next_event():
        if au.get_type() == 1300:
            parse_syscall(au)
        au.next_record()


def main():

    au_log = sys.argv[1]
    parse_file(au_log)

if __name__ == '__main__':
    main()
