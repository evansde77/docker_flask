#!/usr/bin/env python
"""
docker_flask

Sample apps for use demonstating flask apps on docker containers

"""
import sys
import logging

LOGGER = logging.getLogger('docker_flask')
HANDLER = None


def get_logger():
    """set up a basic logger"""
    global HANDLER
    if HANDLER is None:
        LOGGER.setLevel(logging.DEBUG)

        HANDLER = logging.StreamHandler(sys.stdout)
        HANDLER.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        HANDLER.setFormatter(formatter)
        LOGGER.addHandler(HANDLER)
    return LOGGER
