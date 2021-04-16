#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import getpass

from pyhive import presto


class PrestoConnector(object):
    """Class to connect to the Presto cluster on aws EMR"""

    local_user = getpass.getuser()

    def __init__(self, host="localhost", schema="default", catalog="hive", port="8889"):
        self.cluster_name = "PrestoCluster"
        self.host = host
        self.__user = self.local_user
        self.schema = schema
        self.catalog = catalog
        self.port = port
        self._connect()

    def _connect(self):
        self._connection = presto.connect(
            host=self.host, port=self.port, username=self.__user, catalog=self.catalog
        )
        self._cursor = self._connection.cursor()

    def get_connection_str(self):
        return "presto://{host}:{port}/{catalog}/{schema}".format(
            host=self.host, port=self.port, schema=self.schema, catalog=self.catalog
        )

    def connection(self):
        return self._connection

    def cursor(self):
        return self._cursor