"""Access secrets provides by Nautobot secrets providers."""
from typing import Any, Callable, Dict, List, Tuple, Optional, Union

from .nbinfo import SecretGroupinfo
from .delinea import ThycoticSecretServerSecretsReader

import logging

logger = logging.getLogger(__name__)

# Initialize logging to console
logger.setLevel(logging.INFO)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)


class SecretsReader:
    """Access secrets provides by Nautobot secrets providers."""

    def __init__(self):
        """Initialize the SecretsReader class."""
        # Instantiate Nautobot access object
        self.nbot = SecretGroupinfo()
        self.secret_tss_result = None
        self.secret_id = None
        self.secret_path = None

    def get_secret_tss(self, parameters: Dict[str, Any]) -> str:
        """Returns the secret value from Thycotic/Delinea Secret Server.

        This function cashes the result so that retieving a different field of the
        same secret, will not trigger a Thycotic/Delinea Secret Server API call.

        Args:
            parameters (Dict[str, Any]): The parameters as returned from Nautobot.
        Returns:
            str: The secret value.
        """
        secret_id = None
        secret_path = None
        try:
            try:
                secret_id = parameters["secret_id"]
            except KeyError:
                secret_path = parameters["secret_path"]
            # Check if the secret is already read
            if self.secret_tss_result is None or self.secret_id != secret_id or self.secret_path != secret_path:
                # Perform API call to Thycotic/Delinea Secret Server
                connection = ThycoticSecretServerSecretsReader()
                self.secret_tss_result = connection.query_thycotic_secret_server(
                    secret_id=secret_id, secret_path=secret_path
                )
                self.secret_id = secret_id
                self.secret_path = secret_path
            # Return the secret value
            return self.secret_tss_result.fields[parameters["secret_selected_value"]].value  # type: ignore
        except ValueError:
            msg = (
                f"ERROR Reading the Thycotic secret Id:{str(secret_id) if secret_id is not None else 'None'}, "
                f"Path: {str(secret_path) if secret_path is not None else 'None'}!"
            )
            logger.error(msg)
            print(msg)
        return ""

    def read_credentials(self, secrets_group_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Read and Parse secrets_group_data and return a list of all credentials in secrets group.

        Args:
            secrets_group_id (secrets_group_data: Dict[str, Any]): The secrets group id.

        Returns:
            List[Dict[str, Any]]: The list of all credentials in secrets group.

            example: [ {'access_type': 'GENERIC',
                        'secret_description': 'Cisco Switches ATBRKHKP',
                        'secret_id': '63ced5a8-801f-4321-bdad-d0e17559377b',
                        'secret_name': 'Cisco Switches Fallback Password PWD',
                        'secret_provider': 'thycotic-tss-path',
                        'secret_slug': 'cisco-switches-fallback-password-pwd',
                        'secret_type': 'PASSWORD',
                        'value': 'The-Password-Stored-in-Vault'},
                    ]
        raises:
            ValueError: If the secrets provider is not supported.
        """
        if secrets_group_data is None:
            return []
        if not "secrets_group" in secrets_group_data:
            return []

        result: List[Dict[str, Any]] = []
        for sec_info in secrets_group_data["secrets_group"]["secretsgroupassociation_set"]:
            provider = sec_info["secret"]["provider"]

            secrets_info = dict(
                access_type=sec_info["access_type"],  #           e.g.: 'SSH'
                secret_type=sec_info["secret_type"],  #                 'PASSWORD'
                secret_name=sec_info["secret"]["name"],  #              'Checkpoint FWDC - USR'
                secret_slug=sec_info["secret"]["slug"],  #              'checkpoint_fwdc-usr'
                secret_id=sec_info["secret"]["id"],  #                  '7d195c23-2e2c-4ced-b496-b7e524205a62'
                secret_provider=sec_info["secret"]["provider"],  #      'thycotic-tss-id'
                secret_description=sec_info["secret"]["description"],  # 'Datacenter Firewall Cluster'
                value="",  # The empty secret
            )
            func: Callable[[Dict[Any, str]], str] = None  # type: ignore
            if provider in ["thycotic-tss-id", "thycotic-tss-path"]:
                func = self.get_secret_tss
            # elif provider in ...
            else:
                raise ValueError(f"Secrets Provider ({provider}) is not suppoted!")

            secret_value = func(parameters=sec_info["secret"]["parameters"])
            secrets_info.update(dict(value=secret_value))
            result.append(secrets_info)
        return result

    def get_credentials_for_device(self, device_name: str) -> List[Dict[str, Any]]:
        """Get credentials for device.

        Args:
            device_name (str): The Nautobot device name.

        Returns:
            List[Dict[str, Any]]: The list of all credentials in secrets group.

            example: [ {'access_type': 'GENERIC',
                        'secret_description': 'Cisco Switches ATBRKHKP',
                        'secret_id': '63ced5a8-801f-4321-bdad-d0e17559377b',
                        'secret_name': 'Cisco Switches Fallback Password PWD',
                        'secret_provider': 'thycotic-tss-path',
                        'secret_slug': 'cisco-switches-fallback-password-pwd',
                        'secret_type': 'PASSWORD',
                        'value': 'The-Password-Stored-in-Vault'},
                    ]
        raises:
            ValueError: If the secrets provider is not supported.
        """
        # Get the secret group info from the device name
        secret_group_info = self.nbot.get_secrets_group_info_from_device_name(device_name)
        if secret_group_info is None:
            return []
        return self.read_credentials(secret_group_info)

    def get_credentials_for_secrets_group_id(self, secrets_group_id: str) -> List[Dict[str, Any]]:
        """Get credentials for secrets group id.

        Args:
            secrets_group_id (str): The secrets group id.

        Returns:
            List[Dict[str, Any]]: The list of all credentials in secrets group.

            example: [ {'access_type': 'GENERIC',
                        'secret_description': 'Cisco Switches ATBRKHKP',
                        'secret_id': '63ced5a8-801f-4321-bdad-d0e17559377b',
                        'secret_name': 'Cisco Switches Fallback Password PWD',
                        'secret_provider': 'thycotic-tss-path',
                        'secret_slug': 'cisco-switches-fallback-password-pwd',
                        'secret_type': 'PASSWORD',
                        'value': 'The-Password-Stored-in-Vault'},
                    ]
        raises:
            ValueError: If the secrets provider is not supported.
        """
        # Get the secret group info from the secrets group id
        secret_group_info = self.nbot.get_secrets_group_info_by_id(secrets_group_id)
        if secret_group_info is None:
            return []
        # Return the credentials
        return self.read_credentials(secret_group_info)

    def filter_access_type(self, credentials: List[Dict[str, Any]], access_type: str) -> Dict[str, Any]:
        """Filter credentials by access type.

        Args:
            credentials (List[Dict[str, Any]]): The secrets_group_info as returned by
                    get_credentials_for_secrets_group_id() or
                    get_credentials_for_device().
            access_type (str): The access type.
                    see:
                        class SecretsGroupAccessTypeChoices(ChoiceSet) in
                        https://github.com/nautobot/nautobot/blob/develop/nautobot/extras/choices.py

        Returns:
            List[Dict[str, Any]]: The filtered credentials.
        """
        result = {}
        for cred in credentials:
            if cred["access_type"].lower() == access_type.lower():
                result.update({cred["secret_type"].lower(): cred["value"]})
        return result
