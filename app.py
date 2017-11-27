#!/usr/bin/env python
# -*- coding: utf-8 -*-
#   manageiq-bot
#   Copyright(C) 2017 Christoph Görn
#
#   This program is free software: you can redistribute it and / or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see < http: // www.gnu.org / licenses / >.

"""This is Thoth, a dependency updating bot for the ManageIQ community.
"""

__version__ = '0.3.0'

import os
import logging
import json
from json.decoder import JSONDecodeError
from urllib.parse import unquote

import tornado.ioloop
import tornado.web
import tornado.httputil

from tornado.escape import json_decode, json_encode
from prometheus_client import generate_latest, Summary, CONTENT_TYPE_LATEST
from github import Github
from github.GithubException import GithubException
from travispy import TravisPy

from configuration import *

DEBUG_LOG_LEVEL = bool(os.getenv('DEBUG', False))

WEBHOOK_GITHUB_TIME = Summary(
    'webhook_github_processing_seconds', 'Time spent processing Github webhooks request')
WEBHOOK_TRAVISCI_TIME = Summary(
    'webhook_travisci_processing_seconds', 'Time spent processing Travis-CI webhooks request')

if DEBUG_LOG_LEVEL:
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s,%(levelname)s,%(filename)s:%(lineno)d,%(message)s')
else:
    logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)  # pylint: disable=invalid-name


def create_pr_to_master(target_branch, change_subject):
    """create a github pr from target_branch to master"""
    git = Github(GITHUB_ACCESS_TOKEN)
    repo = git.get_repo('goern/manageiq')

    repo.create_pull('[Thoth] automated minor update of one dependency: ' + change_subject,
                     """This PR is generated as part of an automated update, created by [Thoth Dependency Bot](http://dependencies-manageiq-bot.e8ca.engint.openshiftapps.com/)""", 'master', target_branch)

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        build_status = 'check'

        self.render(
            "index.html", title="Thoth - ManageIQ Dependency Bot", build_status=build_status)

class PrometheusHandler(tornado.web.RequestHandler):
    def get(self):
        data = generate_latest()
        self.set_header('Content-type', CONTENT_TYPE_LATEST)
        self.set_header('Content-Length', str(len(data)))
        self.write(data)


class GithubHandler(tornado.web.RequestHandler):
    @WEBHOOK_GITHUB_TIME.time()
    def post(self):
        print(json.dumps(json_decode(self.request.body)))
        response = {'result': 'ok'}
        self.write(response)


class TravisCIHandler(tornado.web.RequestHandler):
    @WEBHOOK_TRAVISCI_TIME.time()
    def post(self):
        file_dic = {}
        parameters = {}
        hook = {}
        hook['state'] = 'gnaaak'
        response = {'result': 'ok'}

        if 'application/x-www-form-urlencoded' in self.request.headers["Content-Type"]:
            tornado.httputil.parse_body_arguments(
                'application/x-www-form-urlencoded', self.request.body, parameters, file_dic)

        logging.debug(unquote(str(self.request.body, 'utf-8')))
        try:
            hook = json.loads(
                unquote(str(self.request.body, 'utf-8')).split('=', 1)[1])
        except JSONDecodeError as jex:
            logging.error(jex)
            return

        # TODO handle exceptions
        logging.debug("Travis-CI webhook received: %s" % json.dumps(hook))

        # if the CI job was successful and it is not related to the master branch
        if 'passed' in hook['state']:
            from_branch = hook['branch']
            if from_branch != 'master':
                logging.info("sending PR from %s to master" % from_branch)

                # send a PR!
                try:
                    _b = from_branch.split('/', 1)[1]
                    updated_dependency = _b.split('-', 1)[1]

                    create_pr_to_master(from_branch, updated_dependency)
                except GithubException as ghe:
                    logging.error(ghe)
                    self.set_status(422)
                    response = {'result': 'fail'}

        self.finish(response)


async def travis_start_build(build_id):
    t = TravisPy.github_auth(THOTH_DEPENDENCY_BOT_TRAVISCI)
    repo = t.repo(TRAVISCI_REPO_SLUG)

    for build in repo.builds:
        await build.restart()


class ApiHandler(tornado.web.RequestHandler):
     async def post(self):
        build_id = json_decode(self.request.body)

        await travis_start_build(build_id['build_id'])
        response = {'result': 'ok'}
        self.write(response)


def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/api", ApiHandler),
        (r"/_metrics", PrometheusHandler),
        (r"/webhooks/github", GithubHandler),
        (r"/webhooks/travis-ci", TravisCIHandler),
        (r"/webhooks/travis-ci/*", TravisCIHandler)
    ], debug=True, template_path='templates')


if __name__ == "__main__":
    if not GITHUB_ACCESS_TOKEN:
        logging.error("GITHUB_ACCESS_TOKEN not provided, terminating")
        exit(-1)

    if not THOTH_DEPENDENCY_BOT_TRAVISCI:
        logging.error("THOTH_DEPENDENCY_BOT_TRAVISCI not provided, terminating")
        exit(-1)

    app = make_app()
    app.listen(8080)
    tornado.ioloop.IOLoop.current().start()
