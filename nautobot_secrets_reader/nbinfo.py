"""Read the secret group information from Nautobot"""

from asyncio.log import logger
import json
import os
from typing import Any, Dict, Optional
from dotenv import load_dotenv
import pynautobot
import logging

logger = logging.getLogger(__name__)


class SecretGroupinfo:
    """Read the secret group information from Nautobot"""

    GRAPHQL_QUERY = """
    query ($secrets_group_id: ID) {
        secrets_group(id: $secrets_group_id) {
            id
            name
            slug
            secretsgroupassociation_set {
                access_type
                secret_type
                secret {
                    id
                    provider
                    name
                    slug
                    parameters
                    description
                }
            }
        }
    }
    """

    def __init__(self):
        """Initialize the class"""
        load_dotenv()
        # Get Nautobot server account information
        self.nautobot_api_endpoint = os.getenv("NAUTOBOT_API_ENDPOINT")
        self.nautobot_token = os.getenv("NAUTOBOT_TOKEN")
        self.nautobot_api_version = os.getenv("NAUTOBOT_API_VERSION")
        self.nautobot = None

    @property
    def nb_connection(self):
        """Returns the connected pynautobot.api object."""
        if self.nautobot is None:
            try:
                self.nautobot = pynautobot.api(url=self.nautobot_api_endpoint, token=self.nautobot_token)
            except Exception as e:
                print(repr(e))
                return None
        return self.nautobot

    def get_secrets_group_info_by_id(self, secrets_group_id: str) -> Optional[Dict[str, Any]]:
        """Query the secret group information from Nautobot

        Args:
            secrets_group_id (str): The Nautobot secrets-group ID.

        Returns:
            Dict[str, Any]: The Nautobot secrets-group information.
        """
        # Get the secret group information from Nautobot
        variables = {"secrets_group_id": secrets_group_id}
        try:
            secret_group_info = self.nb_connection.graphql.query(  # type: ignore
                query=self.GRAPHQL_QUERY, variables=variables
            )
        except pynautobot.core.graphql.GraphQLException as e:  # type: ignore
            logger.error(f"Error querying Nautobot: {e}")
            return None
        return dict(secret_group_info.json["data"])

    def get_secrets_group_info_from_device_name(self, device_name: str) -> Optional[Dict[str, Any]]:
        """Get the secret group information from a Nautobot device name.

        Args:
            device_name (str): The Nautobot device-name.

        Returns:
            Dict[str, Any]: The Nautobot secrets-group information.
        """            
        device = self.nb_connection.dcim.devices.get(name=device_name)  # type: ignore
        if device is not None and device.secrets_group is None:
            # Get the master device of current virtual chassis if exists
            if device.virtual_chassis is not None:
                virtual_chassis = device.virtual_chassis
                if virtual_chassis.master is not None:
                    device = virtual_chassis.master
        if device is None or device.secrets_group is None:
            return None
        secrets_group_id = device.secrets_group.id
        # Return the secret group information
        return self.get_secrets_group_info_by_id(secrets_group_id)
