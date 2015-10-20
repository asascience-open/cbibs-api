#!/usr/bin/env python
'''
tests/test_cbibs_api.py

Unit tests for the CBIBS API Methods
'''

from cbibs_api.api import app
from flask.ext.testing import TestCase
from dateutil.parser import parse as dateparse
from datetime import datetime
from jinja2 import Environment, FileSystemLoader

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
    "Content-type": "text/xml"
}

class TestJsonApi(TestCase):
    def setUp(self):
        self.j2 = Environment(loader=FileSystemLoader('tests/templates'))
        self.j2.globals = {'isinstance':isinstance, 'int':int}
        self.xml_template = self.j2.get_template('xmlrpc.xml.j2')

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

    def make_xml_payload(self, method_name, arglist=[], use_api_key=True):
        if use_api_key:
            arglist = arglist + [self.API_KEY]
        if 'system' not in method_name:
            method_name = 'xmlrpc_cdrh.' + method_name
        payload = self.xml_template.render(method_name=method_name, params=arglist)
        r = self.client.post('/', data=payload, headers=XML_HEADERS)
        return r

    def test_list_constellations(self):
        """Test that CBIBS is among the list of constellations"""
        post_response = self.make_xml_payload("ListConstellations")
        assert post_response.status_code == 200
        root = etree.fromstring(post_response.data)
        xpath_res = root.xpath(".//value/array/data/value/string[text()='CBIBS']")
        assert len(xpath_res) == 1

    def test_list_platforms(self):
        """Test the platforms, check if Jamestown is present"""

        # POST response to legacy JSONRPC endpoint
        post_response = self.make_json_payload('ListPlatforms', ["CBIBS"])
        assert post_response.status_code == 200
        json_response = json.loads(post_response.data)
        result_dict = dict(zip(json_response['result']['id'], json_response['result']['cn']))
        assert result_dict['J'] == 'Jamestown CBIBS Buoy'

        post_response = self.make_xml_payload('ListPlatforms', ['CBIBS'])
        root = etree.fromstring(post_response.data)
        # make sure 'J' is in 'id' array
        xpath_res = root.xpath(".//member[name/text()='id']/value/array/data"
                               "/value/string[text()='J']")
        assert len(xpath_res) == 1

    def test_query_data(self):
        arg_arr = ['CBIBS', 'J', 'sea_water_temperature', '2015-10-01',
                    '2015-10-02']
        post_response = self.make_json_payload('QueryData', arg_arr)
        expected = {
            "error": None,
            "id": 1,
            "result": {
                "measurement": "sea_water_temperature",
                "report_name":"Water Temperature",
                "units": "C",
                "values": {
                    "time": [
                        u'2015-10-01 01:00:00',
                        u'2015-10-01 02:00:00',
                        u'2015-10-01 03:00:00',
                        u'2015-10-01 04:00:00',
                        u'2015-10-01 05:00:00',
                        u'2015-10-01 06:00:00',
                        u'2015-10-01 07:00:00',
                        u'2015-10-01 08:00:00',
                        u'2015-10-01 09:00:00',
                        u'2015-10-01 10:00:00',
                        u'2015-10-01 11:00:00',
                        u'2015-10-01 12:00:00',
                        u'2015-10-01 13:00:00',
                        u'2015-10-01 14:00:00',
                        u'2015-10-01 15:00:00',
                        u'2015-10-01 16:00:00',
                        u'2015-10-01 17:00:00',
                        u'2015-10-01 18:00:00',
                        u'2015-10-01 19:00:00',
                        u'2015-10-01 20:00:00',
                        u'2015-10-01 21:00:00',
                        u'2015-10-01 22:00:00',
                        u'2015-10-01 23:00:00'
                    ],
                    "value": [
                        23.99,
                        23.9,
                        23.89,
                        23.87,
                        23.78,
                        23.88,
                        24.17,
                        23.95,
                        23.84,
                        23.68,
                        23.57,
                        23.69,
                        23.58,
                        23.5,
                        23.4,
                        23.38,
                        23.53,
                        23.64,
                        23.99,
                        23.57,
                        24.07,
                        23.91,
                        23.2
                    ]
                }
            }
        }
        json_response = json.loads(post_response.data)
        assert json_response == expected
        
        post_response = self.make_xml_payload('QueryData', arg_arr)
        assert post_response.status_code == 200
        root = etree.fromstring(post_response.data)
        xpath_res = root.xpath(".//member[name/text()='measurement']/value/string")
        assert xpath_res[0].text == 'sea_water_temperature'

        xpath_res = root.xpath(".//member[name/text()='units']/value/string")
        assert xpath_res[0].text == 'C'
        
        times = root.xpath(".//member[name/text()='values']/value/struct/member[name/text()='time']/value/array/data/value")
        values = root.xpath(".//member[name/text()='values']/value/struct/member[name/text()='value']/value/array/data/value")

        assert len(times) == len(values) and len(values) > 3

    def test_get_number_measurements(self):
        arg_arr = ['CBIBS', 'J', 'sea_water_salinity', '2014-08-01',
                   '2014-08-02']
        post_response = self.make_json_payload('GetNumberMeasurements', arg_arr)
        expected = {
            "id": 1, "error": None, "result": 23
        }
        json_response = json.loads(post_response.data)
        assert expected == json_response

        post_response = self.make_xml_payload('GetNumberMeasurements', arg_arr)
        assert post_response.status_code == 200
        root = etree.fromstring(post_response.data)
        xpath_res = root.xpath(".//param/value/int[text()='23']")
        assert len(xpath_res) == 1

    def test_last_measurement_time(self):
        arg_arr = ['CBIBS', 'J', 'sea_water_salinity']
        post_response = self.make_json_payload('LastMeasurementTime', arg_arr)
        json_response = json.loads(post_response.data)
        assert json_response['id'] == 1
        assert json_response['error'] is None
        obs_date = dateparse(json_response['result']) # Make sure we can parse a proper datek
        assert obs_date > datetime(2014,8,1)

        post_response = self.make_xml_payload('LastMeasurementTime', arg_arr)
        assert post_response.status_code == 200
        root = etree.fromstring(post_response.data)
        xpath_res = root.xpath(".//param/value/string")
        assert len(xpath_res) == 1
        obs_date = dateparse(xpath_res[0].text)
        assert obs_date > datetime(2014,8,1)

    def test_retrieve_current_readings(self):
        arg_arr = ['cbibs', 'J']
        post_response = self.make_json_payload('RetrieveCurrentReadings', arg_arr)
        json_response = json.loads(post_response.data)
        # Assert no duplicates
        assert len(json_response['result']['measurement']) == len(set(json_response['result']['measurement']))
        assert len(json_response['result']['measurement']) > 0
        assert len(json_response['result']['time']) > 0
        assert json_response['result']['station'] == 'J'

        post_response = self.make_xml_payload('RetrieveCurrentReadings', arg_arr)
        assert post_response.status_code == 200
        root = etree.fromstring(post_response.data)
        xpath_res = root.xpath(".//member[name/text()='station']/value/string")
        assert xpath_res[0].text == 'J'

        xpath_res = root.xpath(".//member[name/text()='measurement']/value/array/data/value/string[text()='sea_water_temperature']")
        assert len(xpath_res) == 1
        xpath_res = root.xpath(".//member[name/text()='value']/value/array/data/value/double")
        assert len(xpath_res) > 3

    def test_list_stations_with_param(self):
        arg_arr = ['CBIBS', 'sea_water_salinity']
        post_response = self.make_json_payload('ListStationsWithParam',
                                               arg_arr)
        expected = {
            #"id": 1, "error": None, "result": ["SN","PL","J","SR","S","N","AN","UP","GR","FL","RC"]
            "id": 1, "error": None, "result": ["SN","PL","J","SR","S","N","AN","UP","GR","FL"]
        }
        json_response = json.loads(post_response.data)
        assert set(expected['result']) == set(json_response['result'])
        
        post_response = self.make_xml_payload('ListStationsWithParam', arg_arr)
        assert post_response.status_code == 200
        root = etree.fromstring(post_response.data)
        xpath_res = root.xpath(".//value/array/data/value/string[text()='J']")
        assert len(xpath_res) == 1
        xpath_res = root.xpath(".//value/array/data/value")
        assert len(xpath_res) > 3

    def test_list_parameters(self):
        arg_arr = ['CBIBS', 'J']
        post_response = self.make_json_payload('ListParameters', arg_arr)
        json_response = json.loads(post_response.data)
        assert 'sea_water_salinity' in json_response['result']
        assert len(json_response['result']) > 0
        assert json_response['error'] is None
        
        post_response = self.make_xml_payload('ListParameters', arg_arr)
        assert post_response.status_code == 200
        root = etree.fromstring(post_response.data)
        xpath_res = root.xpath(".//value/array/data/value/string[text()='sea_water_salinity']")
        assert len(xpath_res) == 1
        xpath_res = root.xpath(".//value/array/data/value/string[text()='sea_water_temperature']")
        assert len(xpath_res) == 1

    def test_retrieve_current_super_set(self):
        arg_arr = ['WQJ']
        post_response = self.make_json_payload('RetrieveCurrentSuperSet', arg_arr)
        json_response = json.loads(post_response.data)
        assert len(json_response['result']['time']) > 0
        assert len(json_response['result']['measurement']) > 0
        assert len(json_response['result']['value']) > 0
        assert 'sea_water_temperature' in json_response['result']['measurement']
        
        post_response = self.make_xml_payload('RetrieveCurrentSuperSet', arg_arr)
        assert post_response.status_code == 200
        root = etree.fromstring(post_response.data)
        xpath_res = root.xpath(".//member[name/text()='measurement']/value/array/data/value/string[text()='sea_water_temperature']")
        assert len(xpath_res) == 1
        measurements = root.xpath(".//member[name/text()='measurement']/value/array/data")
        times = root.xpath(".//member[name/text()='time']/value/array/data")
        values = root.xpath(".//member[name/text()='value']/value/array/data")
        assert len(measurements) == len(times) and len(times) == len(values)

    def test_list_methods(self):
        post_response = self.make_json_payload('system.listMethods', [])
        json_response = json.loads(post_response.data)
        from cbibs_api.api import routing_dict
        assert set(routing_dict.keys()) == set(json_response['result'])

        post_response = self.make_xml_payload('system.listMethods', [])
        assert post_response.status_code == 200
        etree.fromstring(post_response.data)

    def test_method_help(self):
        from cbibs_api.api import routing_dict
        for method in routing_dict:
            arg_arr = [method]
            post_response = self.make_json_payload('system.methodHelp', arg_arr)
            json_response = json.loads(post_response.data)
            assert json_response['result']
            
            arg_arr = [method]
            post_response = self.make_xml_payload('system.methodHelp', arg_arr)
            assert post_response.status_code == 200
            root = etree.fromstring(post_response.data)

    def test_method_signature(self):
        from cbibs_api.api import routing_dict
        for method in routing_dict:
            arg_arr = [method]
            post_response = self.make_json_payload('system.methodSignature', arg_arr)
            json_response = json.loads(post_response.data)
            assert json_response['result']
            
            arg_arr = [method]
            post_response = self.make_xml_payload('system.methodSignature', arg_arr)
            assert post_response.status_code == 200
            root = etree.fromstring(post_response.data)

    def test_get_capabilities(self):
        post_response = self.make_json_payload('system.getCapabilities', [])
        json_response = json.loads(post_response.data)
        assert len(json_response['result']) == 3
        assert 'xmlrpc' in json_response['result']
        assert 'json-rpc' in json_response['result']

        post_response = self.make_xml_payload('system.getCapabilities', [])
        assert post_response.status_code == 200
        root = etree.fromstring(post_response.data)
        json_spec = root.xpath(".//member[name/text()='json-rpc']/value/struct/member[name/text()='specUrl']/value/string")
        assert json_spec[0].text == 'http://json-rpc.org/wiki/specification'


    def test_get_station_status(self):
        arg_arr = ['CBIBS', 'J']
        post_response = self.make_json_payload('GetStationStatus', arg_arr)
        json_response = json.loads(post_response.data)
        assert json_response['result'] == 0
        
        post_response = self.make_xml_payload('GetStationStatus', arg_arr)
        assert post_response.status_code == 200
        root = etree.fromstring(post_response.data)
        xpath_res = root.xpath(".//value/int")
        assert xpath_res[0].text == "0"

    def test_query_data_raw(self):
        arg_arr = ['CBIBS', 'J', 'sea_water_salinity', '2014-08-01',
                    '2014-08-02']
        post_response = self.make_json_payload('QueryDataRaw', arg_arr)
        expected = {
            "error": None,
            "id": 1,
            "result": {
                "measurement": "sea_water_salinity",
                "report_name": "Sea Water Salinity",
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
        
        post_response = self.make_xml_payload('QueryDataRaw', arg_arr)
        assert post_response.status_code == 200
        root = etree.fromstring(post_response.data)
        xpath_res = root.xpath(".//member[name/text()='measurement']/value/string")
        assert xpath_res[0].text == 'sea_water_salinity'

        xpath_res = root.xpath(".//member[name/text()='units']/value/string")
        assert xpath_res[0].text == 'PSU'
        
        times = root.xpath(".//member[name/text()='values']/value/struct/member[name/text()='time']/value/array/data/value")
        values = root.xpath(".//member[name/text()='values']/value/struct/member[name/text()='value']/value/array/data/value")

        assert len(times) == len(values) and len(values) > 3

    def test_get_metadata_location(self):
        arg_arr = ['CBIBS', 'J']
        post_response = self.make_json_payload('GetMetaDataLocation', arg_arr)
        json_response = json.loads(post_response.data)
        assert not isinstance(json_response['result']['latitude'], list)
        lat = json_response['result']['latitude']
        lon = json_response['result']['longitude']
        np.testing.assert_allclose([lat, lon], np.array([37.204168, -76.777355]), atol=0.001)
        
        post_response = self.make_xml_payload('GetMetaDataLocation', arg_arr)
        assert post_response.status_code == 200
        root = etree.fromstring(post_response.data)
        lat = root.xpath(".//member[name/text()='latitude']/value/double")
        lat = float(lat[0].text)
        lon = root.xpath(".//member[name/text()='longitude']/value/double")
        lon = float(lon[0].text)
        np.testing.assert_allclose([lat, lon], np.array([37.204168, -76.777355]), atol=0.001)

    def test_query_data_simple(self):
        arg_arr = ['CBIBS', 'J', 'sea_water_temperature', '2015-09-08', '2015-09-08T06:00']
        post_response = self.make_json_payload('QueryDataSimple', arg_arr)
        json_response = json.loads(post_response.data)
        expected = {
            "error": None,
            "id": 1,
            "result": {
                "time": [
                    "2015-09-08 01:00:00",
                    "2015-09-08 02:00:00",
                    "2015-09-08 03:00:00",
                    "2015-09-08 04:00:00",
                    "2015-09-08 05:00:00"
                ],
                "value": [
                    27.51,
                    27.55,
                    27.37,
                    27.5,
                    27.3
                ]
            }
        }
        assert json_response == expected
        post_response = self.make_xml_payload('QueryDataSimple', arg_arr)
        assert post_response.status_code == 200
        root = etree.fromstring(post_response.data)
        times = root.xpath(".//member[name/text()='time']/value/array/data/value/string")
        values = root.xpath(".//member[name/text()='value']/value/array/data/value/double")
        assert len(times) == len(values) and len(times) > 3

    def test_query_data_by_time(self):
        arg_arr = ['CBIBS', 'J', 'sea_water_temperature', '2015-09-08', '2015-09-08T06:00']
        post_response = self.make_json_payload('QueryDataByTime', arg_arr)
        json_response = json.loads(post_response.data)
        root = etree.fromstring(json_response['result'])
        
        post_response = self.make_xml_payload('QueryDataByTime', arg_arr)
        assert post_response.status_code == 200
        root = etree.fromstring(post_response.data)
        xpath_res = root.xpath(".//param/value/string")
        inner_doc = etree.fromstring(xpath_res[0].text)
        xpath_res = inner_doc.xpath(".//time")
        assert len(xpath_res) > 2

    def test_list_qa_codes(self):
        arg_arr = []
        post_response = self.make_json_payload('ListQACodes', arg_arr)
        json_response = json.loads(post_response.data)
        qa_dict = dict(zip(json_response['result']['qacode'], json_response['result']['description']))
        assert qa_dict[9] == 'MISSING'
        assert qa_dict[1] == 'GOOD Value'
        post_response = self.make_xml_payload('ListQACodes', arg_arr)
        assert post_response.status_code == 200
        root = etree.fromstring(post_response.data)
        xpath_res = root.xpath(".//struct/member[name/text()='qacode']/value/array/data/value")
        assert len(xpath_res) == 6

    def test_auth_vs_noauth(self):
        post_response = self.make_json_payload('system.listMethods', [], use_api_key=False)
        assert post_response.status_code == 200

        arg_arr = ['CBIBS', 'J', 'sea_water_temperature', '2015-05-01', '2015-05-01T06:00']
        post_response = self.make_json_payload('QueryDataSimple', arg_arr, use_api_key=False)
        assert post_response.status_code == 401

if __name__ == '__main__':
    unittest.main()
