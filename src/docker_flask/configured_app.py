#!/usr/bin/env python
"""
configured_app

Sample flask App that uses a config file referenced by
an environment variable.


"""
import os
import json
from flask import Flask
from flask.ext.restful import Api, Resource
from . import get_logger


LOGGER = get_logger()
CONFIG = os.environ.get('DOCKER_FLASK_APP_CONFIG')


def _load_config():
    LOGGER.info("configured_app._load_config called")
    if CONFIG is None:
        LOGGER.error("config variable is not set")
        return None
    if not os.path.exists(CONFIG):
        LOGGER.error("config file {} not found".format(CONFIG))
        return None

    with open(CONFIG, 'r') as handle:
        config = json.load(handle)
    return config


class ConfigAPI(Resource):
    """
    simple REST API that supports several verbs
    for accessing and modifying a config file for demo
    purposes

    """
    def __init__(self, *args, **kwargs):
        super(ConfigAPI, self).__init__(*args, **kwargs)
        self.config = _load_config()

    def get(self, element):
        """
        get a config element
        """
        LOGGER.info(u"get()")
        if self.config is None:
            return 500, {'error': "configuration could not be loaded"}

        config_value = self.config.get(element)
        return {"ok": True, "element": config_value, "verb": "GET"}

    def post(self, element):
        return {"ok": True, "verb": "post", "element": element}

    def delete(self, element):
        return {"ok": True, "verb": "delete", "element": element}


def build_app():
    """
    build a basic flask app containing the API
    """
    app = Flask(__name__)
    api = Api(app)
    api.add_resource(ConfigAPI, '/docker_flask/config_app/<element>')
    return app

APP = build_app()
