#!/usr/bin/env python
'''
tests/test_cbibs_api.py

Unit tests for the CBIBS API Methods
'''

from cbibs_api.api import app
from flask.ext.testing import TestCase
from dateutil.parser import parse as dateparse
from datetime import datetime

# safe since we're parsing trusted input
from lxml import etree

import json
import unittest
import numpy as np

JSON_HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json"
}
XML_HEADERS = {
    "Content-Type": "application/xml",
    "Accept": "application/xml"
}

class TestJsonApi(TestCase):
    def create_app(self):
        app.config['TESTING'] = True
        self.API_KEY = app.config['API_KEY']
        return app

    def make_json_payload(self, method_name, arglist=[], use_api_key=True):
        payload = json.dumps({"method": method_name,
                   "params": arglist + [self.API_KEY] if use_api_key else arglist,
                   "id": 1})
        r = self.client.post('/', data=payload, headers=JSON_HEADERS)
        return r

    def test_bad_input(self):
        """Make sure garbage/bad input returns proper responses, etc."""
        # test with no API specifed and no login
        no_api_key_response = self.client.get("/".format(self.API_KEY),
                                              headers=JSON_HEADERS)
        assert no_api_key_response.status_code == 401
        assert (no_api_key_response.json['error'] ==
                "Incorrect API key, or API key not supplied")

    def test_Test(self):
        """Tests the Test function"""
        # test legacy API endpoint first
        expected = 'Test successful'
        post_response = self.make_json_payload('Test')
        # check to make sure we have a 200 response
        assert post_response.status_code == 200
        assert post_response.json['result'] == expected
        # now test new GET enpoint
        get_response = self.client.get("/Test?api_key={}".format(self.API_KEY),
                                       headers=JSON_HEADERS)
        assert get_response.json == expected

    def test_ListConstellations(self):
        """Test that CBIBS is among the list of constellations"""
        get_response = self.client.get("/ListConstellations?api_key={}".format(self.API_KEY),
                                       headers=JSON_HEADERS)
        assert get_response.status_code == 200
        assert 'CBIBS' in get_response.json
        post_response = self.make_json_payload("ListConstellations")
        assert 'CBIBS' in post_response.json['result']

    def test_ListPlatforms(self):
        """Test the platforms, check if Jamestown is present"""
        req_str = "/ListPlatforms?api_key={}&constellation={}".format(self.API_KEY,
                                                                      'CBIBS',)
        # GET response to REST endpoint
        get_response = self.client.get(req_str, headers=JSON_HEADERS)
        assert get_response.status_code == 200
        assert 'J' in get_response.json['id']

        # POST response to legacy JSONRPC endpoint
        post_response = self.make_json_payload('ListPlatforms', ["CBIBS"])
        xml_str = """<methodCall>
                       <methodName>ListPlatforms</methodName>
                       <params>
                       <param><value><string>CBIBS</string></value></param>
                       <param><value><string>%(api_key)s</string></value></param>
                       </params>
                      </methodCall>""" % {"api_key":self.API_KEY}

        # POST response to legacy XMLRPC endpoint
        post_response = self.client.post('/', data=xml_str,
                                         headers=XML_HEADERS)
        root = etree.fromstring(post_response.data)
        # make sure 'J' is in 'id' array
        xpath_res = root.xpath(".//member[name/text()='id']/value/array/data"
                               "/value/string[text()='J']")
        assert len(xpath_res) == 1

    def test_QueryData(self):
        arg_arr = ['CBIBS', 'J', 'sea_water_salinity', '2014-08-01',
                    '2014-08-02']
        post_response = self.make_json_payload('QueryData', arg_arr)
        expected = {
            "error": None,
            "id": 1,
            "result": {
                "measurement": "sea_water_salinity",
                "units": "PSU",
                "values": {
                    "time": [
                        "2014-08-01 01:00:00",
                        "2014-08-01 02:00:00",
                        "2014-08-01 03:00:00",
                        "2014-08-01 04:00:00",
                        "2014-08-01 05:00:00",
                        "2014-08-01 06:00:00",
                        "2014-08-01 07:00:00",
                        "2014-08-01 08:00:00",
                        "2014-08-01 09:00:00",
                        "2014-08-01 10:00:00",
                        "2014-08-01 11:00:00",
                        "2014-08-01 12:00:00",
                        "2014-08-01 13:00:00",
                        "2014-08-01 14:00:00",
                        "2014-08-01 15:00:00",
                        "2014-08-01 16:00:00",
                        "2014-08-01 17:00:00",
                        "2014-08-01 18:00:00",
                        "2014-08-01 19:00:00",
                        "2014-08-01 20:00:00",
                        "2014-08-01 21:00:00",
                        "2014-08-01 22:00:00",
                        "2014-08-01 23:00:00"
                    ],
                    "value": [
                        2.91,
                        2.55,
                        2.35,
                        2.25,
                        2.39,
                        2.64,
                        3.15,
                        3.34,
                        3.38,
                        3.39,
                        2.69,
                        2.78,
                        3.07,
                        2.67,
                        2.26,
                        1.72,
                        1.92,
                        2.59,
                        3.3,
                        4.0,
                        4.13,
                        4.39,
                        3.4
                    ]
                }
            }
        }
        json_response = json.loads(post_response.data)
        assert json_response == expected

    def test_GetNumberMeasurements(self):
        arg_arr = ['CBIBS', 'J', 'sea_water_salinity', '2014-08-01',
                   '2014-08-02']
        post_response = self.make_json_payload('GetNumberMeasurements', arg_arr)
        expected = {
            "id": 1, "error": None, "result": 23
        }
        json_response = json.loads(post_response.data)
        assert expected == json_response


    def test_LastMeasurementTime(self):
        arg_arr = ['CBIBS', 'J', 'sea_water_salinity']
        post_response = self.make_json_payload('LastMeasurementTime', arg_arr)
        json_response = json.loads(post_response.data)
        assert json_response['id'] == 1
        assert json_response['error'] is None
        obs_date = dateparse(json_response['result']) # Make sure we can parse a proper datek
        assert obs_date > datetime(2014,8,1)

    def test_RetrieveCurrentReadings(self):
        arg_arr = ['CBIBS', 'J']
        post_response = self.make_json_payload('RetrieveCurrentReadings', arg_arr)
        json_response = json.loads(post_response.data)
        # Assert no duplicates
        assert len(json_response['result']['measurement']) == len(set(json_response['result']['measurement']))
        assert len(json_response['result']['measurement']) > 0
        assert len(json_response['result']['time']) > 0
        assert json_response['result']['station'] == 'J'

    def test_ListStationsWithParam(self):
        arg_arr = ['CBIBS', 'sea_water_salinity']
        post_response = self.make_json_payload('ListStationsWithParam',
                                               arg_arr)
        expected = {
            "id": 1, "error": None, "result": ["SN","PL","J","SR","S","N","AN","UP","GR","FL","RC"]
        }
        json_response = json.loads(post_response.data)
        assert set(expected['result']) == set(json_response['result'])

    def test_ListParameters(self):
        arg_arr = ['CBIBS', 'J']
        post_response = self.make_json_payload('ListParameters', arg_arr)
        json_response = json.loads(post_response.data)
        assert len(json_response['result']) > 0
        assert json_response['error'] is None

    def test_RetrieveCurrentSuperSet(self):
        arg_arr = ['WQJ']
        post_response = self.make_json_payload('RetrieveCurrentSuperSet', arg_arr)
        json_response = json.loads(post_response.data)
        assert len(json_response['result']['time']) > 0
        assert len(json_response['result']['measurement']) > 0
        assert len(json_response['result']['value']) > 0
        assert 'sea_water_temperature' in json_response['result']['measurement']

    def test_list_methods(self):
        post_response = self.make_json_payload('system.listMethods', [])
        json_response = json.loads(post_response.data)
        from cbibs_api.api import routing_dict
        assert set(routing_dict.keys()) == set(json_response['result'])

    def test_method_help(self):
        from cbibs_api.api import routing_dict
        for method in routing_dict:
            arg_arr = [method]
            post_response = self.make_json_payload('system.methodHelp', arg_arr)
            json_response = json.loads(post_response.data)
            assert json_response['result']

    def test_method_signature(self):
        from cbibs_api.api import routing_dict
        for method in routing_dict:
            arg_arr = [method]
            post_response = self.make_json_payload('system.methodSignature', arg_arr)
            json_response = json.loads(post_response.data)
            assert json_response['result']

    def test_get_capabilities(self):
        post_response = self.make_json_payload('system.getCapabilities', [])
        json_response = json.loads(post_response.data)
        assert len(json_response['result']) == 3
        assert 'xmlrpc' in json_response['result']
        assert 'json-rpc' in json_response['result']

    def test_get_station_status(self):
        arg_arr = ['CBIBS', 'J']
        post_response = self.make_json_payload('GetStationStatus', arg_arr)
        json_response = json.loads(post_response.data)
        assert json_response['result'] == 0

    def test_QueryDataRaw(self):
        arg_arr = ['CBIBS', 'J', 'sea_water_salinity', '2014-08-01',
                    '2014-08-02']
        post_response = self.make_json_payload('QueryDataRaw', arg_arr)
        expected = {
            "error": None,
            "id": 1,
            "result": {
                "measurement": "sea_water_salinity",
                "units": "PSU",
                "values": {
                    "time": [
                        "2014-08-01 01:00:00",
                        "2014-08-01 02:00:00",
                        "2014-08-01 03:00:00",
                        "2014-08-01 04:00:00",
                        "2014-08-01 05:00:00",
                        "2014-08-01 06:00:00",
                        "2014-08-01 07:00:00",
                        "2014-08-01 08:00:00",
                        "2014-08-01 09:00:00",
                        "2014-08-01 10:00:00",
                        "2014-08-01 11:00:00",
                        "2014-08-01 12:00:00",
                        "2014-08-01 13:00:00",
                        "2014-08-01 14:00:00",
                        "2014-08-01 15:00:00",
                        "2014-08-01 16:00:00",
                        "2014-08-01 17:00:00",
                        "2014-08-01 18:00:00",
                        "2014-08-01 19:00:00",
                        "2014-08-01 20:00:00",
                        "2014-08-01 21:00:00",
                        "2014-08-01 22:00:00",
                        "2014-08-01 23:00:00"
                    ],
                    "value": [
                        2.91,
                        2.55,
                        2.35,
                        2.25,
                        2.39,
                        2.64,
                        3.15,
                        3.34,
                        3.38,
                        3.39,
                        2.69,
                        2.78,
                        3.07,
                        2.67,
                        2.26,
                        1.72,
                        1.92,
                        2.59,
                        3.3,
                        4.0,
                        4.13,
                        4.39,
                        3.4
                    ]
                }
            }
        }
        json_response = json.loads(post_response.data)
        assert json_response == expected

    def test_get_metadata_location(self):
        arg_arr = ['CBIBS', 'J']
        post_response = self.make_json_payload('jsonrpc_cdrh.GetMetaDataLocation', arg_arr)
        json_response = json.loads(post_response.data)
        assert not isinstance(json_response['result']['latitude'], list)
        lat = json_response['result']['latitude']
        lon = json_response['result']['longitude']
        np.testing.assert_allclose([lat, lon], np.array([37.204168, -76.777355]))

if __name__ == '__main__':
    unittest.main()
