import pytest
from pprint import pprint

from nautobot_secrets_reader.nbinfo import SecretGroupinfo
from nautobot_secrets_reader.secread import SecretsReader


@pytest.fixture
def nbconn():
    """Returns the connected pynautobot.api object."""
    nb = SecretGroupinfo()
    return nb.nb_connection


def test_secread_secretgroupinfo_connect(nbconn):
    assert nbconn is not None


def test_secred_get_secret_group_info_from_device_name():
    device_name = "ATKPTEST"
    nb = SecretGroupinfo()
    secret_group_info = nb.get_secrets_group_info_from_device_name(device_name)
    assert secret_group_info is not None


def test_secrets_reader_get_credentials_for_device(nbconn):
    device_name = "ATKPTEST"
    secreader = SecretsReader()
    credentials = secreader.get_credentials_for_device(device_name)
    assert credentials is not None


def test_secrets_reader_get_credentials_for_secrets_group_id(nbconn):
    group_id = "43974686-e26c-40a5-8951-854a609be812"
    secreader = SecretsReader()
    credentials = secreader.get_credentials_for_secrets_group_id(group_id)
    assert credentials is not None
    pprint(credentials, width=120)

    generic = secreader.filter_access_type(credentials, "GENERIC")
    assert generic is not None
    print("GENERIC", end=": ")
    pprint(generic, width=120)
