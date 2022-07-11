# Copyright (c) 2022, Oracle and/or its affiliates.
#
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl/
#

import unittest
from e2e.mysqloperator.enterprise import audit_log_base
from setup.config import g_ts_cfg
from utils import auxutil, mutil
from utils import kutil

@unittest.skipIf(g_ts_cfg.enterprise_skip, "Enterprise test cases are skipped")
class AuditLog(audit_log_base.AuditLogBase):
    add_data_timestamp = None
    test_table = "mycluster0"

    def test_0_create(self):
        self.create_cluster()


    def test_1_init(self):
        self.install_plugin_on_primary("mycluster-0")
        self.set_filter_on_all("mycluster-0")


    def test_2_add_data(self):
        self.__class__.add_data_timestamp = auxutil.utctime()
        with mutil.MySQLPodSession(self.ns, "mycluster-0", self.user, self.password) as s:
            s.exec_sql("CREATE SCHEMA audit_foo")
            s.exec_sql(f"CREATE TABLE audit_foo.{self.test_table} (id INT NOT NULL, name VARCHAR(20), PRIMARY KEY(id))")
            s.exec_sql(f'INSERT INTO audit_foo.{self.test_table} VALUES (123456, "first_audit")')
            s.exec_sql(f'INSERT INTO audit_foo.{self.test_table} VALUES (654321, "second_audit")')
            s.exec_sql(f'FLUSH TABLES audit_foo.{self.test_table}')


    def test_3_verify_log(self):
        self.assertTrue(self.does_log_exist("mycluster-0"))

        log_data = self.get_log_data("mycluster-0", self.__class__.add_data_timestamp)
        self.assertIn("CREATE SCHEMA audit_foo", log_data)
        self.assertIn(f"CREATE TABLE audit_foo.{self.test_table} (id INT NOT NULL, name VARCHAR(20), PRIMARY KEY(id))", log_data)
        self.assertIn(f'INSERT INTO audit_foo.{self.test_table} VALUES (123456, \\\\"first_audit\\\\")', log_data)
        self.assertIn(f'INSERT INTO audit_foo.{self.test_table} VALUES (654321, \\\\"second_audit\\\\")', log_data)


    def test_9_destroy(self):
        kutil.delete_ic(self.ns, "mycluster")

        self.wait_pods_gone("mycluster-*")
        self.wait_routers_gone("mycluster-router-*")
        self.wait_ic_gone("mycluster")

        kutil.delete_secret(self.ns, "mypwds")