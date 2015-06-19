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
from collections import OrderedDict

class BaseResource(Resource):
    keys = None
    def get(self):
        """Responds to GET request and provides a JSON result"""
        return self.result_simple()

    def result_simple(self, result_only=False, insert_vals={},
                      sql_name_override=None):
        """
        A wrapper to return a multiple columns from an SQL call
        :param api_call_str:  The API call to make
        :param params: Any parameters supplied to the API call
        """
        sql_name = (self.__class__.__name__ if not sql_name_override else
                    sql_name_override)
        res = db.engine.execute(SQL[sql_name], request.args)
        json_keys = ['id'] + insert_vals.keys() + ['error', 'result']
        res_vals = zip(*res.fetchall())
        if not result_only:
            res_keys = res.keys()
            results = OrderedDict(zip(res_keys, res_vals))
        else:
            results = res_vals[0]
        vals = [1] + insert_vals.values() + [None, results]
        return OrderedDict(zip(json_keys, vals))



class Test(Resource):
    method_decorators = [check_api_key_and_req_type]
    def get(self):
        return {'id': 1, 'error': None, 'result': 'Test successful'}

api.add_resource(Test, '/Test')

class ListConstellations(BaseResource):
    method_decorators = [check_api_key_and_req_type]
    def get(self):
        return self.result_simple(result_only=True)

api.add_resource(ListConstellations, '/ListConstellations')

class ListPlatforms(BaseResource):
    keys = ['self']
    method_decorators = [check_api_key_and_req_type]
    #def get(self):
    #    return self.result_simple('ListPlatforms')

api.add_resource(ListPlatforms, '/ListPlatforms')

# seems somewhat redundant
routing_dict = {
         'Test': Test(),
         'ListConstellations': ListConstellations(),
         'ListPlatforms': ListPlatforms()
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
