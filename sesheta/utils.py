#!/usr/bin/env python3
# Sesheta
# Copyright(C) 2018 Christoph Görn
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


import sys
import os
import random

import requests
import logging

import daiquiri


daiquiri.setup(level=logging.DEBUG, outputs=('stdout', 'stderr'))
_LOGGER = daiquiri.getLogger(__name__)


ENDPOINT_URL = os.getenv('SESHETA_MATTERMOST_ENDPOINT_URL', None)

GITHUB_MATTERMOST_MAPPING = {
    "goern": "goern",
    "fridex": "fridolin",
    "harshad16": "hnalla",
    "ace2107": "akash2107",
    "durandom": "hild",
    "sub-mod": "subin",
    "sushmithaaredhatdev": "sushmitha_nagarajan",
    "vpavlin": "vpavlin"
}

POSITIVE_MATTERMOST_EMOJIS = [
    ':tada:',
    ':champagne:',
    ':party_parrot:',
    ':falloutboythumbsup:',
    ':thumbsup:',
    ':+1:'
] 


def random_positive_emoji() -> str:
    return random.choice(POSITIVE_MATTERMOST_EMOJIS)

def mattermost_username_by_github_user(github: str) -> str:
    """Map a GitHub User to a Mattermost User."""
    mattermost = None

    try:
        mattermost = GITHUB_MATTERMOST_MAPPING[github]
    except KeyError as exp:
        _LOGGER.exception(exp)

    if not mattermost:
        return github

    return f'@{mattermost}'


def notify_channel(message: str) -> None:
    """Send message to Mattermost Channel."""
    if ENDPOINT_URL is None:
        _LOGGER.error('No Mattermost incoming webhook URL supplied!')
        exit(-2)

    payload = {'text': message,
               'icon_url': 'https://avatars1.githubusercontent.com/u/33906690'}

    r = requests.post(ENDPOINT_URL, json=payload)
    if r.status_code != 200:
        _LOGGER.error(f"cant POST to {ENDPOINT_URL}")


def add_labels(pull_request_url: str, labels: list) -> None:
    """Add labels to a GitHub Pull Request."""
    return
