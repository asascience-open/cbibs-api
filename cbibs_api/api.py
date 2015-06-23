#!/usr/bin/env python
#-*- coding: utf-8 -*-
'''
cbibs_api.api
~~~~~~~~~~~~~

API definitions and routes

Copyright 2015 RPS ASA
See LICENSE.txt
'''

from flask import request, Response
from flask_restful import Resource
from cbibs_api import app, api, db
from cbibs_api.utils import check_api_key_and_req_type
from cbibs_api.queries import SQL
from defusedxml.xmlrpc import xmlrpc_client
from collections import OrderedDict

class BaseResource(Resource):
    """Base resource which other API endpoints inherit.  Returns a simple
       JSON response, or an XMLRPC response if XML is requested"""
    keys = None
    def get(self):
        """Responds to GET request and provides a JSON result"""
        res = self.result_simple()
        # return JSON if requested
        # return XML in XMLRPC format if XML is requested
        if (request.content_type in ('application/xml', 'text/xml')):
            # unfortunately key order can't be preserved because OrderedDict
            # can't be marshalled in xmlrpc library and has to be converted to
            # a dict
            if hasattr(res, '__dict__'):
                xml_str = xmlrpc_client.dumps((dict(res),), methodresponse=True)
            else:
                xml_str = xmlrpc_client.dumps((res,), methodresponse=True)
            return Response(xml_str, mimetype='text/xml')
        # return the JSON if not XML
        else:
            return res

    def result_simple(self, result_only=False, singleton_result=False,
                      sql_name_override=None):
        """
        A function to return a multiple columns from an SQL call.  The workhorse
        of this API.
        :param result_only:  Boolean controlling whether to return an array
                             (True) or a dict (False) as the result
        :param singleton_result: if result only is True, return the first
                                 result fetched from the database as a scalar
                                 instead of returning an array
        :param sql_name_override: Defaults to None, which causes it to call
                                  an SQL file with the same name as the class,
                                  without the .sql extension.
                                  If a string is supplied, it will use an
                                  sql file with the same name as the string,
                                  minus the extension
        """
        sql_name = (self.__class__.__name__ if not sql_name_override else
                    sql_name_override)
        res = db.engine.execute(SQL[sql_name], request.args)
        res_vals = zip(*res.fetchall())
        if not result_only:
            res_keys = res.keys()
            results = OrderedDict(zip(res_keys, res_vals))
        else:
            # returning several results as a tuple causes incorrect
            # interpretation, return as list instead
            # usually we return a list
            if not singleton_result:
                results = list(res_vals[0])
            # but some methods return a single value
            else:
                results = res_vals[0][0]
        return results



class Test(BaseResource):
    method_decorators = [check_api_key_and_req_type]
    def get(self):
        return self.result_simple(result_only=True, singleton_result=True)

api.add_resource(Test, '/Test')

class ListConstellations(BaseResource):
    method_decorators = [check_api_key_and_req_type]
    def get(self):
        return self.result_simple(result_only=True)

api.add_resource(ListConstellations, '/ListConstellations')

class ListPlatforms(BaseResource):
    keys = ['constellation']
    method_decorators = [check_api_key_and_req_type]

api.add_resource(ListPlatforms, '/ListPlatforms')

routing_dict = {
         'Test': Test(),
         'ListConstellations': ListConstellations(),
         'ListPlatforms': ListPlatforms()
        }

class BaseApi(Resource):
    """Base API which responds to XMLRPC and JSONRPC methods.  This delegates
       to the REST API methods, but adds fields/functionality as needed to
       emulate RPC."""
    method_decorators = [check_api_key_and_req_type]

    # TODO: Add more canonical RPC error returns depending on spec requested
    def get(self):
        return OrderedDict([('id', 1),
                           ('error', 'Please use POST for the legacy API endpoint'),
                           ('result', None)])

    def post(self):
        if ('application/xml' in request.accept_mimetypes or
            'text/xml' in request.accept_mimetypes):
            payload = xmlrpc_client.loads(request.data)
            # load xmlrpc method
            api_endpoint = routing_dict[payload[1]]
            request.args = dict(zip(api_endpoint.keys, payload[0]))
        else:
            # TODO: handle both jsonrpc and xmlrpc requests
            json_req = request.get_json(force=True)
            # grab the api method
            api_endpoint = routing_dict[json_req.pop('method')]
            if 'params' in json_req:
                params = json_req['params']
                # consider eliminating side effects, makes this difficult
                # to understand
                if api_endpoint.keys:
                    json_req.update(dict(zip(api_endpoint.keys, json_req['params'])))
                request.args = json_req
        # switch request method to get
        res = api_endpoint.get()
        # TODO: handle bad endpoint request
        # return a JSONRPC formed response if coming from POST
        if (request.content_type == 'application/json' and
            request.method == 'POST'):
            return OrderedDict([('id', 1), ('error', None), ('result', res)])
        # return XML in XMLRPC format if XML is requested, or if it's a GET
        # request, return only the result from the REST API
        else:
            return res


api.add_resource(BaseApi, '/')

if __name__ == '__main__':
    app.run(debug=True)
