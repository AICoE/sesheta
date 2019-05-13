#!/usr/bin/env python3
# Sesheta
# Copyright(C) 2018,2019 Christoph Görn
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


"""This will answer OpenShift Readyness and Liveness probes."""


from flask import Blueprint, jsonify


probes = Blueprint("probes", __name__, url_prefix="/_healthz")


@probes.route("/", methods=["GET"])
def readyness():  # pragma: no cover
    """easy."""
    return jsonify({"status": "ok!"}), 200
