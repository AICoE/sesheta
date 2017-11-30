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

import pytest

from datahub_helper import upload_to_datahub

class TravisBuild():
    def __init__(self, id, job_ids):
        self.id = id
        self.job_ids = job_ids

class TravisJob():
    def __init__(self, id, log_id, log):
        self.id = id
        self.log_id = log_id
        self.log = log

class TravisLog():
    def __init__(self, id, body):
        self.id = id
        self.body = body


@pytest.fixture
def Log():
    return TravisLog(1, 'This space intentionally left blank.')

@pytest.fixture
def Job(Log):
    return TravisJob(1, 1, Log)


@pytest.fixture
def Build():
    return TravisBuild(1, [1])


def test_upload_to_datahub(Build, Job):
    """This test requires Red Hat intranet access"""

    r = upload_to_datahub(Build, Job)

    assert r == 201 # created!
