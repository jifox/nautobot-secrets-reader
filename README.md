# Python Module Nautobot-Secrets-Reader

### Nautobot Secrets Python Modul

**Nautobot** allows the definition of **Secrets Groups** which contain a list of secrets used to access devices, etc. For security reasons, Nautobot generally does not store sensitive secrets (device access credentials, systems-integration API tokens, etc.) in its own database.

This module provides access to the secrets stored in a compatible secrets provider. Only access to the "Delinea/Thycotic Secret Server" is currently implemented.

refere to:

* Nautobot Secrets Dokumentation:  <https://nautobot.readthedocs.io/en/latest/core-functionality/secrets>
* Nautobot-Plugin-Secrets-Providers: <https://github.com/nautobot/nautobot-plugin-secrets-providers>


## Development Environment Installation

**Install Poetry**

Poetry must be installed before the Python Virtual Environment can be activated. see: Poetry Documentation
see: [Poetry Docomentation](https://python-poetry.org/docs/)

At the time of this writing, Poetry is installed using the following command:

```bash
curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/install-poetry.py | python -
```

**Virtual Environment**

Mit `poetry` wird das Python Virtual Environment initialisiert

```bash
# Deactivate eventually active virtual environment
deactivate

# Specify python version to use
poetry env use 3.9

# Install modul and development packages
poetry install

# Activate virtual environment
poetry shell
```

## Configuration

The following environment variables must be configured to access _Nautobot_ and the _Delinea/Thycotic Secret Server_.

This can be done in the `.env` file to

```
#############################################################################
# Settings for Nautobot Access
#     e.g. Server: https://nautobot-dev.example.local:8080
#
NAUTOBOT_API_ENDPOINT|https://nautobot-prod.example.local:8083
NAUTOBOT_TOKEN|1234567890123456789012345678901234567890
NAUTOBOT_API_VERSION|1.3


#############################################################################
# Settings for Thycotic Secret-Server-Reader
#     https://github.com/thycotic/python-tss-sdk

SECRET_SERVER_BASE_URL='https://pw.example.local/SecretServer'

# SECRET_SERVER_IS_CLOUD_BASED: (optional) Set to 'True' if you access a
#     cloud based service. (Default: 'False' on-prem)
# SECRET_SERVER_IS_CLOUD_BASED='False'

# Required when SECRET_SERVER_IS_CLOUD_BASED == True
# SECRET_SERVER_TENANT=''

# Specify either username and password or token. If both are defined
# username and password will be used for authentication
# Username | Password | Token | Domain | Authorizer
#   def    |    def   |   *   |   -    | PasswordGrantAuthorizer
#   def    |    def   |   *   |  def   | DomainPasswordGrantAuthorizer
#    -     |    -     |  def  |   -    | AccessTokenAuthorizer
SECRET_SERVER_USERNAME='pw_user'
SECRET_SERVER_PASSWORD='pw_secret_password'
# SECRET_SERVER_TOKEN=""
# SECRET_SERVER_DOMAIN=""

# REQUESTS_CA_BUNDLE (Optional)
#   Specify the trusted certificates file path for self signed certificates
#   e.g. '/etc/ssl/certs/ca-bundle.trust.crt'
REQUESTS_CA_BUNDLE='/etc/ssl/certs/ca-certificates.crt'
```


## Device-Name Secrets


Access to the secrets of a device can be seen in the following example:


```python
from nautobot_secrets_reader.secread import SecretsReader
```

```python
class SecretsReader:
    """Access secrets provides by Nautobot secrets providers."""

    def get_credentials_for_device(self, device_name: str) -> List[Dict[str, Any]]:
        """Get credentials for device.

        Args:
            device_name (str): The Nautobot device name.

        Returns:
            List[Dict[str, Any]]: The list of all credentials in secrets group.

            example: [ {'access_type': 'GENERIC',
                        'secret_description': 'Cisco Switches ATBRKHKP',
                        'secret_id': '63ced5a8-801f-4321-bdad-d0e17559377b',
                        'secret_name': 'Demo Switches Password PWD',
                        'secret_provider': 'thycotic-tss-path',
                        'secret_slug': 'demo-switches-password-pwd',
                        'secret_type': 'PASSWORD',
                        'value': 'The-Password-Stored-in-Vault'},
                    ]
        raises:
            ValueError: If the secrets provider is not supported.
        """

```


```python
DEVICE_NAME = "ATKPTEST"

sr = SecretsReader()
group_data = sr.get_credentials_for_device(DEVICE_NAME)
```

Die Daten der Nautobot Secrets Group sind im folgenden zu sehen.

Dabei sind die Daten welche mit `secret_...` beginnen, Daten aus Nautobot. Das Feld `value` ist das Ergebnis der Anfrage beim entsprechenden **Secrets Provider**


```python
# Imports only for this document
from pprint import pprint
pprint(group_data)
```

    [{'access_type': 'GENERIC',
      'secret_description': '',
      'secret_id': 'f5194ff8-5ffb-4b0e-a77f-ee7a9a3fd5e5',
      'secret_name': 'Test-Password-Path',
      'secret_provider': 'thycotic-tss-path',
      'secret_slug': 'test-password-path',
      'secret_type': 'PASSWORD',
      'value': 'FLD-PASSWORD'},
     {'access_type': 'GENERIC',
      'secret_description': '',
      'secret_id': 'f5194ff8-5ffb-4b0e-a77f-ee7a9a3fd5e5',
      'secret_name': 'Test-Password-Path',
      'secret_provider': 'thycotic-tss-path',
      'secret_slug': 'test-password-path',
      'secret_type': 'SECRET',
      'value': 'FLD-PASSWORD'},
     {'access_type': 'GENERIC',
      'secret_description': 'Username',
      'secret_id': '3f3a7832-fe45-46b3-93d5-eafbd97de565',
      'secret_name': 'TEST-User-ID',
      'secret_provider': 'thycotic-tss-id',
      'secret_slug': 'test-test-user-id',
      'secret_type': 'USERNAME',
      'value': 'FLD-Username'}]


## Filter the Results

The following routine is available for filtering the data via `access_type`:

https://nautobot.readthedocs.io/en/latest/core-functionality/secrets/

At the time writing, the following `access_type`s were available (in the data set without "TYPE_..."):

| access_type   | description |
|---|---|
| TYPE_GENERIC  | "Generic"  |
| TYPE_CONSOLE  | "Console"  |
| TYPE_GNMI     | "gNMI"     |
| TYPE_HTTP     | "HTTP(S)"  |
| TYPE_NETCONF  | "NETCONF"  |
| TYPE_REST     | "REST"     |
| TYPE_RESTCONF | "RESTCONF" |
| TYPE_SNMP     | "SNMP"     |
| TYPE_SSH      | "SSH"      |

e.g.: TYPE_GENERIC is stored as "GENERIC".

The current selection can be seen in the class: [class SecretsGroupAccessTypeChoices(ChoiceSet)](https://github.com/nautobot/nautobot/blob/develop/nautobot/extras/choices.py)


```python
class SecretsReader:
    """Access secrets provides by Nautobot secrets providers."""

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
```


```python
generic = sr.filter_access_type(group_data, "GENERIC")

pprint(generic)
```

    {'password': 'FLD-PASSWORD',
     'secret': 'FLD-PASSWORD',
     'username': 'FLD-Username'}


## Nautobot Group-ID Secrets

The secrets for a particular Secrets Group can be selected from Nautobot by Group-ID as follows:


```python
group_id = "43974686-e26c-40a5-8951-854a609be812"
secrets_per_id = sr.get_credentials_for_secrets_group_id(group_id)
```


```python
pprint(secrets_per_id)
```

    [{'access_type': 'GENERIC',
      'secret_description': '',
      'secret_id': 'f5194ff8-5ffb-4b0e-a77f-ee7a9a3fd5e5',
      'secret_name': 'Test-Password-Path',
      'secret_provider': 'thycotic-tss-path',
      'secret_slug': 'test-password-path',
      'secret_type': 'PASSWORD',
      'value': 'FLD-PASSWORD'},
     {'access_type': 'GENERIC',
      'secret_description': '',
      'secret_id': 'f5194ff8-5ffb-4b0e-a77f-ee7a9a3fd5e5',
      'secret_name': 'Test-Password-Path',
      'secret_provider': 'thycotic-tss-path',
      'secret_slug': 'test-password-path',
      'secret_type': 'SECRET',
      'value': 'FLD-PASSWORD'},
     {'access_type': 'GENERIC',
      'secret_description': 'Username',
      'secret_id': '3f3a7832-fe45-46b3-93d5-eafbd97de565',
      'secret_name': 'TEST-User-ID',
      'secret_provider': 'thycotic-tss-id',
      'secret_slug': 'test-test-user-id',
      'secret_type': 'USERNAME',
      'value': 'FLD-Username'}]



```bash
%%bash
# Running the Tests

pytest nautobot_secrets_reader -s
```

    ============================= test session starts ==============================
    platform linux -- Python 3.9.10, pytest-7.0.1, pluggy-1.0.0
    rootdir: /home/ansible/src/secret-server-reader
    plugins: pylama-7.7.1, anyio-3.6.1
    collected 4 items
    
    nautobot_secrets_reader/tests/test_secread.py ...[{'access_type': 'GENERIC',
      'secret_description': '',
      'secret_id': 'f5194ff8-5ffb-4b0e-a77f-ee7a9a3fd5e5',
      'secret_name': 'Test-Password-Path',
      'secret_provider': 'thycotic-tss-path',
      'secret_slug': 'test-password-path',
      'secret_type': 'PASSWORD',
      'value': 'FLD-PASSWORD'},
     {'access_type': 'GENERIC',
      'secret_description': '',
      'secret_id': 'f5194ff8-5ffb-4b0e-a77f-ee7a9a3fd5e5',
      'secret_name': 'Test-Password-Path',
      'secret_provider': 'thycotic-tss-path',
      'secret_slug': 'test-password-path',
      'secret_type': 'SECRET',
      'value': 'FLD-PASSWORD'},
     {'access_type': 'GENERIC',
      'secret_description': 'Username',
      'secret_id': '3f3a7832-fe45-46b3-93d5-eafbd97de565',
      'secret_name': 'TEST-User-ID',
      'secret_provider': 'thycotic-tss-id',
      'secret_slug': 'test-test-user-id',
      'secret_type': 'USERNAME',
      'value': 'FLD-Username'}]
    GENERIC: {'password': 'FLD-PASSWORD', 'secret': 'FLD-PASSWORD', 'username': 'FLD-Username'}
    .
    
    ============================== 4 passed in 3.26s ===============================
