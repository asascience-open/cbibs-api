
#!/usr/bin/env python
#-*- coding: utf-8 -*-
'''
cbibs_api
~~~~~~~~~

Application and project global declarations

Copyright 2015 RPS ASA
See LICENSE.txt
'''

from unittest import TestCase
from cbibs_api import app, db
import cbibs_api.controller
import json

class TestSimple(TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.app = app.test_client()

    def json_headers(self):
        headers = {
            'Content-Type':'application/json;charset=utf-8',
            'Accept':'application/json;charset=utf-8'
        }
        return headers

    def test_simple(self):
        response = self.app.get('/test')
        assert response.status_code == 200
        data = json.loads(response.data)

        assert data['msg'] == 'test successful'
