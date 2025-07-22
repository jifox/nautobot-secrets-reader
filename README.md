# Python Module Nautobot-Secrets-Reader


**Work in Progress: Currently only Delinea/Thycothic Secret Server Access is imlemented.**

### Nautobot Secrets Python Modul

**Nautobot** allows the definition of **Secrets Groups** which contain a list of secrets used to access devices, etc. For security reasons, Nautobot generally does not store sensitive secrets (device access credentials, systems-integration API tokens, etc.) in its own database.

This module provides access to the secrets stored in a compatible secrets provider. Only access to the "Delinea/Thycotic Secret Server" is currently implemented.

refere to:

* Nautobot Secrets Dokumentation:  <https://nautobot.readthedocs.io/en/latest/core-functionality/secrets>
* Nautobot-Plugin-Secrets-Providers: <https://github.com/nautobot/nautobot-plugin-secrets-providers>

## Compatibility Matrix
| Nautobot Version | Nautobot-Secrets-Reader Version | Supported Secret Providers | Git Branch |
|------------------|-------------------|----------------------------------------|------------|
| >=1.4.0, <2.0    | >=1.0.0,<2.0.0    | Delinea/Thycotic Secret Server         | release-1.0  |
| >=2.0.0, <3.0    | >=2.0.0,<3.0.0    | Delinea/Thycotic Secret Server         | release-2.0  |


## Development Environment Installation

**Install Poetry**

