#!/usr/bin/env python
"""
spooler app

This app uses the uwsgi spooler to handle async tasks.
It includes two rest endpoints, a simple one and done
spooler and a more complex continously spooling API
to run jobs on the spooler repeatedly

This module uses the uwsgi API so it needs to be run
under uwsgi.
For example:

uwsgi --spooler=/tmp/spooler \
      --master \
      --http-socket 127.0.0.1:3031 \
      -w docker_flask.spooler_app:APP

"""
import os
import time
import uwsgi
from flask import Flask
from flask.ext.restful import Api, Resource, reqparse

from uwsgidecorators import spool, spoolforever
from . import get_logger


LOGGER = get_logger()


@spool
def consume_feed(arguments):
    LOGGER.info("consume_feed starting {}".format(arguments))
    time.sleep(2)
    LOGGER.info("consume_feed exiting...")


@spoolforever
def consume_feed_continuously(arguments):
    LOGGER.info("consume_feed_continuously starting {}".format(arguments))
    time.sleep(2)
    LOGGER.info("consume_feed_continuously exiting...")


def _parse_request():
    parser = reqparse.RequestParser()
    parser.add_argument(
        'feed',
        type=str,
        location='json',
        required=True
    )
    args = parser.parse_args()
    LOGGER.info('args={}'.format(args))
    return args


class SpoolerAPI(Resource):
    """
    simple REST API that spools tasks in response to POST requests
    and executes them once

    """
    def post(self):
        LOGGER.info(u"post()")
        args = _parse_request()
        resp = consume_feed(args)
        LOGGER.info(resp)
        return {"ok": True, 'spooled': resp}, 202


class ContinuousSpoolerAPI(Resource):
    """
    REST API that spools tasks forever in response to POST
    requests, provides a GET verb to list the jobs
    and also a DELETE verb to remove jobs
    """
    def get(self):
        """
        respond to GET with a list of the jobs
        on the spooler
        """
        jobs = uwsgi.spooler_jobs()
        LOGGER.info(uwsgi.opt)
        LOGGER.info(jobs)
        return {'ok': True, 'jobs': jobs}, 200

    def post(self):
        """
        respond to a POST by adding a new job to the spooler
        that will be continuously spooled

        POST data should be JSON that includes a 'feed' argument

        Response includes the uwsgi job id that was spawned
        """
        LOGGER.info(u"post()")
        args = _parse_request()
        resp = consume_feed_continuously(args)
        LOGGER.info(resp)
        return {"ok": True, 'spooled': resp}, 202

    def delete(self):
        """
        respond to a delete request by attempting to delete the job
        specified by the job parameter in the payload JSON data

        """
        parser = reqparse.RequestParser()
        parser.add_argument(
            'job',
            type=str,
            location='json',
            required=True
        )
        args = parser.parse_args()
        LOGGER.info('args={}'.format(args))
        job = args['job']
        if args['job'] not in uwsgi.spooler_jobs():
            return {'error': 'job doesnt exist', 'job': job}, 404
        taskname = os.path.basename(job)
        spool_file = os.path.join(uwsgi.opt['spooler'], taskname)
        if not os.path.exists(spool_file):
            msg = "spooler file not found for {}".format(job)
            LOGGER.info("{} - {}".format(msg, spool_file))
            return {'error': msg, 'job': job}, 404
        LOGGER.info("removing: {}".format(spool_file))
        os.remove(spool_file)
        return {"ok": True, 'removed': job}, 200


def build_app():
    """
    build a basic flask app containing the API
    """
    app = Flask(__name__)
    api = Api(app)
    api.add_resource(SpoolerAPI, '/docker_flask/spool_once')
    api.add_resource(ContinuousSpoolerAPI, '/docker_flask/spool_forever')
    return app


APP = build_app()
