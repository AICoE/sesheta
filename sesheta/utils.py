#!/usr/bin/env python3
# Sesheta
# Copyright(C) 2018,2019 Christoph Görn
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


"""Utility methods used by handlers or processors."""


import os
import random

import json
import requests
import logging

import daiquiri

from httplib2 import Http
from apiclient.discovery import build, build_from_document
from httplib2 import Http
from oauth2client.service_account import ServiceAccountCredentials

daiquiri.setup(level=logging.DEBUG, outputs=("stdout", "stderr"))
_LOGGER = daiquiri.getLogger(__name__)

DEBUG = bool(os.getenv("DEBUG", True))
SESHETA_GITHUB_ACCESS_TOKEN = os.getenv("SESHETA_GITHUB_ACCESS_TOKEN", None)
THOTH_DEVOPS_SPACE = os.getenv("SESHETA_GOOGLE_CHAT_SPACE", None)

# pragma: no cover
GITHUB_GOOGLE_CHAT_MAPPING = {
    "goern": "Christoph Goern",
    "fridex": "Frido Pokorny",
    "ace2107": "Akash Parekh",
    "durandom": "Marcel Hild",
    "sub-mod": "Subin Modeel",
    "CermakM": "Marek Cermak",
    "vpavlin": "Vaclav Pavlin",
}

# pragma: no cover
POSITIVE_MATTERMOST_EMOJIS = [
    ":tada:",
    ":champagne:",
    ":party_parrot:",
    ":falloutboythumbsup:",
    ":thumbsup:",
    ":+1:",
    ":confetti_ball:",
]

# pragma: no cover
POSITIVE_GOOGLE_CHAT_EMOJIS = ["😊", "😌", "🙏", "👍", "😇", "☺️", "👌"]

# pragma: no cover
PR_SIZE_LABELS = ["size/XS", "size/S", "size/M", "size/L", "size/XL", "size/XXL"]


def calculate_pullrequest_size(pullrequest) -> str:
    """Calculate the number of additions/deletions of this PR."""
    try:
        lines_changes = pullrequest["additions"] + pullrequest["deletions"]

        if lines_changes > 1000:
            return "size/XXL"
        elif lines_changes >= 500 and lines_changes <= 999:
            return "size/XL"
        elif lines_changes >= 100 and lines_changes <= 499:
            return "size/L"
        elif lines_changes >= 30 and lines_changes <= 99:
            return "size/M"
        elif lines_changes >= 10 and lines_changes <= 29:
            return "size/S"
        elif lines_changes >= 0 and lines_changes <= 9:
            return "size/XS"
    except KeyError as exc:
        _LOGGER.exception(exc)
        return None


def random_positive_emoji() -> str:
    """Pick a random positive emoji."""
    return random.choice(POSITIVE_MATTERMOST_EMOJIS)


def random_positive_emoji2() -> str:
    """Pick a random positive emoji."""
    return random.choice(POSITIVE_GOOGLE_CHAT_EMOJIS)


def google_chat_username_by_github_user(github: str) -> str:
    """Map a GitHub User to a Google Chat User."""
    gchat = None

    try:
        gchat = GITHUB_GOOGLE_CHAT_MAPPING[github]
    except KeyError as exp:
        _LOGGER.exception(exp)

    if not gchat:
        return github

    return f"{gchat}"


def notify_channel(kind: str, message: str, url: str) -> None:
    """Send message to a Google Hangouts Chat space."""
    response = None
    scopes = ["https://www.googleapis.com/auth/chat.bot"]
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        "/opt/app-root/etc/gcloud/sesheta-chatbot-968e13a86991.json", scopes
    )
    http_auth = credentials.authorize(Http())

    chat = build("chat", "v1", http=http_auth)

    if kind.upper() in ["NEW_PULL_REQUEST", "NEW_PULL_REQUEST_REVIEW", "PULL_REQUEST_REVIEW", "REBASE_PULL_REQUEST"]:
        response = (
            chat.spaces().messages().create(parent=THOTH_DEVOPS_SPACE, body=create_pull_request_response(message, url))
        )
    elif kind.upper() == "NEW_ISSUE":
        response = chat.spaces().messages().create(parent=THOTH_DEVOPS_SPACE, body=create_issue_response(message, url))
    elif kind.upper() == "MERGED_PULL_REQUEST":
        response = chat.spaces().messages().create(parent=THOTH_DEVOPS_SPACE, body={"text": message})
    elif kind.upper() == "PROMETHEUS_ALERT":
        response = (
            chat.spaces().messages().create(parent=THOTH_DEVOPS_SPACE, body=create_prometheus_alert(message, url))
        )

    if response is not None:
        response.execute()


def add_labels(pull_request_url: str, labels: list) -> None:  # pragma: no cover
    """Add labels to a GitHub Pull Request."""
    _LOGGER.debug(f"adding labels '{labels}' to {pull_request_url}")

    # TODO migrate this to IGitt
    headers = {"Authorization": "token %s" % SESHETA_GITHUB_ACCESS_TOKEN}

    requests.post(f"{pull_request_url}/labels", headers=headers, data=json.dumps(labels))


def set_size(pull_request_url: str, sizeLabel: str) -> None:  # pragma: no cover
    """Set the size labels of a GitHub Pull Request."""
    _LOGGER.debug(f"adding size label '{sizeLabel}' to {pull_request_url}")

    add_labels(pull_request_url, [sizeLabel])


def create_pull_request_response(message: str, url: str) -> dict:
    """Create a Google Hangouts Chat Card."""
    response = dict()
    cards = list()
    widgets = list()
    header = None

    widgets.append({"textParagraph": {"text": message}})
    widgets.append({"buttons": [{"textButton": {"text": "open this PR", "onClick": {"openLink": {"url": url}}}}]})

    cards.append({"sections": [{"widgets": widgets}]})

    response["cards"] = cards
    id = url.split("/")[-1]
    response["name"] = f"pull_request-{id}"

    return response


def create_prometheus_alert(message: str, url: str) -> dict:
    """Create a Google Hangouts Chat Card for prometheus alert."""
    response = dict()
    cards = list()
    widgets = list()

    widgets.append({"textParagraph": {"text": message}})
    widgets.append({"buttons": [{"textButton": {"text": "open the Alert", "onClick": {"openLink": {"url": url}}}}]})
    cards.append({"sections": [{"widgets": widgets}]})
    response["cards"] = cards
    response["name"] = f"prometheus_alert"
    return response


def create_issue_response(message: str, url: str) -> dict:
    """Create a Google Hangouts Chat Card."""
    response = dict()
    cards = list()
    widgets = list()
    header = None

    widgets.append({"textParagraph": {"text": message}})
    widgets.append({"buttons": [{"textButton": {"text": "open this Issue", "onClick": {"openLink": {"url": url}}}}]})
    widgets.append(
        {
            "buttons": [
                {
                    "textButton": {
                        "text": "list all open Issues",
                        "onClick": {
                            "openLink": {
                                "url": "https://github.com/issues?q=is%3Aopen+is%3Apr+archived%3Afalse+user%3Athoth-station"  # Ignore PycodestyleBear (E501)
                            }
                        },
                    }
                }
            ]
        }
    )

    cards.append({"sections": [{"widgets": widgets}]})

    response["cards"] = cards
    id = url.split("/")[-1]
    response["name"] = f"issue-{id}"

    return response