Poetry must be installed before the Python Virtual Environment can be activated. see: Poetry Documentation
see: [Poetry Docomentation](https://python-poetry.org/docs/)

At the time of this writing, Poetry is installed using the following command:

```bash
# Optionally set the CA-Bundle for SSL connections
export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt

# Install Poetry
POETRY_VERSION=1.8.5 curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/install-poetry.py | python -

# Add Poetry to PATH
export PATH="$HOME/.local/bin:$PATH"

# Add the dotenv plugin to Poetry that loads .env files automatically
poetry self add poetry-dotenv-plugin
```


**Virtual Environment**

`Poetry` is used to setup a Python Virtual Environment.

```bash
# Deactivate eventually active virtual environment
deactivate

# Specify python version to use
poetry env use 3.12

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
NAUTOBOT_API_ENDPOINT=https://nautobot-prod.example.local:8083
NAUTOBOT_TOKEN=1234567890123456789012345678901234567890
NAUTOBOT_API_VERSION=1.4


#############################################################################
# Settings for Delinea/Thycotic Secret-Server-Reader
#     https://github.com/DelineaXPM/python-tss-sdk

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
# Initialize the environment variables for the project
from dotenv import load_dotenv
load_dotenv(".env", override=True)
```




    True



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

The variable `group_data` contains the Nautobot Secrets Group information.

Field names starting with `secret_...`, are data from Nautobot. Das field `value` contains the seret value retrieved from the specified `secret_provider`.

```python
# Imports only for this document
from pprint import pprint
for gd in group_data:
    if gd["secret_type"] in ["PASSWORD", "SECRET", "USERNAME"]:
        gd["value"] = "(REDACTED)"
pprint(group_data)
```

    [{'access_type': 'GENERIC',
      'secret_description': 'Cisco Switches ATBRKHKP',
      'secret_id': '63ced5a8-801f-4321-bdad-d0e17559377b',
      'secret_name': 'Cisco Switches PWD - ATBRKHKP - [01]',
      'secret_provider': 'delinea-tss-id',
      'secret_type': 'PASSWORD',
      'value': '(REDACTED)'},
     {'access_type': 'GENERIC',
      'secret_description': 'Cisco Switches Enable Passwort',
      'secret_id': '330b2983-3f33-4b00-be4f-258e642e6fac',
      'secret_name': 'Cisco Switches Enable - ATBRKPKH - [01]',
      'secret_provider': 'delinea-tss-id',
      'secret_type': 'SECRET',
      'value': '(REDACTED)'},
     {'access_type': 'GENERIC',
      'secret_description': 'Cisco Switches ATBRKHKP',
      'secret_id': 'a7b50e47-25cb-4f07-8641-ff3eda42effe',
      'secret_name': 'Cisco Switches - ATBRKHKO - USR - [01]',
      'secret_provider': 'delinea-tss-id',
      'secret_type': 'USERNAME',
      'value': '(REDACTED)'},
     {'access_type': 'HTTP_S_',
      'secret_description': 'Cisco Switches ATBRKHKP',
      'secret_id': '63ced5a8-801f-4321-bdad-d0e17559377b',
      'secret_name': 'Cisco Switches PWD - ATBRKHKP - [01]',
      'secret_provider': 'delinea-tss-id',
      'secret_type': 'PASSWORD',
      'value': '(REDACTED)'},
     {'access_type': 'HTTP_S_',
      'secret_description': 'Cisco Switches Enable Passwort',
      'secret_id': '330b2983-3f33-4b00-be4f-258e642e6fac',
      'secret_name': 'Cisco Switches Enable - ATBRKPKH - [01]',
      'secret_provider': 'delinea-tss-id',
      'secret_type': 'SECRET',
      'value': '(REDACTED)'},
     {'access_type': 'HTTP_S_',
      'secret_description': 'Cisco Switches ATBRKHKP',
      'secret_id': 'a7b50e47-25cb-4f07-8641-ff3eda42effe',
      'secret_name': 'Cisco Switches - ATBRKHKO - USR - [01]',
      'secret_provider': 'delinea-tss-id',
      'secret_type': 'USERNAME',
      'value': '(REDACTED)'},
     {'access_type': 'SSH',
      'secret_description': 'Cisco Switches ATBRKHKP',
      'secret_id': '63ced5a8-801f-4321-bdad-d0e17559377b',
      'secret_name': 'Cisco Switches PWD - ATBRKHKP - [01]',
      'secret_provider': 'delinea-tss-id',
      'secret_type': 'PASSWORD',
      'value': '(REDACTED)'},
     {'access_type': 'SSH',
      'secret_description': 'Cisco Switches Enable Passwort',
      'secret_id': '330b2983-3f33-4b00-be4f-258e642e6fac',
      'secret_name': 'Cisco Switches Enable - ATBRKPKH - [01]',
      'secret_provider': 'delinea-tss-id',
      'secret_type': 'SECRET',
      'value': '(REDACTED)'},
     {'access_type': 'SSH',
      'secret_description': 'Cisco Switches ATBRKHKP',
      'secret_id': 'a7b50e47-25cb-4f07-8641-ff3eda42effe',
      'secret_name': 'Cisco Switches - ATBRKHKO - USR - [01]',
      'secret_provider': 'delinea-tss-id',
      'secret_type': 'USERNAME',
      'value': '(REDACTED)'}]


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
from string import printable


generic = sr.filter_access_type(group_data, "GENERIC")
printable = generic
if printable["password"] is not None:
    printable["password"] = "MyPassword"
if printable["username"] is not None:
    printable["username"] = "MyUsername"
if printable["secret"] is not None:
    printable["secret"] = "MySecret"
pprint(printable)
```

    {'password': 'MyPassword', 'secret': 'MySecret', 'username': 'MyUsername'}


## Nautobot Group-ID Secrets

The secrets for a particular Secrets Group can be selected from Nautobot by Group-ID as follows:

```python
# This test Secret Group-ID contains only placeholder credentials
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
      'secret_provider': 'delinea-tss-path',
      'secret_type': 'PASSWORD',
      'value': 'FLD-PASSWORD'},
     {'access_type': 'GENERIC',
      'secret_description': '',
      'secret_id': 'f5194ff8-5ffb-4b0e-a77f-ee7a9a3fd5e5',
      'secret_name': 'Test-Password-Path',
      'secret_provider': 'delinea-tss-path',
      'secret_type': 'SECRET',
      'value': 'FLD-PASSWORD'},
     {'access_type': 'GENERIC',
      'secret_description': 'Username',
      'secret_id': '3f3a7832-fe45-46b3-93d5-eafbd97de565',
      'secret_name': 'TEST-User-ID',
      'secret_provider': 'delinea-tss-id',
      'secret_type': 'USERNAME',
      'value': 'FLD-Username'}]


## Running the Tests

```bash
%%bash
# Running the Tests
pytest nautobot_secrets_reader -s
```

