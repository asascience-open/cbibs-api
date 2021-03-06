#!/usr/bin/env python
#-*- coding: utf-8 -*-
'''
cbibs_api.api
~~~~~~~~~~~~~

API definitions and routes

Copyright 2015 RPS ASA
See LICENSE.txt
'''

from flask import request, Response, jsonify
from flask_restful import Resource
from cbibs_api import app, api, db
from cbibs_api.utils import check_api_key_and_req_type, UnauthorizedError, request_wants_xml, request_wants_json
from cbibs_api.utils import output_json, output_xml
from cbibs_api.queries import SQL
from defusedxml.xmlrpc import xmlrpc_client
from collections import OrderedDict
from werkzeug.wrappers import Response as ResponseBase
from flask_restful.utils import error_data, unpack
from jinja2 import Environment, PackageLoader
from copy import copy
from dateutil.relativedelta import relativedelta
from dateutil.parser import parse as dateparse
from datetime import datetime
import pandas as pd

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
        args = copy(cls.keys)
        if check_api_key_and_req_type in cls.method_decorators:
            args += ['api_key']
        arguments = ', '.join(['string %s[req]' % keyname for keyname in args or []])
        description = 'CDRH %(protocol)s %(resource)s Function (%(arguments)s)' % locals()
        return getattr(cls, 'helpstring', None) or description

class ListConstellations(BaseResource):
    keys = []
    method_decorators = [check_api_key_and_req_type]
    def get(self):
        return self.result_simple(result_only=True)


class ListPlatforms(BaseResource):
    keys = ['constellation']
    method_decorators = [check_api_key_and_req_type]


class GetNumberMeasurements(BaseResource):
    keys = ['constellation', 'station', 'measurement',
            'beg_date', 'end_date']
    method_decorators = [check_api_key_and_req_type]
    def get(self):
        return self.result_simple(result_only=True, singleton_result=True)

class LastMeasurementTime(BaseResource):
    keys = ['constellation', 'station', 'measurement']
    method_decorators = [check_api_key_and_req_type]
    def get(self):
        return str(self.result_simple(result_only=True, singleton_result=True))

class RetrieveCurrentReadings(BaseResource):
    keys = ['constellation', 'station']
    method_decorators = [check_api_key_and_req_type]
    def __init__(self):
        sql_name = self.__class__.__name__
        self.constellation = request.args.get('constellation', 'cbibs')
        self.station = request.args.get('station')
        now = datetime.utcnow()
        start_date = now - relativedelta(weeks=2)
        params = {'constellation':self.constellation, 'station':self.station, 'start_date':start_date}
        self.table = pd.read_sql(SQL[sql_name], db.engine, params=params)
        self.table = self.table[~self.table['obs_value'].isnull()]
        self.table = self.table[~self.table['primary_qc'].isin([3,4])]
        blacklist = [
            'sea_water_freezing_point',
            'error_count'
        ]
        self.table = self.table[~self.table['measurement'].isin(blacklist)]
        self.table = self.table.sort(['measure_ts', 'measurement'])
    def get(self):
        '''
        '''

        '''
        Table has
        - measure_ts
        - measurement (name+depth)
        - obs_value
        - canonical_units
        - primary_qc
        '''


        variables = self.table['measurement'].unique()
        values = []
        times = []
        units = []
        report_names = []
        for variable in variables:
            row = self.table[(self.table['measurement'] == variable)].iloc[-1]
            times.append(row['measure_ts'].strftime('%Y-%m-%d %H:%M:%S'))
            values.append(row['obs_value'].item())
            units.append(row['canonical_units'])
            report_names.append(row['report_name'])
        self.res = OrderedDict([
            (u'constellation', self.constellation),
            (u'station', self.station),
            (u'measurement',tuple(variables)),
            (u'time', times),
            (u'value', values),
            (u'units', units),
            (u'report_name', report_names)
        ])

        return self.res

class ListStationsWithParam(BaseResource):
    keys = ['constellation', 'parameter']
    method_decorators = [check_api_key_and_req_type]
    def get(self):
        return self.result_simple(result_only=True)

