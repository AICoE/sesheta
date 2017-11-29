#!/usr/bin/env python
# -*- coding: utf-8 -*-
#   sesheta
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
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""This is Thoth, a dependency updating bot for Open-Source Communities.
"""

__version__ = '0.3.0'

import os
import json
import logging

from travispy import TravisPy
from travis_helper import store_travisci_logs_to_datahub

from configuration import *

DEBUG_LOG_LEVEL = bool(os.getenv('DEBUG', False))

if DEBUG_LOG_LEVEL:
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s,%(levelname)s,%(filename)s:%(lineno)d,%(message)s')
else:
    logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)  # pylint: disable=invalid-name


if __name__ == '__main__':
    logging.info("This is {} v{}".format('upload_travis_log_to_datahub', __version__))

    if not GITHUB_ACCESS_TOKEN:
        logging.error("No GITHUB_ACCESS_TOKEN")
        exit(-1)

    TRAVIS = TravisPy.github_auth(GITHUB_ACCESS_TOKEN)
    logging.debug("At Travis-CI I am " + TRAVIS.user().login)

    store_travisci_logs_to_datahub(TRAVIS, TRAVIS_REPO_SLUG)
