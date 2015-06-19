import unittest
from cbibs_api.api import app
from flask.ext.testing import TestCase
import json


class TestJsonApi(TestCase):
    def create_app(self):
        app.config['TESTING'] = True
        self.API_KEY = app.config['API_KEY']
        return app

    def make_json_payload(self, method_name, arglist=[], use_api_key=True):
        payload = json.dumps({"method": method_name,
                   "params": arglist + [self.API_KEY] if use_api_key else arglist,
                   "id": 1})
        headers = {"Content-Type": "application/json",
                   'Accept': 'application/json'}
        r = self.client.post('/', data=payload, headers=headers)
        return r

    def test_bad_input(self):
        """Make sure garbage/bad input returns proper responses, etc."""
        # test with no API specifed and no login
        no_api_key_response = self.client.get("/".format(self.API_KEY))
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
        get_response = self.client.get("/Test?api_key={}".format(self.API_KEY))
        assert get_response.json['result'] == expected

    def test_ListConstellations(self):
         """Test that CBIBS is among the list of constellations"""
         get_response = self.client.get("/ListConstellations?api_key={}".format(self.API_KEY))
         assert get_response.status_code == 200
         assert 'CBIBS' in get_response.json['result']
         post_response = self.make_json_payload("ListConstellations")
         assert 'CBIBS' in post_response.json['result']

    def test_ListPlatforms(self):
         """Test the platforms, check if Jamestown is present"""
         req_str = "/ListPlatforms?api_key={}&constellation={}".format(self.API_KEY,
                                                                       'CBIBS')
         get_response = self.client.get(req_str)
         assert get_response.status_code == 200
         assert 'J' in get_response.json['result']['id']

if __name__ == '__main__':
    unittest.main()
