#!/usr/bin/env python
# -*- coding: utf-8 -*-
from sqlalchemy.engine import create_engine
from toolkit.aws.secrets_manager import SecretManager


class PostgresConnector(object):
    """Class to connect to a PostgresDB"""

    def __init__(
        self,
        host="localhost",
        username=None,
        password=None,
        database=None,
        port="54320",
        **kwargs
    ):
        self.__config = {
            "host": host,
            "username": username,
            "password": password,
            "database": database,
            "port": port,
        }
        self.__config.update(kwargs)

        self.host = self.__config["host"]
        self.__username = self.__config["username"]
        self.__password = self.__config["password"]
        self.database = self.__config["database"]
        self.port = self.__config["port"]
        self._connect()

    def _connect(self):
        self._engine = create_engine(
            "postgresql+psycopg2://{username}:{password}@{host}:{port}/{database}".format(
                username=self.__username,
                password=self.__password,
                host=self.host,
                port=self.port,
                database=self.database,
            )
        )

        self._connection = self._engine.raw_connection()
        self._cursor = self._connection.cursor()

    def connection(self):
        return self._connection

    def cursor(self):
        return self._cursor


class SMPostgresConnector(PostgresConnector):
    """Connects to a postgres database using the Secrets Manager
       to retrieve the credentials. 
       The secret is expected to have the following fields:
       username, password, host, database, port.
    """

    def __init__(
        self, profile="default", region="eu-west-1", secret_key=None, **kwargs
    ):
        if not secret_key:
            raise ValueError("The secret key cannot be None!")

        sm = SecretManager(profile=profile, region=region)

        _creds = sm.get_credential_from_secret(secret_key)
        _creds.update(kwargs)

        super().__init__(**_creds)
