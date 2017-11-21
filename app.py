#!/usr/bin/env python

import os
import json
import logging

import tornado.ioloop
import tornado.web
import tornado.httputil

from tornado.escape import json_decode, json_encode
from prometheus_client import start_http_server, Summary
from github import Github

DEBUG_LOG_LEVEL = bool(os.getenv('DEBUG', False))
WEBHOOK_GITHUB_TIME = Summary(
    'webhook_github_processing_seconds', 'Time spent processing Github webhooks request')


if DEBUG_LOG_LEVEL:
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s,%(levelname)s,%(filename)s:%(lineno)d,%(message)s')
else:
    logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)  # pylint: disable=invalid-name


def create_pr_to_master(target_branch):
    """create a github pr from target_branch to master"""
    git = Github(os.environ.get('GITHUB_ACCESS_TOKEN'))
    repo = git.get_user().get_repo('manageiq')

    repo.create_pull('[Thoth] automated minor update of one dependency',
                     'This PR is generated as part of an automated update, created by Thoth Dependency Bot', 'master', target_branch)

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        build_status = 'check'

        self.render(
            "index.html", title="Thoth - ManageIQ Dependency Bot", build_status=build_status)


class GithubHandler(tornado.web.RequestHandler):
    @WEBHOOK_GITHUB_TIME.time()
    def post(self):
        print(json.dumps(json_decode(self.request.body)))
        response = {'result': 'ok'}
        self.write(response)


class TravisCIHandler(tornado.web.RequestHandler):
    def post(self):
        file_dic = {}
        parameters = {}
        hook = {}
        hook['state'] = 'gnaaak'

        if 'application/x-www-form-urlencoded' in self.request.headers["Content-Type"]:
            tornado.httputil.parse_body_arguments(
                'application/x-www-form-urlencoded', self.request.body, parameters, file_dic)

        logging.debug(parameters)

        for key, value in parameters.items():
            if key is 'payload':
                hook = value

        # TODO handle exceptions

        logging.debug("Travis-CI webhook received: %s" % hook)

        if ('success' in hook['state'] and hook['branches'][0]['name'] != 'master'):
            logging.info("sending PR from %s to master" % json.dumps(hook['branches'][0]['name']))

            create_pr_to_master(hook['branches'][0]['name'])

        response={'result': 'ok'}
        self.write(response)


def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/webhooks/github", GithubHandler),
        (r"/webhooks/travis-ci", TravisCIHandler),
        (r"/webhooks/travis-ci/*", TravisCIHandler)
    ], debug=True, template_path='templates')


if __name__ == "__main__":
    app = make_app()
    app.listen(8080)
    tornado.ioloop.IOLoop.current().start()
