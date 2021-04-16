import ast
import boto3
import base64


class SecretManager(object):
    def __init__(self, profile: str = None, region: str = "eu-west-1"):
        self._session = (
            boto3.session.Session()
            if profile is None
            else boto3.session.Session(profile_name=profile)
        )

        self._manager = self._session.client(
            service_name="secretsmanager", region_name=region
        )

    def describe_session(self) -> dict:
        """Describes the initialized aws session."""
        return {
            "available_profiles": self._session.available_profiles,
            "profile_in_use": self._session.profile_name,
            "region": self._session.region_name,
        }

    def get_credential_from_secret(self, secret_key) -> dict:
        """Give a SecretKey, returns the dictionary of values associated with that secret."""
        response = self._manager.get_secret_value(SecretId=secret_key)

        if "SecretString" in response:
            secret = response["SecretString"]
        else:
            secret = base64.b64decode(response["SecretBinary"])

        return dict(ast.literal_eval(secret))
