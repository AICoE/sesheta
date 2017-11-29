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

import logging
import json

from datahub_helper import upload_to_datahub


class TravisLogProcessingState():
    """TravisLogProcessingState will manage the state of Travis-CI Log Processing"""
    def __init__(self):
        self.processed_logs = set()

    def add(self, log_id):
        """add a Travis-CI log ID to the state"""
        self.processed_logs.add(log_id)

    def persist(self, file_name):
        """persist the state to a given file"""
        with open(file_name, 'w') as outfile:
            json.dump(list(self.processed_logs), outfile)

    def restore(self, file_name):
        """restore the state from a given file, if the file does not
        exists, state is initilized with an empty set of log ids"""
        try:
            self.processed_logs = set(json.load(open(file_name)))
        except FileNotFoundError as fnfe:
            logging.error(fnfe)


def store_travisci_logs_to_datahub(travis, repo_slug):
    """This function will download all logs of any build in the given
    repository and send them to DataHub"""

    # lets recall from out memories.. which log_id did we process?
    state = TravisLogProcessingState()
    state.restore('travis-datahub-memory.json')

    logging.debug("processed log_ids: %s",
                  json.dumps(list(state.processed_logs)))

    r = travis.repo(repo_slug)

    logging.info("Start processing Travis-CI job logs...")
    try:
        for b in travis.builds(repository_id=r.id):
            logging.debug("Build {}: {}: {}".format(
                b.id, b.commit.branch, b.job_ids))

            for job_id in b.job_ids:
                job = travis.job(job_id)

                if not job.log_id in state.processed_logs:
                    upload_to_datahub(b, job)
                    state.add(job.log_id)

    except KeyboardInterrupt:
        logging.debug("interrupt received, stopping…")
    finally:
        state.persist('travis-datahub-memory.json')
