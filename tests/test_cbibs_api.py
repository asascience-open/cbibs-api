import unittest
from cbibs_api.api import app
from flask.ext.testing import TestCase
import json
# safe since we're parsing trusted input
from lxml import etree

JSON_HEADERS = headers = {"Content-Type": "application/json",
                          'Accept': 'application/json'}
XML_HEADERS = headers = {"Content-Type": "application/xml",
                         'Accept': 'application/xml'}

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
                        <param><value><string>0b0e81fe763a79660716bcee98a9ccbea653c8bd</string></value></param>
                        </params>
                       </methodCall>"""

         # POST response to legacy XMLRPC endpoint
         post_response = self.client.post('/', data=xml_str,
                                          headers=XML_HEADERS)
         root = etree.fromstring(post_response.data)
         # make sure 'J' is in 'id' array
         xpath_res = root.xpath(".//member[name/text()='id']/value/array/data"
                                "/value/string[text()='J']")
         assert len(xpath_res) == 1

    def test_QueryData(self):
        arg_arr = ['CBIBS', 'J', 'sea_water_salinity', '2009-01-01',
                    '2010-01-01']
        post_response = self.make_json_payload('QueryData', arg_arr)

    def test_GetNumberMeasurements(self):
         arg_arr = ['CBIBS', 'J', 'sea_water_salinity', '2009-01-01',
                    '2010-01-01']
         post_response = self.make_json_payload('GetNumberMeasurements',
                                                arg_arr)

    def test_LastMeasurementTime(self):
        arg_arr = ['CBIBS', 'J', 'sea_water_salinity']
        post_response = self.make_json_payload('LastMeasurementTime', arg_arr)

    def test_RetrieveCurrentReadings(self):
         arg_arr = ['CBIBS', 'J']
         post_response = self.make_json_payload('RetrieveCurrentReadings',
                                                arg_arr)
         assert ('sea_water_salinity' in
                 post_response.json['result']['measurement'])

if __name__ == '__main__':
    unittest.main()
