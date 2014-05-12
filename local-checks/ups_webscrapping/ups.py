#!/usr/bin/python
# -*- encoding: utf-8; py-indent-offset: 4 -*-
import urllib2
import json
request = urllib2.Request( r'http://192.168.1.6:8081/cgi-bin/ups_view.exe', 'json=ups')
request.add_header('Content-Type', 'application/json')
response = urllib2.urlopen(request)
a = json.loads(response.read())
b = a.get('ups')
c = b.get('valtable')
d = c.get('BATTCAP')
e = c.get('TEMPDEG')
f = c.get('INVOLT')
print "P UPS-Status temp=%s;30;35|capacity=%s;50:105;25:105|volt=%s;210:235;190:240 USV Status is" % (e , d , f[0])

