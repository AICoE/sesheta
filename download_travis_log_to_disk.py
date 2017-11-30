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
import sys
import json
import logging

from travispy import TravisPy
from travis_helper import TravisLogProcessingState

from configuration import *

DEBUG_LOG_LEVEL = bool(os.getenv('DEBUG', False))

if DEBUG_LOG_LEVEL:
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s,%(levelname)s,%(filename)s:%(lineno)d,%(message)s')
else:
    logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)  # pylint: disable=invalid-name


if __name__ == '__main__':
    logging.info("This is {} v{}".format(sys.argv[0], __version__))

    if not GITHUB_ACCESS_TOKEN:
        logging.error("No GITHUB_ACCESS_TOKEN")
        exit(-1)

    TRAVIS = TravisPy.github_auth(GITHUB_ACCESS_TOKEN)
    logging.debug("At Travis-CI I am " + TRAVIS.user().login)

    state = TravisLogProcessingState()
    state.restore('travis-datahub-memory.json')

    logging.debug("processed log_ids: %s",
                  json.dumps(list(state.processed_logs)))

    travis = TravisPy.github_auth(GITHUB_ACCESS_TOKEN)
    r = travis.repo(TRAVIS_REPO_SLUG)

    # TODO refactor this and store_travisci_logs_to_datahub()
    logging.info("Start processing Travis-CI job logs...")
    try:
        for b in travis.builds(repository_id=r.id):
            logging.debug("Build {}: {}: {}".format(
                b.id, b.commit.branch, b.job_ids))

            for job_id in b.job_ids:
                job = travis.job(job_id)

                if not job.log_id in state.processed_logs:
                    with open(".cache/{}.json".format(job.log_id), 'w') as outfile:
                        json.dump(job.log.body, outfile)

                    state.add(job.log_id)

    except KeyboardInterrupt:
        logging.debug("interrupt received, stopping…")
    finally:
        state.persist('travis-datahub-memory.json')
