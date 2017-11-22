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
from github.GithubException import GithubException

DEBUG_LOG_LEVEL = bool(os.getenv('DEBUG', False))
GITHUB_ACCESS_TOKEN = os.environ.get('GITHUB_ACCESS_TOKEN')
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
    git = Github(GITHUB_ACCESS_TOKEN)
    repo = git.get_user().get_repo('manageiq')

    repo.create_pull('[Thoth] automated minor update of one dependency',
                     """This PR is generated as part of an automated update, created by [Thoth Dependency Bot](http://dependencies-manageiq-bot.e8ca.engint.openshiftapps.com/)

                     PS: `Gemfile.lock` has been removed from this branch...""", 'master', target_branch)

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
        response = {'result': 'ok'}

        if 'application/x-www-form-urlencoded' in self.request.headers["Content-Type"]:
            tornado.httputil.parse_body_arguments(
                'application/x-www-form-urlencoded', self.request.body, parameters, file_dic)

        hook = json.loads(str(self.request.body, 'utf-8').split('=', 1)[1])

        # TODO handle exceptions

        logging.debug("Travis-CI webhook received: %s" % hook)

        # if the CI job was successful and it is not related to the master branch
        if 'success' in hook['state']:
            from_branch = hook['branches']['name']
            if from_branch != 'master':
                logging.info("sending PR from %s to master" % from_branch)

                # send a PR!
                try:
                    create_pr_to_master(from_branch)
                except GithubException as ghe:
                    logging.error(ghe)
                    self.set_status(422)
                    response = {'result': 'fail'}

        self.finish(response)


def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/webhooks/github", GithubHandler),
        (r"/webhooks/travis-ci", TravisCIHandler),
        (r"/webhooks/travis-ci/*", TravisCIHandler)
    ], debug=True, template_path='templates')


if __name__ == "__main__":
    if not GITHUB_ACCESS_TOKEN:
        logging.error("GITHUB_ACCESS_TOKEN not provided, terminating")
        exit(-1)

    app = make_app()
    app.listen(8080)
    tornado.ioloop.IOLoop.current().start()