class ListParameters(BaseResource):
    keys = ['constellation', 'station']
    method_decorators = [check_api_key_and_req_type]
    def get(self):
        return self.result_simple(result_only=True)

class QueryData(BaseResource):
    """Fetches data within a time range"""
    keys = ['constellation', 'station', 'measurement',
            'beg_date', 'end_date']
    method_decorators = [check_api_key_and_req_type]
    def __init__(self, sql_name=None):
        sql_name = sql_name or self.__class__.__name__
        self.constellation = request.args.get('constellation', 'CBIBS')
        self.station = request.args.get('station')
        beg_date = dateparse(request.args.get('beg_date'), ignoretz=True)
        end_date = dateparse(request.args.get('end_date'), ignoretz=True)
        params = {
            'constellation': self.constellation,
            'station': self.station,
            'beg_date': beg_date.isoformat() + 'Z',
            'end_date': end_date.isoformat() + 'Z'
        }
        self.table = pd.read_sql(SQL[sql_name], db.engine, params=params)
        self.table = self.table[self.table['obs_value'].notnull()]
        self.table = self.table[self.table['measurement'] == request.args.get('measurement')]
        self.table = self.table[~self.table['primary_qc'].isin([3,4])]
        self.table = self.table.sort(['measure_ts'])


    def get(self):

        if len(self.table) < 1:
            return {}
        retval = {
            'measurement' : request.args.get('measurement'),
            'report_name' : self.table.iloc[-1]['report_name'],
            'units' : self.table.iloc[-1]['units'],
            'values' : {
                'time' : [t.strftime('%Y-%m-%d %H:%M:%S') for t in self.table['measure_ts']],
                'value' : self.table['obs_value'].values.tolist()
            }
        }
        return retval

class RetrieveCurrentSuperSet(BaseResource):
    keys = ['superset']
    method_decorators = [check_api_key_and_req_type]
    def get(self):
        return self.result_simple()

class ListMethods(BaseResource):
    keys = []
    def __init__(self):
        self.res = routing_dict.keys()

    def get(self):
        return self.res

class MethodHelp(BaseResource):
    keys = ['methodname']
    def __init__(self):
        self.res = routing_dict[request.args['methodname']].get_description()

    def get(self):
        return self.res

class MethodSignature(BaseResource):
    keys = ['methodname']
    def __init__(self):
        cls = routing_dict[request.args['methodname']]
        args = cls.keys or []
        self.res = [[cls.return_type] + ["string" for s in args]] # Nested lists on purpose

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

class GetStationStatus(BaseResource):
    keys = ['constellation', 'station']
    method_decorators = [check_api_key_and_req_type]
    return_type = "int"
    def get(self):
        return int(not self.res)

class QueryDataRaw(BaseResource):
    keys = ['constellation', 'station', 'measurement', 'beg_date', 'end_date']
    method_decorators = [check_api_key_and_req_type]

    def get(self):
        return {
            'measurement' : self.res['measurement'][0],
            'report_name' : self.res['report_name'][0],
            'units' : self.res['units'][0],
            'values' : {
                'time' : self.res['time'],
                'value' : [float(v) for v in self.res['value']]
            }
        }

class GetMetaDataLocation(BaseResource):
    keys = ['constellation', 'station']
    method_decorators = [check_api_key_and_req_type]

    def get(self):
        return {
            'latitude':self.res['latitude'][0],
            'longitude':self.res['longitude'][0]
        }

class QueryDataSimple(QueryData):
    keys = ['constellation', 'station', 'measurement', 'beg_date', 'end_date']
    method_decorators = [check_api_key_and_req_type]

    def __init__(self):
        QueryData.__init__(self, 'QueryData')

    def get(self):
        if len(self.table) < 1:
            return {'time':[], 'value':[]}
        return {
            'time' : [t.strftime('%Y-%m-%d %H:%M:%S') for t in self.table['measure_ts']],
            'value' : self.table['obs_value'].values.tolist()
        }

