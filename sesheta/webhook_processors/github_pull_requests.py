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


"""This processes GitHub Pull Requests."""


import logging


import daiquiri


from sesheta.utils import notify_channel, mattermost_username_by_github_user


daiquiri.setup(level=logging.DEBUG, outputs=('stdout', 'stderr'))
_LOGGER = daiquiri.getLogger(__name__)


def process_github_open_pullrequest(pullrequest: dict) -> None:
    """Will handle with care."""
    _LOGGER.info(f"A Pull Request has been opened: {pullrequest['url']}")

    if pullrequest['title'].startswith('Automatic update of dependency'):
        return

    notify_channel(f"_{mattermost_username_by_github_user(pullrequest['user']['login'])}_ just "
                   f"opened a pull request: '[{pullrequest['title']}]({pullrequest['html_url']})'...")
