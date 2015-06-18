#!/usr/bin/env python
#-*- coding: utf-8 -*-
'''
cbibs_api.api
~~~~~~~~~~~~~

API definitions and routes

Copyright 2015 RPS ASA
See LICENSE.txt
'''

from flask import request
from flask_restful import Resource
from cbibs_api import app, api, db
from cbibs_api.utils import check_api_key_and_req_type
from cbibs_api.queries import SQL


class Test(Resource):
    method_decorators = [check_api_key_and_req_type]
    def get(self):
        return {'id': 1, 'error': None, 'result': 'Test successful'}

api.add_resource(Test, '/Test')

class ListConstellations(Resource):
    method_decorators = [check_api_key_and_req_type]
    def get(self):
        res = db.engine.execute(SQL['ListConstellations'])
        constellations = [row.organization for row in res.fetchall()]
        return {'id': 1, 'error': None, 'result': constellations}

api.add_resource(ListConstellations, '/ListConstellations')


# seems somewhat redundant
routing_dict = {
         'Test': Test(),
         'ListConstellations': ListConstellations()
        }

class BaseApi(Resource):
    method_decorators = [check_api_key_and_req_type]
    def get(self):
        return {'id': 1, 'msg': 'Please use POST for the legacy API endpoint',
                'result': None}

    def post(self):
        json_req = request.get_json(force=True)
        api_endpoint = routing_dict[json_req.pop('method')]
        request.args = json_req
        # switch request method to get
        return api_endpoint.get()


api.add_resource(BaseApi, '/')

if __name__ == '__main__':
    app.run(debug=True)
