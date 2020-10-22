# Copyright (c) 2020, Oracle and/or its affiliates.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License, version 2.0,
# as published by the Free Software Foundation.
#
# This program is also distributed with certain software (including
# but not limited to OpenSSL) that is licensed under separate terms, as
# designated in a particular file or component or in included license
# documentation.  The authors of MySQL hereby grant you an additional
# permission to link the program and your derivative works with the
# separately licensed software that they have included with MySQL.
# This program is distributed in the hope that it will be useful,  but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See
# the GNU General Public License, version 2.0, for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin St, Fifth Floor, Boston, MA 02110-1301 USA

from .innodbcluster import operator_cluster
from .backup import operator_backup
from . import config, utils
from .group_monitor import g_group_monitor
import kopf
import datetime


# @kopf.on.login()
# def on_login(**kwargs):
#     return kopf.login_via_client(**kwargs)


@kopf.on.startup()
def on_startup(settings: kopf.OperatorSettings, logger, **_):
    utils.log_banner(__file__, logger)

    # Change the annotation field for storing kopf state, so that the main operator
    # and the pod controller don't collide
    # settings.persistence.finalizer = "operator.mysql.oracle.com/kopf-finalizer"
    # settings.persistence.progress_storage = kopf.AnnotationsProgressStorage(prefix='operator.mysql.oracle.com')
    # settings.persistence.diffbase_storage = kopf.AnnotationsDiffBaseStorage(
    #     name='operator.mysql.oracle.com/last-handled-configuration'
    # )

    operator_cluster.monitor_existing_clusters()

    g_group_monitor.start()



@kopf.on.cleanup()
def on_shutdown(logger, **kwargs):
    g_group_monitor.stop()