class QueryDataByTime(QueryData):
    keys = ['constellation', 'station', 'measurement', 'beg_date', 'end_date']
    method_decorators = [check_api_key_and_req_type]
    def __init__(self):
        QueryData.__init__(self, 'QueryData')

    def get(self):
        template = j2.get_template('query_data_by_time.xml.j2')
        rows = []
        for index, row in self.table.iterrows():
            rows.append([
                row['measure_ts'].strftime('%Y-%m-%d %H:%M:%s'),
                row['obs_value'],
                row['units']
            ])
        payload = template.render(rows=rows)
        return payload

class ListQACodes(BaseResource):
    keys = []
    method_decorators = [check_api_key_and_req_type]


# TODO: could dry this up by making a helper function for the API
# instead of repeating every time
routing_dict = {
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
         'xmlrpc_cdrh.QueryDataRaw' : QueryDataRaw,
         'jsonrpc_cdrh.GetMetaDataLocation' : GetMetaDataLocation,
         'jsonrpc_cdrh.QueryDataSimple' : QueryDataSimple
        }


class BaseApi(Resource):
    """Base API which responds to XMLRPC and JSONRPC methods.  This delegates
       to the REST API methods, but adds fields/functionality as needed to
       emulate RPC."""
    def __init__(self):
        Resource.__init__(self)
        self.representations = {
            'text/xml' : output_xml,
            'application/json' : output_json
        }

    def get(self):

        return OrderedDict([('id', 1),
                            ('error', 'Please use POST for the legacy API endpoint'),
                            ('result', None)])

    def parse_args(self):
        if 'xml' in request.content_type:
            return self.parse_xml()
        return self.parse_json()

    def parse_json(self):
        # TODO: handle both jsonrpc and xmlrpc requests
        json_req = request.get_json(force=True)
        # grab the api method
        self.api_endpoint = routing_dict[json_req.pop('method')]
        if 'params' in json_req:
            params = json_req['params']
            # consider eliminating side effects, makes this difficult
            # to understand
            if self.api_endpoint.keys:
                json_req.update(dict(zip(self.api_endpoint.keys, json_req['params'])))

        return json_req

    def parse_xml(self):
        payload = xmlrpc_client.loads(request.data)
        # load xmlrpc method
        self.api_endpoint = routing_dict[payload[1]]
        return dict(zip(self.api_endpoint.keys, payload[0]))

    def dispatch_request(self, *args, **kwargs):

        # Taken from flask
        #noinspection PyUnresolvedReferences
        meth = getattr(self, request.method.lower(), None)
        if meth is None and request.method == 'HEAD':
            meth = getattr(self, 'get', None)
        assert meth is not None, 'Unimplemented method %r' % request.method

        for decorator in self.method_decorators:
            meth = decorator(meth)

        resp = meth(*args, **kwargs)

        if isinstance(resp, ResponseBase):  # There may be a better way to test
            return resp

        representations = self.representations or {}

        #noinspection PyUnresolvedReferences
        mediatype = request.accept_mimetypes.best_match(representations, default=None)
        if mediatype in representations:
            data, code, headers = unpack(resp)
            resp = representations[mediatype](data, code, headers)
            resp.headers['Content-Type'] = mediatype
            return resp
        elif request.content_type in representations:
            mediatype = request.content_type
            data, code, headers = unpack(resp)
            resp = representations[mediatype](data, code, headers)
            resp.headers['Content-Type'] = mediatype
            return resp

        return resp

    def post(self):
        request.args = self.parse_args()

        # call api endpoint with current request context
        # and switch request method to get
        try:
            resource = self.api_endpoint()
            get_method = resource.get
            for wrapper in getattr(resource, 'method_decorators', []):
                get_method = wrapper(get_method)
            res = get_method()
        except UnauthorizedError as e:
            return {'error':e.message}, 401
        except Exception as e:
            if app.config['DEBUG'] or app.config['TESTING']:
                raise
            return {'error':e.message}, 400

        if request_wants_xml() or request.content_type == 'text/xml':
            return res
        return res


api.add_resource(BaseApi, '/')