<<<<<<< HEAD
    ============================= test session starts ==============================
    platform linux -- Python 3.9.10, pytest-7.1.2, pluggy-1.0.0
    rootdir: /home/ansible/src/secret-server-reader
    plugins: pylama-8.4.1, anyio-3.6.1
=======
    [1m============================= test session starts ==============================[0m
    platform linux -- Python 3.12.10, pytest-8.3.5, pluggy-1.5.0
    rootdir: /home/ansible/dev/nautobot-secrets-reader
    configfile: pyproject.toml
    plugins: anyio-4.9.0, pylama-8.4.1
>>>>>>> develop
    collected 4 items
    
    nautobot_secrets_reader/tests/test_secread.py [32m.[0m[32m.[0m[32m.[0m[{'access_type': 'GENERIC',
      'secret_description': '',
      'secret_id': 'f5194ff8-5ffb-4b0e-a77f-ee7a9a3fd5e5',
      'secret_name': 'Test-Password-Path',
      'secret_provider': 'delinea-tss-path',
      'secret_type': 'PASSWORD',
      'value': 'FLD-PASSWORD'},
     {'access_type': 'GENERIC',
      'secret_description': '',
      'secret_id': 'f5194ff8-5ffb-4b0e-a77f-ee7a9a3fd5e5',
      'secret_name': 'Test-Password-Path',
      'secret_provider': 'delinea-tss-path',
      'secret_type': 'SECRET',
      'value': 'FLD-PASSWORD'},
     {'access_type': 'GENERIC',
      'secret_description': 'Username',
      'secret_id': '3f3a7832-fe45-46b3-93d5-eafbd97de565',
      'secret_name': 'TEST-User-ID',
      'secret_provider': 'delinea-tss-id',
      'secret_type': 'USERNAME',
      'value': 'FLD-Username'}]
    GENERIC: {'password': 'FLD-PASSWORD', 'secret': 'FLD-PASSWORD', 'username': 'FLD-Username'}
    [32m.[0m
    
<<<<<<< HEAD
    ============================== 4 passed in 3.42s ===============================
=======
    [32m============================== [32m[1m4 passed[0m[32m in 7.68s[0m[32m ===============================[0m


```
$ pytest nautobot_secrets_reader -s
================================================================================================================ test session starts =================================================================================================================
platform linux -- Python 3.12.9, pytest-8.3.5, pluggy-1.5.0
rootdir: /home/ansible/dev/nautobot-secrets-reader
configfile: pyproject.toml
plugins: anyio-4.9.0, pylama-8.4.1
collected 4 items                                                                                                                                                                                                                                    

nautobot_secrets_reader/tests/test_secread.py ...[{'access_type': 'GENERIC',
  'secret_description': '',
  'secret_id': 'f5194ff8-5ffb-4b0e-a77f-ee7a9a3fd5e5',
  'secret_name': 'Test-Password-Path',
  'secret_provider': 'delinea-tss-path',
  'secret_type': 'PASSWORD',
  'value': 'FLD-PASSWORD'},
 {'access_type': 'GENERIC',
  'secret_description': '',
  'secret_id': 'f5194ff8-5ffb-4b0e-a77f-ee7a9a3fd5e5',
  'secret_name': 'Test-Password-Path',
  'secret_provider': 'delinea-tss-path',
  'secret_type': 'SECRET',
  'value': 'FLD-PASSWORD'},
 {'access_type': 'GENERIC',
  'secret_description': 'Username',
  'secret_id': '3f3a7832-fe45-46b3-93d5-eafbd97de565',
  'secret_name': 'TEST-User-ID',
  'secret_provider': 'delinea-tss-id',
  'secret_type': 'USERNAME',
  'value': 'FLD-Username'}]
GENERIC: {'password': 'FLD-PASSWORD', 'secret': 'FLD-PASSWORD', 'username': 'FLD-Username'}
.

================================================================================================================= 4 passed in 8.08s ==================================================================================================================
```

```python
!jupyter nbconvert --to markdown --output README.md --TemplateExporter.exclude_input_prompt=True --TemplateExporter.exclude_output_prompt=True README.ipynb 

```

    [NbConvertApp] Converting notebook README.ipynb to markdown
    [NbConvertApp] Writing 10785 bytes to README.md
>>>>>>> develop

