#!/usr/bin/env python3
# Sesehta
# Copyright(C) 2017,2018 Christoph Görn
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

"""This is the Flask webhook receiver..."""


import logging

from thoth.common import init_logging

from sesheta import create_application, __version__


init_logging()

_LOGGER = logging.getLogger('thoth.sesheta')


_LOGGER.info(f"Hi, I am Sesheta, I will handle your incoming GitHub webhooks, "
             f"and I'm running v{__version__}")

application = create_application()
