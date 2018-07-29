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


"""Make sure that all our repos have the minimum labels resent."""


import os
import logging

import daiquiri
import sesheta

from sesheta.common import init_github_interface, ensure_label_present


DEBUG = bool(os.getenv('DEBUG', False))
SESHETA_GITHUB_ACCESS_TOKEN = os.getenv('SESHETA_GITHUB_ACCESS_TOKEN', None)

daiquiri.setup(level=logging.INFO)
logger = daiquiri.getLogger('label_checker')

if DEBUG:
    logger.setLevel(level=logging.DEBUG)
else:
    logger.setLevel(level=logging.INFO)

logger.info(f"Version v{sesheta.__version__}")


if __name__ == '__main__':
    if not SESHETA_GITHUB_ACCESS_TOKEN:
        logger.error(
            'Github Token not provided via environment variable SESHETA_GITHUB_ACCESS_TOKEN')
        exit(-1)

    github, org, GITHUB_ORGANIZATION, GITHUB_REPOSITORIES, DEFAULT_LABELS = init_github_interface(
        SESHETA_GITHUB_ACCESS_TOKEN)

    logger.info(
        f"Hi, I'm {github.get_user().name}, and I'm fully operational now!")
    logger.debug("... and I am running in DEBUG mode!")

    for repo in GITHUB_REPOSITORIES:
        logger.debug(
            f"checking if all required labels are present in repository {repo}")

        _repo = org.get_repo(repo)
        current_labels = _repo.get_labels()

        for label in DEFAULT_LABELS:
            logger.debug(f"checking for '{label['name']}'")
            ensure_label_present(
                _repo, label['name'], label['color'], current_labels)
