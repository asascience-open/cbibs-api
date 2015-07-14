from cbibs_api import app, db
from flask import jsonify, request, current_app, make_response
from functools import wraps
from cbibs_api.queries import SQL
from collections import OrderedDict
from defusedxml.xmlrpc import xmlrpc_client
import json

class UnauthorizedError(Exception):
    pass

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
            raise UnauthorizedError('Incorrect API key, or API key not supplied')
        elif request.method == 'POST':
            try:
                if request.content_type == 'text/xml':
                    payload = xmlrpc_client.loads(request.data)
                    current_key = payload[0][-1]
                else:
                    json_req = request.get_json(force=True, silent=True)
                    # if a non empty or valid JSON response, try to grab the key
                    if not json_req:
                        raise UnauthorizedError('Incorrect API key, or API key not supplied') 
                    current_key = json_req.get('params').pop()
                # if the get returns none and tries to index (TypeError),
                # or params is empty (IndexError) return None
            except TypeError, IndexError:
                current_key = None
            if current_key == app.config['API_KEY']:
                return fn(*args, **kwargs)
        raise UnauthorizedError('Incorrect API key, or no API key specified')
    return wrapper

def request_wants_json():
    best = request.accept_mimetypes.best_match(['application/json'])
    return best == 'application/json' and request.accept_mimetypes[best] > request.accept_mimetypes['text/html']

def request_wants_xml():
    current_app.logger.info(request.accept_mimetypes)
    best = request.accept_mimetypes.best_match(['text/xml','application/xml'])
    return best in ('text/xml', 'application/xml') and request.accept_mimetypes[best] > request.accept_mimetypes['text/html']

def output_json(data, code, headers=None):
    res = {'id' : 1, 'result' : data, 'error': None}
    response = make_response(json.dumps(res), code)
    response.headers.extend(headers or {})
    return response

def output_xml(data, code, headers=None):
    if hasattr(data, '__dict__'):
        xml_str = xmlrpc_client.dumps((dict(data),), methodresponse=True)
    else:
        xml_str = xmlrpc_client.dumps((data,), methodresponse=True)
    response = make_response(xml_str, code)
    response.headers.extend(headers or {})
    return response

