#!/usr/bin/env python
#-*- coding: utf-8 -*-
'''
cbibs_api
~~~~~~~~~

Application and project global declarations

Copyright 2015 RPS ASA
See LICENSE.txt
'''
from flask import Flask
from flask_environments import Environments
from flask.ext.sqlalchemy import SQLAlchemy
from flask_restful import Api
from cbibs_api.reverse_proxy import ReverseProxied
import os

app = Flask(__name__)
app.wsgi_app = ReverseProxied(app.wsgi_app)

env = Environments(app)

env.from_yaml('config.yml')
if os.path.exists('config.local.yml'):
    env.from_yaml('config.local.yml')

if app.config['LOGGING'] == True:
    import logging
    logger = logging.getLogger('pyprojects.app')
    logger.setLevel(logging.DEBUG)

    log_directory = app.config['LOG_FILE_PATH']
    log_filename = os.path.join(log_directory,app.config['LOG_FILE'])
    if not os.path.exists(os.path.dirname(log_filename)):
        os.makedirs(os.path.dirname(log_filename))
    file_handler = logging.FileHandler(log_filename, mode='a+')

    stream_handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(process)d - %(name)s - %(module)s:%(lineno)d - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    stream_handler.setFormatter(formatter)
    app.logger.addHandler(file_handler)
    #app.logger.addHandler(stream_handler)
    app.logger.setLevel(logging.DEBUG)
    app.logger.info('Application Process Started')

api = Api(app)
db = SQLAlchemy(app)
