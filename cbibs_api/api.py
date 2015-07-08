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
from jinja2 import Environment, PackageLoader

# Is this superfluous because of flask?
j2 = Environment(loader=PackageLoader('cbibs_api', 'templates'))

class BaseResource(Resource):
    """Base resource which other API endpoints inherit.  Returns a simple
       JSON response, or an XMLRPC response if XML is requested"""
    # consider renaming to avoid confusion with the dict method
    keys = None
    return_type = "string"
    def __init__(self):
        self.res = self.result_simple()

    def get(self):
        """Responds to GET request and provides a JSON result"""
        return self.res

    def result_simple(self, result_only=False, singleton_result=False,
                      reflect_params=False, sql_name_override=None):
        """
        A function to return a multiple columns from an SQL call.  The workhorse
        of this API.
        :param result_only:  Boolean controlling whether to return an array
                             (True) or a dict (False) as the result
        :param singleton_result: if result only is True, return the first
                                 result fetched from the database as a scalar
                                 instead of returning an array.  These extra
                                 key/value pairs will come at the beginning of
                                 the JSON generated.  OrderedDict or similar
                                 should be used if key ordering is important.
        :param reflect_params: If True, include the passed in parameters as part
                               of the results.  Does not work if result_only
                               is also True.
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
            if reflect_params:
                request_vals = OrderedDict((k, request.args[k]) for k in
                                           self.keys)
                res_keys = request_vals.keys() + res.keys()
                res_vals = request_vals.values() + res_vals
            else:
                res_keys = res.keys()
            results = OrderedDict(zip(res_keys, res_vals))
        else:
            # returning several results as a tuple causes incorrect
            # interpretation, return as list instead
            # usually we return a list
            if reflect_params:
                raise ValueError('reflect_param set but result type set to ' \
                                 'simple')
            if not singleton_result:
                results = list(res_vals[0])
            # but some methods return a single value
            else:
                results = res_vals[0][0]
        return results

    @classmethod
    def get_description(cls):
        if 'xml' in request.content_type:
            protocol = 'XML-RPC'
        else:
            protocol = 'JSON-RPC'
        resource = getattr(cls, 'resource_name', None) or cls.__name__
        arguments = ', '.join(['string %s[req]' % keyname for keyname in cls.keys or []])
        description = 'CDRH %(protocol)s %(resource)s Function (%(arguments)s)' % locals()
        return getattr(cls, 'helpstring', None) or description

class Test(BaseResource):
    keys = []
    method_decorators = [check_api_key_and_req_type]
    def get(self):
        return self.result_simple(result_only=True, singleton_result=True)

api.add_resource(Test, '/Test')

class ListConstellations(BaseResource):
    keys = []
    method_decorators = [check_api_key_and_req_type]
    def get(self):
        return self.result_simple(result_only=True)

api.add_resource(ListConstellations, '/ListConstellations')

class ListPlatforms(BaseResource):
    keys = ['constellation']
    method_decorators = [check_api_key_and_req_type]

api.add_resource(ListPlatforms, '/ListPlatforms')


class GetNumberMeasurements(BaseResource):
    keys = ['constellation', 'stationid', 'measurement',
            'beg_date', 'end_date']
    method_decorators = [check_api_key_and_req_type]
    def get(self):
        return self.result_simple(result_only=True, singleton_result=True)

api.add_resource(GetNumberMeasurements, '/GetNumberMeasurements')

class LastMeasurementTime(BaseResource):
    keys = ['constellation', 'stationid', 'measurement']
    method_decorators = [check_api_key_and_req_type]
    def get(self):
        return str(self.result_simple(result_only=True, singleton_result=True))

api.add_resource(LastMeasurementTime, '/LastMeasurementTime')

class RetrieveCurrentReadings(BaseResource):
    keys = ['constellation', 'station']
    method_decorators = [check_api_key_and_req_type]
    def get(self):
        return self.result_simple(reflect_params=True)

api.add_resource(RetrieveCurrentReadings, '/RetrieveCurrentReadings')

class ListStationsWithParam(BaseResource):
    keys = ['constellation', 'parameter']
    method_decorators = [check_api_key_and_req_type]
    def get(self):
        return self.result_simple(result_only=True)

api.add_resource(ListStationsWithParam, '/ListStationsWithParam')

class ListParameters(BaseResource):
    keys = ['constellation', 'stationid']
    method_decorators = [check_api_key_and_req_type]
    def get(self):
        return self.result_simple(result_only=True)

api.add_resource(ListParameters, '/ListParameters')

class QueryData(BaseResource):
    """Fetches data within a time range"""
    keys = ['constellation', 'stationid', 'measurement',
            'beg_date', 'end_date']
    method_decorators = [check_api_key_and_req_type]

    def get(self):
        return {
            'measurement' : self.res['measurement'][0],
            'units' : self.res['units'][0],
            'values' : {
                'time' : self.res['time'],
                'value' : [float(v) for v in self.res['value']]
            }
        }

api.add_resource(QueryData, '/QueryData')

class RetrieveCurrentSuperSet(BaseResource):
    keys = ['superset']
    method_decorators = [check_api_key_and_req_type]
    def get(self):
        return self.result_simple()

api.add_resource(RetrieveCurrentSuperSet, '/RetrieveCurrentSuperSet')

class ListMethods(BaseResource):
    keys = []
    def __init__(self):
        self.res = routing_dict.keys()

    def get(self):
        return self.res

api.add_resource(ListMethods, '/system/listMethods')

class MethodHelp(BaseResource):
    keys = ['methodname']
    def __init__(self):
        self.res = routing_dict[request.args['methodname']].get_description()

    def get(self):
        return self.res

api.add_resource(MethodHelp, '/system/methodHelp')

class MethodSignature(BaseResource):
    keys = ['methodname']
    def __init__(self):
        cls = routing_dict[request.args['methodname']]
        args = cls.keys or []
        self.res = [[cls.return_type] + ["string" for s in args]] # Nested lists on purpose

api.add_resource(MethodSignature, '/system/methodSignature')

class GetCapabilities(BaseResource):
    keys = []
    def __init__(self):
        self.res = {
            "introspection": {
                "specUrl": "http://phpxmlrpc.sourceforge.net/doc-2/ch10.html",
                "specVersion": 2
            },
            "json-rpc": {
                "specUrl": "http://json-rpc.org/wiki/specification",
                "specVersion": 1
            },
            "xmlrpc": {
                "specUrl": "http://www.xmlrpc.com/spec",
                "specVersion": 1
            }
        }

api.add_resource(GetCapabilities, '/system/getCapabilities')

class GetStationStatus(BaseResource):
    keys = ['constellation', 'station']
    method_decorators = [check_api_key_and_req_type]
    return_type = "int"
    def get(self):
        return int(not self.res)

api.add_resource(GetStationStatus, '/GetStationStatus')


class QueryDataRaw(BaseResource):
    keys = ['constellation', 'stationid', 'measurement', 'beg_date', 'end_date']
    method_decorators = [check_api_key_and_req_type]

    def get(self):
        return {
            'measurement' : self.res['measurement'][0],
            'units' : self.res['units'][0],
            'values' : {
                'time' : self.res['time'],
                'value' : [float(v) for v in self.res['value']]
            }
        }

api.add_resource(QueryDataRaw, '/QueryDataRaw')

class GetMetaDataLocation(BaseResource):
    keys = ['constellation', 'stationid']
    method_decorators = [check_api_key_and_req_type]

    def get(self):
        return {
            'latitude':self.res['latitude'][0],
            'longitude':self.res['longitude'][0]
        }

api.add_resource(GetMetaDataLocation, '/jsonrpc/GetMetaDataLocation')

class QueryDataSimple(BaseResource):
    keys = ['constellation', 'stationid', 'measurement', 'beg_date', 'end_date']
    method_decorators = [check_api_key_and_req_type]
    
    def __init__(self):
        self.res = self.result_simple(sql_name_override='QueryData')

    def get(self):
        return {
            'time' : self.res['time'],
            'value' : [float(v) for v in self.res['value']]
        }

api.add_resource(QueryDataSimple, '/QueryDataSimple')

class QueryDataByTime(BaseResource):
    keys = ['constellation', 'stationid', 'measurement', 'beg_date', 'end_date']
    method_decorators = [check_api_key_and_req_type]
    def __init__(self):
        self.res = self.result_simple(sql_name_override='QueryData')

    def get(self):
        template = j2.get_template('query_data_by_time.xml.j2')
        rows = []
        for i,t in enumerate(self.res['time']):
            rows.append([t, self.res['measurement'][i], self.res['value'][i], self.res['units'][i]])
        payload = template.render(rows=rows)
        return payload

api.add_resource(QueryDataByTime, '/QueryDataByTime')

class ListQACodes(BaseResource):
    keys = []
    method_decorators = [check_api_key_and_req_type]

api.add_resource(ListQACodes, '/ListQACodes')


# TODO: could dry this up by making a helper function for the API
# instead of repeating every time
routing_dict = {
         'Test': Test,
         'ListConstellations': ListConstellations,
         'ListPlatforms': ListPlatforms,
         'ListStationsWithParam': ListStationsWithParam,
         'QueryData': QueryData,
         'GetNumberMeasurements': GetNumberMeasurements,
         'LastMeasurementTime': LastMeasurementTime,
         'RetrieveCurrentReadings': RetrieveCurrentReadings,
         'ListParameters' : ListParameters,
         'RetrieveCurrentSuperSet' : RetrieveCurrentSuperSet,
         'system.listMethods' : ListMethods,
         'system.methodHelp' : MethodHelp,
         'system.methodSignature' : MethodSignature,
         'system.getCapabilities' : GetCapabilities,
         'GetStationStatus' : GetStationStatus,
         'QueryDataRaw' : QueryDataRaw,
         'GetMetaDataLocation' : GetMetaDataLocation,
         'QueryDataSimple' : QueryDataSimple,
         'QueryDataByTime': QueryDataByTime,
         'ListQACodes' : ListQACodes,
         'xmlrpc_cdrh.ListStationsWithParam' : ListStationsWithParam,
         'xmlrpc_cdrh.RetrieveCurrentReadings' : RetrieveCurrentReadings, 
         'xmlrpc_cdrh.LastMeasurementTime' : LastMeasurementTime,
         'xmlrpc_cdrh.QueryData' : QueryData,
         'xmlrpc_cdrh.ListConstellations' : ListConstellations,
         'xmlrpc_cdrh.ListQACodes' : ListQACodes,
         'xmlrpc_cdrh.ListPlatforms' : ListPlatforms,
         'xmlrpc_cdrh.ListParameters' : ListParameters,
         'xmlrpc_cdrh.GetNumberMeasurements' : GetNumberMeasurements,
         'xmlrpc_cdrh.RetrieveCurrentSuperSet' : RetrieveCurrentSuperSet,
         'xmlrpc_cdrh.GetStationStatus' : GetStationStatus,
         'xmlrpc_cdrh.QueryDataByTime' : QueryDataByTime,
         'xmlrpc_cdrh.GetMetaDataLocation' : GetMetaDataLocation,
         'xmlrpc_cdrh.QueryDataSimple' : QueryDataSimple,
         'xmlrpc_cdrh.QueryDataRaw' : QueryDataRaw
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

        if 'application/xml' in request.accept_mimetypes or 'text/xml' in request.accept_mimetypes:
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
        # call api endpoint with current request context
        # and switch request method to get
        res = api_endpoint().get()
        # TODO: handle bad endpoint request
        # return a JSONRPC formed response if coming from POST
        if (request.content_type == 'application/json' and
            request.method == 'POST'):
            return OrderedDict([('id', 1), ('error', None), ('result', res)])
        # return XML in XMLRPC format if XML is requested, or if it's a GET
        # request, return only the result from the REST API
        elif 'xml' in request.content_type:
            if hasattr(res, '__dict__'):
                xml_str = xmlrpc_client.dumps((dict(res),), methodresponse=True)
            else:
                xml_str = xmlrpc_client.dumps((res,), methodresponse=True)
            return Response(xml_str, mimetype='text/xml')
        return jsonify(error='Invalid request'), 400


api.add_resource(BaseApi, '/')

if __name__ == '__main__':
    app.run(debug=True)
