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

import requests

from configuration import DATAHUB_TRAVISCI_INDEX, DATAHUB_ENDPOINT, DATAHUB_R_CERT, DATAHUB_R_KEY, DATAHUB_W_CERT, DATAHUB_W_KEY

def upload_to_datahub(build, job):
    """upload_to_databub will upload the log body to datahub"""

    logging.debug("Uploading {}:{}:{} to DataHub index {}".format(build.id, job.id, job.log_id, DATAHUB_TRAVISCI_INDEX))

    datahub_entry = {}
    datahub_entry['build_id'] = build.id
    datahub_entry['job_id'] = job.id
    datahub_entry['log_id'] = job.log_id
    datahub_entry['raw_log'] = job.log.body

    # FIXME exception handling is missing
    r = requests.post(DATAHUB_ENDPOINT + DATAHUB_TRAVISCI_INDEX + 'log/' + str(job.log_id), 
                      data=json.dumps(datahub_entry), cert=(
                          DATAHUB_W_CERT, DATAHUB_W_KEY), verify=False)

    return r.status_code
