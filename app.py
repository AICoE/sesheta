#!/usr/bin/env python

import os
import tornado.ioloop
import tornado.web
from tornado.escape import json_decode, json_encode
from prometheus_client import start_http_server, Summary

WEBHOOK_GITHUB_TIME = Summary('webhook_github_processing_seconds', 'Time spent processing Github webhooks request')


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        build_status = 'check'

        self.render(
            "index.html", title="Thoth - ManageIQ Dependency Bot", build_status=build_status)


class GithubHandler(tornado.web.RequestHandler):
    @WEBHOOK_GITHUB_TIME.time()
    def post(self):
        print(json_decode(self.request.body))
        response = {'result': 'ok'}
        self.write(response)


class TravisCIHandler(tornado.web.RequestHandler):
    def post(self):
        print(json_decode(self.request.body))
        response = {'result': 'ok'}
        self.write(response)


def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/webhooks/github", GithubHandler),
        (r"/webhooks/travis-ci", TravisCIHandler)
    ], debug=True, template_path='templates')


if __name__ == "__main__":
    app = make_app()
    app.listen(8080)
    tornado.ioloop.IOLoop.current().start()
