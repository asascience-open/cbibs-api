#!/usr/bin/env python
#-*- coding: utf-8 -*-
'''
cbibs_api.controller
~~~~~~~~~~~~~~~~~~~~

Application controller: defines the routes and application logic
'''

from flask import jsonify
from cbibs_api import app, db

@app.route('/test')
def test():
    '''
    Returns a simple JSON encoded message of the string "test successful"
    '''
    return jsonify(msg='test successful')

