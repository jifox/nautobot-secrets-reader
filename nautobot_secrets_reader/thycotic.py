"""Secrets Provider for Thycotic Secret Server."""
import os
from pathlib import Path
from typing import Any, Dict, Optional
from dotenv import load_dotenv

from thycotic.secrets.server import (
    AccessTokenAuthorizer,
    PasswordGrantAuthorizer,
    DomainPasswordGrantAuthorizer,
    SecretServerCloud,
    SecretServer,
    ServerSecret,
    SecretServerError,
)


from .helpers import is_truthy


class ThycoticSecretServerSecretsReader:
    """Class to read secrets from Thycotic/Delinea Secret Server."""

    CONFIG: Dict[str, Any] = {}  # Configuration values are read from environment variables.
    _secret: Optional[ServerSecret] = None  # Cashed result of get_secret()
    _param_secret_id: Optional[str] = None  # Parameter used to retireve the cached secret.
    _param_secret_path: Optional[str] = None  # Parameter used to retireve the cached secret.

    def __init__(self) -> None:
        load_dotenv()  # Load environment variables from .env file.
        self.CONFIG = {
            "thycotic": {  # https://github.com/thycotic/python-tss-sdk
                "base_url": os.getenv("SECRET_SERVER_BASE_URL"),
                "cloud_based": is_truthy(os.getenv("SECRET_SERVER_IS_CLOUD_BASED", "False")),
                # tenant: required when cloud_based == True
                "tenant": os.getenv("SECRET_SERVER_TENANT", ""),
                # Setup thycotic authorizer
                # Username | Password | Token | Domain | Authorizer
                #   def    |   def    |   *   |   -    | PasswordGrantAuthorizer
                #   def    |   def    |   *   |  def   | DomainPasswordGrantAuthorizer
                #    -     |    -     |  def  |   *    | AccessTokenAuthorizer
                #   def    |    -     |  def  |   *    | AccessTokenAuthorizer
                #    -     |   def    |  def  |   *    | AccessTokenAuthorizer
                "username": os.getenv("SECRET_SERVER_USERNAME", ""),
                "password": os.getenv("SECRET_SERVER_PASSWORD", ""),
                "token": os.getenv("SECRET_SERVER_TOKEN", ""),
                "domain": os.getenv("SECRET_SERVER_DOMAIN", ""),
                # ca_bundle_path: (optional) Path to trusted certificates file.
                #     This must be set as environment variable.
                #     see: https://docs.python-requests.org/en/master/user/advanced/
                "ca_bundle_path": os.getenv("REQUESTS_CA_BUNDLE", ""),
            }
        }

    @property
    def config(self) -> Dict[str, Any]:
        """Returns the configuration dictionary."""
        return self.CONFIG["thycotic"]

    @property
    def secret_id(self) -> Optional[str]:
        """Get the secret_id."""
        return self._param_secret_id

    @property
    def secret_path(self) -> Optional[str]:
        """Get the secret_path."""
        return self._param_secret_path

    @property
    def secret(self) -> Optional[ServerSecret]:
        """Get the secret."""
        return self._secret

    def get(self, field_name: str):
        """Extracts the value of a secrets field.
        Args:
            field_name (str): Name of the field to extract.

        Returns:
            Any: The secret value.
        """
        if not self._secret:
            raise AttributeError(
                "No secret available. Use query_thycotic_secret_server() to retrieve the secret fron Secret Server."
            )
        # Attempt to return the selected value.
        try:
            return self._secret.fields[field_name].value
        except KeyError as err:
            raise KeyError(f"Secret field '{field_name}' not found in secret '{self._secret.name}'.") from err

    def query_thycotic_secret_server(self, secret_id=None, secret_path=None):
        """Query Thycotic Secret Server.

        Args:
            secret_id (str): The secret ID.
            secret_path (str): The secret path.

        Returns:
            ServerSecret: The secret.
        """
        if self._secret and self._param_secret_id == secret_id and self._param_secret_path == secret_path:
            return self._secret
        base_url = self.config["base_url"]
        ca_bundle_path = self.config["ca_bundle_path"]
        cloud_based = self.config["cloud_based"]
        domain = self.config["domain"]
        password = self.config["password"]
        tenant = self.config["tenant"]
        token = self.config["token"]
        username = self.config["username"]
        # Ensure required parameters are set
        if any(
            [token is None and not all([username, password]), cloud_based and not all([tenant, username, password])]
        ):
            raise ValueError(
                """The Secret Server is not configured!
                See section 'Configuration' in `README.md'.
                """
            )
        # Setup authorizer
        must_restore_env = False
        original_env = os.getenv("REQUESTS_CA_BUNDLE", "")
        try:
            if ca_bundle_path is not None:
                # Ensure cerificates file exists if ca_bundle_path is defined
                if not Path(str(ca_bundle_path)).exists():
                    raise ValueError(
                        (
                            "Thycotic Secret Server is not configured properly! "
                            "Trusted certificates file not found: "
                            "Environment variable 'REQUESTS_CA_BUNDLE': "
                            f"{ca_bundle_path}."
                        )
                    )
                # Set the trusted certificates file path to environment variable.
                if original_env != ca_bundle_path:
                    os.environ["REQUESTS_CA_BUNDLE"] = str(ca_bundle_path)
                    must_restore_env = True
            # Setup thycotic authorizer
            # Username | Password | Token | Domain | Authorizer
            #   def    |   def    |   *   |   -    | PasswordGrantAuthorizer
            #   def    |   def    |   *   |  def   | DomainPasswordGrantAuthorizer
            #    -     |    -     |  def  |   *    | AccessTokenAuthorizer
            #   def    |    -     |  def  |   *    | AccessTokenAuthorizer
            #    -     |   def    |  def  |   *    | AccessTokenAuthorizer
            if all([username, password]):
                if domain is not None:
                    thy_authorizer = DomainPasswordGrantAuthorizer(
                        base_url=base_url, domain=domain, username=username, password=password
                    )
                else:
                    thy_authorizer = PasswordGrantAuthorizer(base_url=base_url, username=username, password=password)
            else:
                thy_authorizer = AccessTokenAuthorizer(token)

            # Get the client.
            if cloud_based:
                thycotic = SecretServerCloud(tenant=tenant, authorizer=thy_authorizer)
            else:
                thycotic = SecretServer(base_url=base_url, authorizer=thy_authorizer)

            # Attempt to retrieve the secret.
            try:
                if secret_id is not None:
                    secret = ServerSecret(**thycotic.get_secret(secret_id))
                    self._secret = secret
                    self._param_secret_id = str(secret_id)
                    self._param_secret_path = None
                else:
                    secret = ServerSecret(**thycotic.get_secret_by_path(secret_path))
                    self._secret = secret
                    self._param_secret_id = None
                    self._param_secret_path = str(secret_path)
            except SecretServerError as err:
                self._secret = None
                self._param_secret_id = None
                self._param_secret_path = None
                raise ValueError(f"Thycotic Secret Server error: {err.message}") from err
            return secret
        finally:
            if must_restore_env:
                os.environ["REQUESTS_CA_BUNDLE"] = original_env
