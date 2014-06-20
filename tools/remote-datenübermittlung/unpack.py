#!/usr/bin/python

import os
import sys
import email
import errno
import mimetypes

from optparse import OptionParser

def main():
    parser = OptionParser(usage="""Hilfetext""")
    parser.add_option('-d', '--directory',
                      type='string', action='store',
                      help="""Hilfe""")
    opts, args = parser.parse_args()
    if not opts.directory:
        parser.print_help()
        sys.exit(1)

    try:
        msgfile = args[0]
    except IndexError:
        parser.print_help()
        sys.exit(1)

    fp = open(msgfile)
    msg = email.message_from_file(fp)
    fp.close()

    counter = 1
    for part in msg.walk():
        if part.get_content_maintype() == 'multipart' or part.get_content_maintype() == 'text':
            continue
        filename = part.get_filename()
        if not filename:
            continue
        fp = open(os.path.join(opts.directory, filename), 'wb')
        fp.write(part.get_payload(decode=True))
        fp.close()

if __name__ == '__main__':
    main()
