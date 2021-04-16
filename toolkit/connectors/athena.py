import os
import boto3
import pandas as pd
from pyathenajdbc import connect
from pyathenajdbc.util import as_pandas


class AthenaConnector(object):

    config = {"schema": "default", "log_path": "/tmp/AthenaConnector.log"}

    def __init__(
        self, profile=None, role=None, region="eu-west-1", s3_staging_dir=None, **kwargs
    ):
        self.__aws_role = role
        self.region = region

        self.__b = (
            boto3.session.Session()
            if profile is None
            else boto3.session.Session(profile_name=profile)
        )

        self.__sts = self.__b.client("sts")
        self.config.update(kwargs)

        self._set_aws_credentials()
        self.s3_staging_dir = s3_staging_dir or self._get_default_staging_dir()

        self._connection = connect(
            schema_name=self.config["schema"],
            s3_staging_dir=self.s3_staging_dir,
            region_name=self.region,
            log_path=self.config["log_path"],
        )
        self._cursor = self._connection.cursor()

    def _set_aws_credentials(self):
        if self.__aws_role:
            aws_cred = self.__sts.assume_role(
                RoleArn=self.__aws_role,
                RoleSessionName="Session-" + self.__aws_role.split("/")[-1],
                # Asking for the maximum token time (1h)
                DurationSeconds=3600,
            )
            self.__aws_account_id = aws_cred["AssumedRoleUser"]["Arn"].split(":")[-2]
            self.__aws_access_key = aws_cred["Credentials"]["AccessKeyId"]
            self.__aws_secret_key = aws_cred["Credentials"]["SecretAccessKey"]
            self.__aws_sess_token = aws_cred["Credentials"]["SessionToken"]
            self.__aws_token_time = aws_cred["Credentials"]["Expiration"]
        else:
            aws_cred = self.__b.get_credentials()
            self.__aws_account_id = self.__sts.get_caller_identity()["Account"]
            self.__aws_access_key = aws_cred.access_key
            self.__aws_secret_key = aws_cred.secret_key
            self.__aws_sess_token = aws_cred.token
            self.__aws_token_time = None

        os.environ["AWS_ACCESS_KEY_ID"] = str(self.__aws_access_key)
        os.environ["AWS_SECRET_ACCESS_KEY"] = str(self.__aws_secret_key)
        os.environ["AWS_SESSION_TOKEN"] = str(self.__aws_sess_token)

    def connection(self):
        return self._connection

    def cursor(self):
        return self._cursor

    def refresh_token(self):
        raise NotImplementedError("Will be implemented in the future.")

    def return_df(self, query):
        self._cursor.execute(query)
        return as_pandas(self._cursor)

    def _get_default_staging_dir(self):
        return "s3://aws-athena-query-results-{account_id}-{aws_region}/".format(
            account_id=self.__aws_account_id, aws_region=self.region
        )