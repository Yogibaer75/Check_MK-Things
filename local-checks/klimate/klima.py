#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-
from bs4 import BeautifulSoup
import urllib2

soup = BeautifulSoup(
    urllib2.urlopen("http://192.168.1.1/UnitT/TNode/index.htm").read(), "html.parser")
# print soup('table')[12]
print("<<<<klima>>>>")
print("<<<local>>>")
tables = [12, 14, 16, 18, 20, 32, 34, 36, 38, 40]
for x in tables:
    name = soup("table")[x].findAll("tr")[0].findAll("td")[1].a.string
    status = soup("table")[x].findAll("tr")[1].findAll("td")[1].string
    statuswert = soup("table")[x].findAll("tr")[1].findAll("td")[3].string
    temp1 = soup("table")[x].findAll("tr")[3].findAll("td")[1].string
    temp1wert = soup("table")[x].findAll("tr")[3].findAll("td")[3].string
    temp2 = soup("table")[x].findAll("tr")[4].findAll("td")[1].string
    temp2wert = soup("table")[x].findAll("tr")[4].findAll("td")[3].string
    name = name.replace(" ", "_")
    if statuswert == "AUS":
        rueck = "2"
    else:
        rueck = "P"
    print("%s %s %s=%s;26.0;28.0|%s=%s;22.0;24.0 %s %s" % (
        rueck,
        name,
        temp1,
        temp1wert,
        temp2,
        temp2wert,
        status,
        statuswert,
    ))
print("<<<<>>>>")
