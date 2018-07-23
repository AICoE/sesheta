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


"""This processes GitHub Reviews."""

import sys
import logging

import daiquiri

from sesheta.utils import notify_channel, mattermost_username_by_github_user, add_labels


daiquiri.setup(__name__, outputs=(
    daiquiri.output.Stream(sys.stdout)))
_LOGGER = daiquiri.getLogger(__name__)
_LOGGER.setLevel(logging.DEBUG)


def process_github_pull_request_review(pullrequest: dict, review: dict) -> None:
    """Will handle with care."""
    if review['state'] == 'comment':
        notify_channel(
            f"_{mattermost_username_by_github_user(review['user']['login'])}_ submitted a review:comment"
            f" for Pull Request '[{pullrequest['title']}]({pullrequest['html_url']})'")
    elif review['state'] == 'approved':
        notify_channel(
            f":white_check_mark: _{mattermost_username_by_github_user(review['user']['login'])}_ approved"
            f" Pull Request '[{pullrequest['title']}]({pullrequest['html_url']})'")
        add_labels(pullrequest['url'], ['approved'])


def process_github_pull_request_review_requested(
        pullrequest: dict) -> None:
    """Will handle with care."""
    for requested_reviewer in pullrequest['requested_reviewers']:
        notify_channel(
            f":play_or_pause_button: a review by _{mattermost_username_by_github_user(requested_reviewer['login'])}_"
            f" has been requested for "
            f"Pull Request '[{pullrequest['title']}]({pullrequest['html_url']})'")


def process_github_pull_request_review_submitted(pullrequest: dict, review: dict) -> None:
    """Will handle with care."""
    if review['state'].startswith('approved'):
        _LOGGER.info("TODO set label 'approved' for {pullrequest['html_url']}")
