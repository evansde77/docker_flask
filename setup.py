#!/usr/bin/env python

from setuptools import setup

setup(name='docker_flask',
      version='0.0.0',
      description='Example nginx/uwsgi/flask applications running in docker containers',
      author='Dave Evans',
      author_email='evansde77.github@gmail.com',
      url='https://github.com/evansde77/docker_flask',
      packages=['docker_flask'],
      package_dir={'docker_flask': 'src/docker_flask'}
)
