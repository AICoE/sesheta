#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""This is thoth, a dependency updating bot...
"""

__version__ = '0.1.0'

import os
import json
import logging
import shutil
import fileinput
import re

import semver
from tornado import httpclient
from gemfileparser import GemfileParser

from git import Repo, Actor
from git.exc import GitCommandError
from github import Github

MASTER_REPO_URL = 'git@github.com:goern/manageiq.git'
GEMNASIUM_STATUS_URL = 'https://api.gemnasium.com/v1/projects/goern/manageiq/dependencies'
GITHUB_REPO_NAME = 'manageiq'
LOCAL_WORK_COPY = './manageiq-workdir'
SSH_CMD = 'ssh -i id_deployment_key'

try:
    from dotenv import load_dotenv, find_dotenv

    load_dotenv(find_dotenv())
except Exception as e:
    logging.warning(e)

DEBUG_LOG_LEVEL = bool(os.getenv('DEBUG', False))

if DEBUG_LOG_LEVEL:
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s,%(levelname)s,%(filename)s:%(lineno)d,%(message)s')
else:
    logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)  # pylint: disable=invalid-name


def _download_Gemfile():
    http_client = httpclient.HTTPClient()
    try:
        response = http_client.fetch(
            "https://raw.githubusercontent.com/goern/manageiq/master/Gemfile")

        with open('Gemfile-manageiq', 'w') as file:
            file.write(response.body.decode("utf-8"))
    except httpclient.HTTPError as e:
        # HTTPError is raised for non-200 responses; the response
        # can be found in e.response.
        print("Error: " + str(e))
    except Exception as e:
        # Other errors are possible, such as IOError.
        print("Error: " + str(e))
    http_client.close()


def major(semverlike):
    _semver = None
    try:
        _semver = semver.parse(semverlike)['major']
    except ValueError as ve:
        logging.error("%s: %s" % (ve, semverlike))
        _semver = semverlike.split('.')[0]

    return _semver


def minor(semverlike):
    _semver = None
    try:
        _semver = semver.parse(semverlike)['minor']
    except ValueError as ve:
        logging.error("%s: %s" % (ve, semverlike))
        _semver = semverlike.split('.')[1]

    return _semver


def get_dependency_status(slug):
    http_client = httpclient.HTTPClient()

    try:
        req = httpclient.HTTPRequest(url=GEMNASIUM_STATUS_URL,
                                     auth_username='X',
                                     auth_password=os.getenv('GEMNASIUM_API_KEY'))
        response = http_client.fetch(req)

        with open('gemnasium-manageiq.json', 'w') as file:
            file.write(response.body.decode("utf-8"))
    except httpclient.HTTPError as e:
        # HTTPError is raised for non-200 responses; the response
        # can be found in e.response.
        logging.error(e)
    except Exception as e:
        # Other errors are possible, such as IOError.
        logging.error(e)
    http_client.close()

    # TODO handle exceptions
    data = json.load(open('gemnasium-manageiq.json'))

    return data


def bump_minor(package):
    logging.info("updating %s to %s" % (package['name'],
                                        package['distributions']['stable']))

    OWD = os.getcwd()
    os.chdir(LOCAL_WORK_COPY)

    parser = GemfileParser('Gemfile', 'manageiq')
    deps = parser.parse()

    for key in deps:
        if deps[key]:
            for dependency in deps[key]:
                if dependency.name == package['name']:
                    print(dependency.__dict__)

                    with fileinput.input(files=('Gemfile'), inplace=True, backup='.swp') as f:
                        for line in f:
                            if '"' + dependency.name + '"' in line:
                                line = line.replace(dependency.requirement,
                                                    package['distributions']['stable'], 1)

                            print(line)

    os.chdir(OWD)

if __name__ == '__main__':
    deps = get_dependency_status('goern/manageiq')

"""
    for dep in deps:
        if dep['color'] == 'yellow':  # and at first, just the yellow ones
            # if we have no major version shift, lets update the Gemfile
            if ((major(dep['locked']) == major(dep['package']['distributions']['stable'])) and
                    (minor(dep['locked']) < minor(dep['package']['distributions']['stable']))):
                target_branch = 'bots-life/updating-' + dep['package']['name']

                if not dep['first_level']:
                    logging.debug("skipping update, %s is not on first level" %
                                  dep['package']['name'])
                else:
                    bump_minor(dep['package'])

            else:
                logging.warning("skipping update, %s %s -> %s is a major update ENOTIMPLEMENTED"
                                % (dep['package']['name'],
                                   dep['locked'], dep['package']['distributions']['stable']))
"""
