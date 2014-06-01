#!/usr/bin/python
# -*- encoding: utf-8; py-indent-offset: 4 -*-
# +------------------------------------------------------------------+
# |             ____ _               _        __  __ _  __           |
# |            / ___| |__   ___  ___| | __   |  \/  | |/ /           |
# |           | |   | '_ \ / _ \/ __| |/ /   | |\/| | ' /            |
# |           | |___| | | |  __/ (__|   <    | |  | | . \            |
# |            \____|_| |_|\___|\___|_|\_\___|_|  |_|_|\_\           |
# |                                                                  |
# | Copyright Mathias Kettner 2013             mk@mathias-kettner.de |
# +------------------------------------------------------------------+
#
# This file is part of Check_MK.
# The official homepage is at http://mathias-kettner.de/check_mk.
#
# check_mk is free software;  you can redistribute it and/or modify it
# under the  terms of the  GNU General Public License  as published by
# the Free Software Foundation in version 2.  check_mk is  distributed
# in the hope that it will be useful, but WITHOUT ANY WARRANTY;  with-
# out even the implied warranty of  MERCHANTABILITY  or  FITNESS FOR A
# PARTICULAR PURPOSE. See the  GNU General Public License for more de-
# ails.  You should have  received  a copy of the  GNU  General Public
# License along with GNU Make; see the file  COPYING.  If  not,  write
# to the Free Software Foundation, Inc., 51 Franklin St,  Fifth Floor,
# Boston, MA 02110-1301 USA.

#Author: Bastian Kuhn bk@mathias-kettner.de
# enhanced by: Phil Randal phil.randal@gmail.com
# extended by: Andreas Doehler andreas.doehler@gmail.com

#set testing True to output to stdout instead of creating files

testing = False
#testing = False

import os
import sys
import socket

socket_pathlokal = "~/tmp/run/live"
socket_path = os.path.expanduser(socket_pathlokal)

s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
s.connect(socket_path)

# Write command to socket
s.send("GET hosts\nColumns: host_name address\n")

# Important: Close sending direction. That way
# the other side knows we are finished.
s.shutdown(socket.SHUT_WR)

# Now read the answer
answer = s.recv(100000000)

# Parse the answer into a table (a list of lists)
table = [ line.split(';') for line in answer.split('\n')[:-1] ]

# tag mappings
# these correspond to host tags define in WATO

# map each tag dropdown entry to its parent tag
#     or itself if a single checkbox
#     or "" if it is a subtag

tagz = {
# dropdown tags
   'cmk-agent': 'agent',
   'snmp-only': 'agent',
   'snmp-tcp':  'agent',
   'ping': 'agent',

   'prod': 'criticality',
   'critical': 'criticality',
   'test': 'criticality',
   'offline': 'criticality',

   'lan': 'networking',
   'wan': 'networking',
   'dmz': 'networking',

# checkbox tags

   'dns': 'dns',

# subtags

   'snmp': '',
   'tcp': '',

}

try:
    pathlokal = "~/etc/check_mk/conf.d/wato/"
    pathlokal = os.path.expanduser(pathlokal)
    datei = open(sys.argv[1],'r')
except:
    print """Run this script inside a OMD site
    Usage: ./wato_import.py csvfile.csv
    CSV Example:
    wato_foldername;hostname;host_alias;parents;ip_address;tags"""
    sys.exit()

errorz = 0
folders = {}
for line in datei:
    nameexist = False
    line=line.replace('\n',';\n')
    ordner, name, alias, parents, ip, tags = line.split(';')[:6]
    if testing == False:
        if ordner:
          try:
            os.makedirs(pathlokal+ordner)
          except os.error:
            pass
    folders.setdefault(ordner,[])
    for i in table:
        if i[0] == name:
            nameexist = True
    if nameexist == False:
        folders[ordner].append((name,alias,parents,ip,tags))
datei.close()

for folder in folders:
    all_hosts = ""
    host_attributes = ""
    ip_addresses = ""
    alias_details = ""
    parent_details = ""
    for name, alias, parents, ip, tags in folders[folder]:
#      print tags
      tags2 = tags.replace('|\n','')
      all_hosts += "  '%s|%s',\n" % (name, tags2)
      ip_addresses += "  '%s': u'%s',\n" % (name, ip)
      alias_details += "  (u'%s', ['%s']),\n" % (alias, name)
      if parents != '':
          parent_details += "  ('%s', ['%s']),\n" % (parents, name)

      host_attributes += "  '%s': {\n" % (name)
      host_attributes += "    'alias': u'%s',\n" % (alias)
      host_attributes += "    'ipaddress': u'%s',\n" % (ip)
      if parents != '':
          parents2 = parents.replace(",","', '")
          host_attributes += "    'parents': ['%s'],\n" % (parents2)

      # handle tags

      words = tags.split("|")
      for word in words:
        if tagz.has_key(word):
          tg = tagz[word]
          if tg != "":
            host_attributes += "    'tag_%s': '%s',\n" % (tg, word)
        else:
          if word != "":
              print ("host '%s' has unrecognised tag '%s'" % (name,word))
              errorz += 1
      host_attributes = host_attributes[:-2] + "},\n"

    if errorz != 0:
      print "Error(s) detected - aborting"
      sys.exit()

    if testing:
        print ('##########################################\n\n# Folder: %s\n\n') % folder

        print ('all_hosts += [')
        print (all_hosts)
        print (']\n\n')

        print('# Explicit IP addresses\nipaddresses.update({')
        # {'test': u'127.0.0.1'}
        print (ip_addresses[:-2])
        print ('})\n\n')

        print ("# Settings for alias\nextra_host_conf.setdefault('alias', []).extend([")
        # (u'test', ['test')]
        print (alias_details[:-2])
        print ('])\n\n')

        print ("# Settings for parents\nextra_host_conf.setdefault('parents', []).extend([")
        # ('test_parent', ['test'])
        print (parent_details[:-2])
        print ('])\n\n')

        print ('host_attributes.update({')
        print (host_attributes[:-2])
        print ('})\n')
    else:
        ziel = open(pathlokal + folder + '/hosts.mk','a')

        ziel.write('all_hosts += [')
        ziel.write(all_hosts)
        ziel.write(']\n\n')

        ziel.write('# Explicit IP addresses\nipaddresses.update({')
        # {'test': u'127.0.0.1'}
        ziel.write(ip_addresses[:-2])
        ziel.write('})\n\n')

        ziel.write("# Settings for alias\nextra_host_conf.setdefault('alias', []).extend([")
        # (u'test', ['test')]
        ziel.write(alias_details[:-2])
        ziel.write('])\n\n')

        ziel.write("# Settings for parents\nextra_host_conf.setdefault('parents', []).extend([")
        # ('test_parent', ['test'])
        ziel.write(parent_details[:-2])
        ziel.write('])\n\n')

        ziel.write('host_attributes.update({')
        ziel.write(host_attributes[:-2])
        ziel.write('})\n')

        ziel.close()
