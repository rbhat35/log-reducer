#!/usr/bin/python
import auparse
import audit
import sys
import os




def parse_syscall(au):
    """ Parse a audit log.

    Warning: Order of parsing matters.
    """
    sysnum = au.find_field('syscall')
    pid = au.find_field('pid')
    exe = au.find_field('exe')
    subject = "{0}:{1}".format(pid, exe)
    event = au.get_timestamp()
    item = au.find_field('item')

    ts = "{0}.{1}.{2}".format(event.sec, event.milli, event.serial)
    event = (ts, subject, sysnum, item)
    print sysnum
    print event


def parse_file(au_log):

    au = auparse.AuParser(auparse.AUSOURCE_FILE, au_log)

    while True:
        au.parse_next_event()
        #print au.get_type(), audit.audit_msg_type_to_name(au.get_type())
        if au.get_type() == 1300:
            parse_syscall(au)
        #print audit.audit_msg_type_to_name(au.get_type()), au.get_type()
        au.next_record()



def main():

    au_log = sys.argv[1]
    parse_file(au_log)



if __name__ == '__main__':
    main()

