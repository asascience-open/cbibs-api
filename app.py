#!/usr/bin/env python
#-*- coding: utf-8 -*-
'''
app
~~~

Wrapper to launch the application

Copyright 2015 RPS ASA
See LICENSE.txt
'''

from cbibs_api import app
from cbibs_api.api import api

if __name__ == '__main__':
    app.run(host=app.config['HOST'], port=app.config['PORT'])
