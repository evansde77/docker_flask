#!/usr/bin/env python
"""
Trivial REST application for testing/demo purposes

"""
from flask import Flask
from flask.ext.restful import Api, Resource
from . import get_logger


LOGGER = get_logger()


class API(Resource):
    """
    simple REST API that supports several verbs

    """
    def get(self, argument):
        """

        """
        LOGGER.info(u"get({})".format(argument))
        return {"ok": True, "argument": argument, "verb": "GET"}

    def post(self, argument):
        LOGGER.info(u"post({})".format(argument))
        return {"ok": True, "argument": argument, "verb": "post"}

    def delete(self, argument):
        LOGGER.info(u"delete({})".format(argument))
        return {"ok": True, "argument": argument, "verb": "delete"}


def build_app():
    """
    build a basic flask app containing the API
    """
    app = Flask(__name__)
    api = Api(app)
    api.add_resource(API, '/docker_flask/<argument>')
    return app

APP = build_app()
