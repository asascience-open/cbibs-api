from cbibs_api import app, db
from flask import jsonify, request
from functools import wraps
from cbibs_api.queries import SQL
from collections import OrderedDict
from defusedxml.xmlrpc import xmlrpc_client

def jsonify_status(json_dict, response_code=200):
    """
    Helper function to return JSON response for Flask with an optionally
    specified status code
    :param json_dict: dict to be serialized to JSON
    :param response_code: HTTP response code to return.  Defaults to 200.
    """
    res = jsonify(json_dict)
    res.status_code = response_code
    return res

def check_api_key_and_req_type(fn):
    """
    Wrapper to check that API key is supplied and valid and that the HTTP
    request verb is currently supported.
    """
    # TODO: a handy feature would be to use some kind of authentication so the
    # API key does not need to be repeatedly used.  In the event that is added
    # it probably should go in the wrapper below
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if request.method == 'GET':
            current_key = request.args.get('api_key')
            if current_key == app.config['API_KEY']:
                return fn(*args, **kwargs)
            else:
                return jsonify_status({'error': 'Incorrect API key, or API key not supplied'}, 401)
        elif request.method == 'POST':
            try:
                if ('application/xml' in request.accept_mimetypes or
                     'text/xml' in request.accept_mimetypes):
                    payload = xmlrpc_client.loads(request.data)
                    current_key = payload[0][-1]
                else:
                    json_req = request.get_json(force=True, silent=True)
                    # if a non empty or valid JSON response, try to grab the key
                    if json_req:
                        # current key should always be specified last by in request
                        # parameters
                        # attempt to pop off the API key since we won't need it
                        # for verification more than once
                        current_key = json_req.get('params').pop()
                # if the get returns none and tries to index (TypeError),
                # or params is empty (IndexError) return None
            except TypeError, IndexError:
                current_key = None
            if current_key == app.config['API_KEY']:
                return fn(*args, **kwargs)
            else:
                return jsonify_status({'id': 1, 'error': 'Incorrect API key, or no API key specified',
                                'result': None}, 401)
        else:
            return jsonify_status({'id': 1, 'error': 'Invalid request method. Currently supported request methods: [GET, POST]',
                            'result': None}, 405)
    return wrapper
