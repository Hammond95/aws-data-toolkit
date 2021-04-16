import mock
import pytest
import ast
import textwrap

from mock import MagicMock

from toolkit.aws.secrets_manager import SecretManager


class FakeSecretManagerClient(object):
    d = (
        """
    {
        'database': 'database-name',
        'password': 'password',
        'port': '1900',
        'host': 'db.hostname.amazonaws.com',
        'username': 'test_user'
    }""".replace(
            "\n", ""
        )
        .replace(" ", "")
        .replace("'", '"')
    )

    response = """
    {{
        'ARN': 'arn:aws:secretsmanager:eu-west-1:0000000000:secret:/db/secret/generic/bla',
        'Name': '/db/secret/generic/bla',
        'VersionId': 'aaaaaaaa-bbbb-cccc-dddd-000000000000',
        'SecretString': '{secret}',
        'VersionStages': ['AWSCURRENT'],
        'CreatedDate': 'datetime.datetime(2019, 6, 12, 11, 30, 6, 420000, tzinfo=tzlocal())',
        'ResponseMetadata': {{
            'RequestId': 'aaaaaaaa-bbbb-cccc-dddd-000000000000',
            'HTTPStatusCode': 200,
            'HTTPHeaders': {{
                'date': 'Sun, 04 Aug 2019 03:51:57 GMT',
                'content-type': 'application/x-amz-json-1.1',
                'content-length': '459',
                'connection': 'keep-alive',
                'x-amzn-requestid': 'aaaaaaaa-bbbb-cccc-dddd-000000000000'
            }}, 'RetryAttempts': 0
        }}
    }}
    """.format(
        secret=d
    )

    def get_secret_value(self, SecretId="/db/secret/generic/bla"):
        return dict(
            ast.literal_eval(
                textwrap.dedent(self.response).replace("\n", "").replace(" ", "")
            )
        )


def fake_init(self):
    print(type(self))
    pass


def test_get_credentials():
    sm = SecretManager
    sm.__init__ = fake_init

    sm_instance = sm()
    sm_instance._manager = FakeSecretManagerClient()

    res = sm_instance.get_credential_from_secret("/db/secret/generic/bla")

    assert res["database"] == "database-name"
    assert res["password"] == "password"
    assert res["port"] == "1900"
    assert res["host"] == "db.hostname.amazonaws.com"
    assert res["username"] == "test_user"


if __name__ == "__main__":
    # Unit Test
    test_get_credentials()