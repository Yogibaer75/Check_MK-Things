#!/usr/bin/python
# -*- encoding: utf-8; py-indent-offset: 4 -*-
#

def parse_eseries(info):
    parsed = {}
    dev_id = None
    for line in info:
        if len(line) == 2:
            dev_id = line[1]
        elif len(line) >= 10 and dev_id != None:
            data = " ".join(line)
            data_dict = eval(data)
            parsed[dev_id] = data_dict
            dev_id = None
    return parsed

