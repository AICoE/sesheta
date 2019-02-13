#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# thoth-core
# Copyright (C) 2018 Christoph Görn
#
# This program is free software: you can redistribute it and / or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

"""A scrum helper bot."""


import os
import logging

import requests

from httplib2 import Http
from apiclient.discovery import build, build_from_document
from httplib2 import Http
from oauth2client.service_account import ServiceAccountCredentials

from thoth.common import init_logging


class InvalidPayload(Exception):
    """This might be raised via Google Hangout Chat."""

    pass


class HTTPError(Exception):
    """This might be raised via Google Hangout Chat."""

    pass


__version__ = "0.4.0"


DEBUG = bool(os.getenv("DEBUG", True))

SPACE = os.getenv("SESHETA_SCRUM_SPACE", None)
SESHETA_SCRUM_MESSAGE = os.getenv("SESHETA_SCRUM_MESSAGE", None)
SESHETA_SCRUM_URL = os.getenv("SESHETA_SCRUM_URL", None)

init_logging()
_LOGGER = logging.getLogger("thoth.bots.sesehta.scrum_standup")

if DEBUG:
    _LOGGER.setLevel(level=logging.DEBUG)
else:
    _LOGGER.setLevel(level=logging.INFO)


if __name__ == "__main__":
    _LOGGER.info(f"Thoth Bot: Scrum Standup Helper v{__version__}")
    logging.getLogger("googleapiclient.discovery_cache").setLevel(logging.ERROR)

    if SESHETA_SCRUM_MESSAGE is None:
        _LOGGER.error("No bot message supplied!")
        exit(-2)

    if SESHETA_SCRUM_URL is None:
        _LOGGER.error("No url supplied!")
        exit(-2)

    response = dict()
    cards = list()
    widgets = list()
    header = None

    widgets.append({"textParagraph": {"text": SESHETA_SCRUM_MESSAGE}})
    widgets.append(
        {"buttons": [{"textButton": {"text": "open bluejeans", "onClick": {"openLink": {"url": SESHETA_SCRUM_URL}}}}]}
    )

    cards.append({"sections": [{"widgets": widgets}]})

    response["cards"] = cards
    response["name"] = f"scrum_standup"

    scopes = ["https://www.googleapis.com/auth/chat.bot"]
    credentials = ServiceAccountCredentials.from_json_keyfile_name("etc/credentials.json", scopes)
    http_auth = credentials.authorize(Http())

    chat = build("chat", "v1", http=http_auth)
    response = chat.spaces().messages().create(parent=SPACE, body=response)

    if response is not None:
        response.execute()
