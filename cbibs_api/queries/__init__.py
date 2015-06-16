#!/usr/bin/env python
#-*- coding: utf-8 -*-

'''
    cbibs_api.queries
    ~~~~~~~~~~~~~~~~~

    This package serves as a mechanism to import stored SQL queries. Each query
    is stored with the module as a .sql file. On initial load of this module
    each query is loaded into the global variable SQL and is then available to
    any importing clients.

    :copyright: (C) 2015 RPS ASA
    :license: MIT, see LICENSE.txt for more details.
'''

import pkg_resources

SQL = {}

def load():
    '''
    Loads each of the .sql files and places the query into the SQL variable
    with the same name as the file, minus the .sql part.
    '''
    for resource in pkg_resources.resource_listdir(__name__, None):
        if resource.endswith('sql'):
            buf = pkg_resources.resource_string(__name__, resource)
            sql = parse_sql(buf)
            name = resource.replace('.sql','')
            SQL[name] = sql

def parse_sql(buf):
    output = []
    for line in buf.split('\n'):
        if line.startswith('--'):
            continue
        output.append(line)
    return '\n'.join(output)

if len(SQL) == 0:
    load()




