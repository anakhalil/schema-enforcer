# Schema Enforcer

Schema Enforcer provides a framework for testing structured data against schema definitions. Right now, [JSONSchema](https://json-schema.org/understanding-json-schema/index.html) is the only schema definition language supported, but we intend to add YANG models and other schema definition languages at some point in the future.

## Getting Started

### Install

Schema Enforcer is a python library which is available on PyPi. It requires a python version of 3.7 or greater. Once a supported version of python is installed on your machine, pip can be used to install the tool by using the command `python -m pip install schema-enforcer`.

```cli
bash$ python --version
Python 3.7.9

bash$ pip --version
pip 20.1.1 from /usr/local/lib/python3.7/site-packages/pip (python 3.7)

python -m pip install schema-enforcer
```

> Note: To determine the version of python your system is using, the command `python --version` can be run from a terminal emulator

> Note: Pip is a package manager for python. While most recent versions of python come with pip installed, some do not. You can determine if pip is installed on your system using the command `pip --version`. If it is not, the instructions for installing it, once python has been installed, can be found [here](https://pip.pypa.io/en/stable/installing/)

### Overview

Schema Enforcer requires that two different elements be defined by the user:

- Schema Definition Files: These are files which define the schema to which a given set of data should adhere.
- Structured Data Files: These are files which contain data that should adhere to the schema defined in one (or multiple) of the schema definition files

When `schema-enforcer` runs, it assumes directory hierarchy which should be in place from the folder in which the tool is run.

- `schema-enforcer` will search for **schema definition files** nested inside of `./schema/schemas/` which end in `.yml`, `.yaml`, or `.json`.
- `schema-enforcer` will do a recursive search for **structured data files** starting in the current working diretory (`./`). It does this by searching all directories (including the current working directory) for files ending in `.yml`, `.yaml`, or `.json`. The `schema` folder and it's subdirectories are excluded from this search by default.

```cli
bash$ cd examples/example1
bash$ tree
.
├── chi-beijing-rt1
│   ├── dns.yml
│   └── syslog.yml
├── eng-london-rt1
│   ├── dns.yml
│   └── ntp.yml
└── schema
    └── schemas
        ├── dns.yml
        ├── ntp.yml
        └── syslog.yml

4 directories, 7 files
```

In the above example, `chi-beijing-rt1` is a directory with structured data files containing some configuration for a router named `chi-beijing-rt1`. There are two structured data files inside of this folder, `dns.yml` and `syslog.yml`. Similarly, the `eng-london-rt1` directory contains definition files for a router named `eng-london-rt1`, `dns.yml` and `ntp.yml`.

The file chi-beijing-rt1/dns.yml defines the DNS servers chi-beijing.rt1 should use. The data in this file includes a simple hash-type data structure with a key of "dns_servers" and a value of an array. Each element in this array is a hash-type object with a key of `address` and a value which is the string of an IP address.

```cli
bash$ cat chi-beijing-rt1/dns.yml                    
---
dns_servers:
  - address: "10.1.1.1"
  - address: "10.2.2.2"
```

The file `schema/schemas/dns.yml` is a schema definition file. It contains a schema definition for ntp servers writtin in JSONSchema. The data in `chi-beijing-rt1/dns.yml` and `eng-london-rt1/dns.yml` should adhere to the schema defined in this schema definition file.

```cli
bash$ cat schema/schemas/dns.yml
---
$schema: "http://json-schema.org/draft-07/schema#"
$id: "schemas/dns_servers"
description: "DNS Server Configuration schema."
type: "object"
properties:
  dns_servers:
    type: "array"
    items:
      type: "object"
      properties:
        name:
          type: "string"
        address:
          type: "string"
          format: "ipv4"
        vrf:
          type: "string"
      required:
        - "address"
      uniqueItems: true
required:
  - "dns_servers"
```

> Note: The cat of the schema definitil file may be a little scary if you haven't seen JSONSchema before. Don't worry too much if it is difficult to parse right now. The important thing to note is that this file contains a schema definition to which the structured data in the files `chi-beijing-rt1/dns.yml` and `eng-london-rt1/dns.yml` should adhere.

### Basic usage

Once schema-enforcer has been installed, the `schema-enforcer validate` command can be used run schema validations of YAML/JSON instance files against the defined schema.

```cli
bash$ schema-enforcer --help
Usage: schema-enforcer [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  ansible        Validate the hostvar for all hosts within an Ansible...
  schema         Manage your schemas
  validate       Validates instance files against defined schema
```

To run the schema validations, the command `schema-enforcer validate` can be run.

```cli
bash$ schema-enforcer validate
test-schema validate            
ALL SCHEMA VALIDATION CHECKS PASSED
```

To acquire more context regarding what files specifically passed schema validation, the `--show-pass` flag can be passed in.

```
PASS [FILE] ./eng-london-rt1/ntp.yml
PASS [FILE] ./eng-london-rt1/dns.yml
PASS [FILE] ./chi-beijing-rt1/syslog.yml
PASS [FILE] ./chi-beijing-rt1/dns.yml
ALL SCHEMA VALIDATION CHECKS PASSED
```

If we modify one of the addresses in the `chi-beijing-rt1/dns.yml` files so that it's value is the boolean true instead of an IP address string, then run the `schema-enforcer tool`, the validation will fail with an error message.

```cli
bash$ cat chi-beijing-rt1/dns.yml                    
---
dns_servers:
  - address: true
  - address: "10.2.2.2"
bash$ test-schema validate            
FAIL | [ERROR] True is not of type 'string' [FILE] ./chi-beijing-rt1/dns.yml [PROPERTY] dns_servers:0:address
```

### Where To Go Next

More detailed documentation can be found inside of README.md files inside of the `docs/` directory.
- [Using a pyproject.toml file for configuration](https://github.com/networktocode-llc/jsonschema_testing/tree/master/docs/configuration.md)
- [Mapping Structured Data Files to Schema Files](https://github.com/networktocode-llc/jsonschema_testing/tree/master/docs/mapping_schemas.md)
- [The `validate` command](https://github.com/networktocode-llc/jsonschema_testing/tree/master/docs/validate_command.md)
- [The `schema` command](https://github.com/networktocode-llc/jsonschema_testing/tree/master/docs/schema_command.md)
- [The Ansible command](https://github.com/networktocode-llc/jsonschema_testing/tree/master/docs/ansible_command.md)


<!-- The below examples assume the following `pyproject.toml` file.

```yaml
[tool.jsonschema_testing]
schema_file_extension = ".json"

instance_file_extension = ".yml"

instance_search_directories = ["./"]

[tool.jsonschema_testing.schema_mapping]
# Map instance filename to schema filename
'dns.yml' = ['schemas/dns_servers', 'http://networktocode.com/schemas/core/base']
'syslog.yml' = ["schemas/syslog_servers"]
``` -->

<!-- #### json_schema_path

Description
***********

Defines the location of all JSON formatted schema files required to build schema definitions. The schema directory structure has subdirectories named `schemas` and `definitions`.

Example
*******

```shell
(.venv) $ ls schema/json/
definitions    schemas
```

#### yaml_schema_path

Description
***********
Defines the location of all YAML formatted schema files required to build schema definitions. The schema directory structure has subdirectories named `schemas` and `definitions`.


Example
*******

```shell
(.venv) $ ls schema/yaml/
definitions    schemas
```

#### json_schema_definitions

Description
***********
Defines the location of all JSON formatted schema definitions.

#### yaml_schema_definitions

Description
***********

Defines the location of all YAML formatted schema definitions.

#### json_full_schema_definitions

Description
***********

Defines the location to place schema definitions in after resolving all `$ref` objects. The schemas defined in **json_schema_definitions** are the authoritative source, but these can be expanded for visualization purposes (See `test-schema resolve-json-refs` below).

#### device_variables

Description
***********

Defines the directory where device variables are located. The directory structure expects subdirectories for each host and YAML files for defining variables per schema. The YAML files must use the `.yml` extension.

Example
*******

```shell
(.venv) $ ls hostvars/
csr1    csr2    eos1    junos1
(.venv) $ ls hostvars/csr1/
ntp.yml   snmp.yml
```

#### inventory_path

Description
***********

Defines the path to Ansible Inventory. This supports Ansible Inventory Practices.

Example
*******

```shell
(.venv) $ ls inventory/
hosts    group_vars/    host_vars/
(.venv) $ ls inventory/group_vars/
all.yml    ios.yml    eos.yml    nyc.yml
```

## Using Invoke


### Defining Schemas

The Schemas can be defined in YAML or JSON, and test-schema CLI tool can be used to replicate between formats. The conversion will overwrite any existing destination format files, but they do not currently remove files that have been deleted.  

Args
****

#### json_schema_path (str)

The path to JSON schema directories. The default is `json_schema_path` defined in the `pyproject.toml` file.

#### yaml_schema_path (str)

The path ot YAML schema directories. The default is `yaml_schema_path` defined in the `pyproject.toml` file.

#### Example

Environment
***********

```shell
(.venv) $ ls schema/yaml/schemas
ntp.yml    snmp.yml

(.venv) $ ls schema/json/schemas
ntp.json   vty.json

(.venv) $ cat schema/yaml/schemas/ntp.yml
---
$schema: "http://json-schema.org/draft-07/schema#"
$id: "schemas/ntp"
description: "NTP Configuration schema."
type: "object"
properties:
  ntp_servers:
    $ref: "../definitions/arrays/ip.json#ipv4_hosts"
  authentication:
    type: "boolean"
  logging:
    type: "boolean"
required: ["ntp_servers"]

(.venv) $ cat schema/json/schemas/ntp.yml
{
    "$schema": "http://json-schema.org/draft-07/schema#",
    "description": "NTP Configuration schema.",
    "type": "object",
    "properties": {
        "ntp_servers": {
            "$ref": "../definitions/arrays/ip.json#ipv4_hosts"
        }
    },
    "required": [
        "ntp_servers"
    ]
}
(.venv) $ 
```

The above environment has the following differences:

* The `schema/yaml/schemas` directory does not have the `vty` schema defined in `schema/json/schemas/`
* The `schema/yaml/schemas` directory has schema defined for `snmp` that is not defined in `schema/json/schemas`
* The YAML version of the `ntp` schema has 2 additional properties defined compared ot the JSON version

Converting Schema between formats
************

The CLI command `test-schema convert-yaml-to-json` or `test-schema convert-json-to-yaml` can be used to perform the conversion from your desired source format to the destination format. -->
<!-- 
### Resolving JSON Refs

The JSON Reference specification provides a mechanism for JSON Objects to incorporate reusable fragments defined outside of its own structure. This is done using the `$ref` key, and a value defining the URI to reach the resource definition.

```json
{
    "servers": {
        "$ref": "definitions/arrays/hosts.json#servers"
    }
}
```

The CLI tool can be used to resolve these JSON References used in the project's schema definitions. The resulting expanded Schema Definition will be written to a file. This only works for schemas defined in JSON, so you must use the `test-schema convert-yaml-to-json` method first if your primary source is the schema written in YAML.

Args
****

#### json_schema_path (str)

The path to JSONSchema definintions in JSON format. The defualt is `json_schema_definitions` defined in the `pyproject.toml` file.

#### output_path (str)

The path to write the resulting schema definitions to. The default is `json_full_schema_definitions` defined in the `pyproject.toml` file.

#### Example

Schema References
***********

```shell
(.venv) $ cat schema/json/schemas/ntp.json
{
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id": "schemas/ntp",
    "description": "NTP Configuration schema.",
    "type": "object",
    "properties": {
        "ntp_servers": {
            "$ref": "../definitions/arrays/ip.json#ipv4_hosts"
        }
    },
    "required": [
        "ntp_servers"
    ]
}
(.venv) $ cat schema/json/definitinos/arrays/ip.json
{
    "definitions": {
        "ipv4_hosts": {
            "type": "array",
            "items": {
                "$ref": "../objects/ip.json#ipv4_host"
            },
            "uniqueItems": true
        }
    }
}
(.venv) $ cat schema/json/definitions/objects/ip.json
{
    "definitions": {
        "ipv4_network": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string"
                },
                "network": {
                    "$ref": "../properties/ip.json#ipv4_address"
                },
                "mask": {
                    "$ref": "../properties/ip.json#ipv4_cidr"
                },
                "vrf": {
                    "type": "string"
                }
            },
            "required": [
                "network",
                "mask"
            ]
        }
    }
}
(.venv) $ cat schema/json/definitions/properties/ip.json
{
    "ipv4_address": {
        "type": "string",
        "format": "ipv4"
    },
    "ipv4_cidr": {
        "type": "number",
        "minimum": 0,
        "maximum": 32
    }
}
(.venv) $ 
```

The above environment has the following References:

* `schemas/ntp.json` has ntp_servers which references `"../definitions/arrays/ip.json#ipv4_hosts`
* `definitions/arrays/ip.json#ipv4_hosts` references `../objects/ip.json#ipv4_host` for the arrays items
* `definitions/objects/ip.json#ipv4_host` references both `ipv4_address` and `ipv4_mask` in `../properties/ip.json` -->
<!-- 
### Using test-schema command-line tool

To use the `test-schema` script, the pyproject.toml file must have a tool.jsonschema_testing section that defines some of the required setup variables.  An example of this is in the example/ folder, and this is from where you can also directly run the `test-schema` cli for testing and development purposes.


CLick is used for the CLI tool, and full help is available for the commands and sub-options as follows:

e.g.
```
$ cd example/
$ test-schema --help
Usage: test-schema [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  convert-json-to-yaml       Reads JSON files and writes them to YAML files.
  convert-yaml-to-json       Reads YAML files and writes them to JSON files.
  generate-hostvars          Generates ansible variables and creates a file...
  generate-invalid-expected  Generates expected ValidationError data from...
  resolve-json-refs          Loads JSONSchema schema files, resolves...
  validate-schema            Validates instance files against defined
                             schema...

  view-validation-error      Generates ValidationError from invalid mock...

$ test-schema validate-schema --help
Usage: test-schema validate-schema [OPTIONS]

  Validates instance files against defined schema

  Args:     show_pass (bool): show successful schema validations
  show_checks (bool): show schemas which will be validated against each
  instance file

Options:
  --show-checks  Shows the schemas to be checked for each instance file
                 [default: False]

  --show-pass    Shows validation checks that passed  [default: False]
  --help         Show this message and exit.
  ```


### Validating Instance Data Against Schema

The CLI also provides a sub-command to validate instances against schema. The schema definitions used are pulled from **json_schema_definitions** defined in the `pyproject.toml` file. The network device data used is pulled from **device_variables** defined in the `pyproject.toml` file. 

```
$ test-schema validate-schema --help
Usage: test-schema validate-schema [OPTIONS]

  Validates instance files against defined schema

  Args:     show_pass (bool): show successful schema validations
  show_checks (bool): show schemas which will be validated against each
  instance file

Options:
  --show-checks  Shows the schemas to be checked for each instance file
                 [default: False]

  --show-pass    Shows validation checks that passed  [default: False]
  --help         Show this message and exit.


$ test-schema validate-schema --show-pass
PASS | [SCHEMA] dns_servers | [FILE] hostvars/eng-london-rt1/dns.yml
PASS | [SCHEMA] dns_servers | [FILE] hostvars/usa-lax-rt1/dns.yml
PASS | [SCHEMA] dns_servers | [FILE] hostvars/chi-beijing-rt1/dns.yml
PASS | [SCHEMA] dns_servers | [FILE] hostvars/mex-mxc-rt1/dns.yml
PASS | [SCHEMA] dns_servers | [FILE] hostvars/ger-berlin-rt1/dns.yml
PASS | [SCHEMA] dns_servers | [FILE] hostvars/usa-nyc-rt1/dns.yml
PASS | [SCHEMA] syslog_servers | [FILE] hostvars/usa-lax-rt1/syslog.yml
PASS | [SCHEMA] syslog_servers | [FILE] hostvars/chi-beijing-rt1/syslog.yml
PASS | [SCHEMA] syslog_servers | [FILE] hostvars/mex-mxc-rt1/syslog.yml
PASS | [SCHEMA] syslog_servers | [FILE] hostvars/usa-nyc-rt1/syslog.yml
ALL SCHEMA VALIDATION CHECKS PASSED
```

The --strict flag allows you to quickly override the additionalProperties attribute of schemas and check for any properties that are not defined in the schema:

```
$ test-schema validate-schema  --strict
FAIL | [ERROR] Additional properties are not allowed ('test_extra_item_property' was unexpected) [FILE] hostvars/fail-tests/ntp.yml [PROPERTY] ntp_servers:1 [SCHEMA] ntp.yml
FAIL | [ERROR] Additional properties are not allowed ('test_extra_property' was unexpected) [FILE] hostvars/fail-tests/ntp.yml [SCHEMA] ntp.yml
FAIL | [ERROR] Additional properties are not allowed ('test_extra_property' was unexpected) [FILE] hostvars/fail-tests/dns.yml [PROPERTY] dns_servers:1 [SCHEMA] dns.yml
```

In the above case, the ntp.yml contained "something: extra" as shown below:
```
---
ntp_servers:
  - address: "10.6.6.6"
    name: "ntp1"
  - address: "10.7.7.7"
    name: "ntp1"
    vrf: 123
    extra_item: else
ntp_authentication: False
ntp_logging: True
something: extra
```

-------------------

## Historic usage notes below, some items need to be reviewed/reimplemented in new CLI.
Passing the `--hosts` and `--schema` args resulted in only 4 tests running.

### Generating Host Vars

If the parent project is using Ansible, there is a Task that will build the inventory and write variable files based on the top-level Schema Properties.
This task uses the `ansible-inventory` command to get Ansible's view of the inventory.
The filenames will use the same name as the filename of the Schema definition.
Each file will contain the variable definitions for any top-level schema properties found in the Ansible inventory.

Args
****

#### output_path (str)

The path to store the variable files. The default root directory uses `device_variables` defined in the `pyproject.toml` file. Each host will have their own subdirectory from this value.

#### schema_path (str)

The path where the JSON formatted schema files are located.
The default uses `json_schema_definitions` defined in the `pyproject.toml` file.

#### inventory_path (str)

The path to Ansible Inventory.
The default uses `inventory_path` defined in the `pyproject.toml` file.

#### Example

Environment
***********

**ansible inventory**

```shell
ls inventory/
hosts.ini    group_vars/    host_vars/
```

**empty hostvars**

```shell
(.venv) $ ls hostvars/
(.venv) $
```

**schema definitions**

```
(.venv) $ ls schemas/json/schemas/
ntp.json    snmp.json
(.venv) $ less schemas/json/schemas/ntp.json
{
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id": "schemas/ntp",
    "description": "NTP Configuration schema.",
    "type": "object",
    "properties": {
        "ntp_servers": {
            "$ref": "../definitions/arrays/ip.json#ipv4_hosts"
        },
        "ntp_authentication": {
            "type": "boolean"
        },
        "ntp_logging": {
            "type": "boolean"
        }
    },
    "required": [
        "ntp_servers"
    ]
}
(.venv) $
```

Using Invoke
************

```shell
(.venv) $ invoke generate-hostvars -o hostvars/ -s schema/json/schemas
Generating var files for host1
-> ntp
-> snmp
Generating var files for host2
-> ntp
(.venv) $ ls hostvars/
host    host2
(.venv) $ ls hostvars/host1/
ntp.yml    snmp.yml
(.venv) $ ls hostvars/host2/
ntp.yml
(.venv) $ less hostvars/host1/ntp.yml
---
ntp_servers:
  - address: "10.1.1.1"
    vrf: "mgmt"
ntp_authentication: true
(.venv) $
```

In the above example, both hosts had directories created:

  * host1 had two files created since it defined variables for both schemas
  * host2 only had one file created since it did not define data matching the snmp schema

Looking at the variables for `host1/ntp.yml`, only two of the three top-level Properties were defined.


### Create Invalid Mock Exceptions

This task is a helper to creating test cases for validating the defined Schemas properly identify invalid data.
Python's JSONSchema implmentation only has a single Exception for failed validation.
In order to verify that invalid data is failing validation for the expected reason, the tests investigate the Exception's attributes against the expected failure reasons.
This task will dynamically load JSON files in the Invalid mock directory (see Testing below), and create corresponding files with the Exception's attributes.
These attributes are stored in a YAML file adjacent to the invalid data files.

This task has one required argument, `schema`, which is used to identify the schema file and mock directory to load files from, and where to store the attribute files.

This uses `json_schema_path` defined in the ``pyproject.toml`` file to look for Schema definitions.
The invalid mock data is expected to be in `tests/mocks/<schema>/invalid/`.
All JSON files in the invalid mock directory will be loaded and have corresponding attribute files created.

Args
****

#### schema (str)

The schema filename to load invalid mock data and test against the Schema in order to generate expected ValidationError attributes. This should not include any file extensions.

#### Example

Environment
***********

```shell
(.venv) $ ls tests/mocks/ntp/invalid/
invalid_format.json    invalid_ip.json
(.venv) $
```

Using Invoke
************

```shell
(.venv) $ python -m invoke create-invalid-expected -s ntp
Writing file to tests/mocks/ntp/invalid/invalid_format.yml
Writing file to tests/mocks/ntp/invalid/invalid_ip.yml
(.venv) $ ls tests/mocks/ntp/invalid/
invalid_format.json    invalid_format.yml    invalid_ip.json
invalid_ip.yml
(.venv) $ less invalid_ip.yml
---
message: "'10.1.1.1000' is not a 'ipv4'"
schema_path: "deque(['properties', 'ntp_servers', 'items', 'properties', 'address', 'format'])"
validator: "format"
validator_value: "ipv4"
(.venv) $
```

## Testing

This project provides 2 testing methodologies for schema validation using PyTest:
  * Validating that the Schema definitions validate and invalidate as expected
  * Validating data against the defined schema

The test files to use are:
  * jsonschema_testing/tests/test_schema_validation.py
  * jsonschema_testing/tests/tests_data_against_schema.py

The mock data for `test_schema_validation` should be placed in the parent project's directory, located in `tests/mocks/<schema>/`.

### Validating Schema Definitions

The schema validation tests will test that each defined schema has both valid and invalid test cases defined.
The tests expect JSON files defining mock data; these files can be named anything, but must use the `.json` extension.
In addition to the JSON files, the invalid tests also requires YAML files with the attributes from the expected ValidationError.
The filenames of the YAML files must match the names used by the JSON files.

#### Example

Environment
***********

**valid test cases**

```shell
(.venv) $ ls tests/mocks/
ntp    snmp
(.venv) $ ls tests/mocks/ntp/valid/
full_implementation.json    partial_implementation.json
(.venv) $ less tests/mocks/ntp/valid/full_implementation.json
{
    "ntp_servers": [
        {
            "name": "ntp-east",
            "address": "10.1.1.1"
        },
        {
            "name": "ntp-west",
            "address": "10.2.1.1",
            "vrf": "mgmt"
        }
    ],
    "authentication": false,
    "logging": true
}
(.venv) $
```

**invalid test cases**

```shell
(.venv) $ ls tests/mocks/
(.venv) $ ls tests/mocks/ntp/invalid/
invalid_ip.json    invalid_ip.yml
(.venv) $ less tests/mocks/ntp/invalid/invalid_ip.json
{
    "ntp_servers": [
        {
            "name": "ntp-east",
            "address": "10.1.1.1000"
        }
    ]
}
(.venv) $ less tests/mocks/ntp/invalid/invalid_ip.yml
---
message: "'10.1.1.1000' is not a 'ipv4'"
schema_path: "deque(['properties', 'ntp_servers', 'items', 'properties', 'address', 'format'])"
validator: "format"
validator_value: "ipv4"
(.venv) $
```

Using Pytest
************

```shell
(.venv) $ pytest tests/test_schema_validation.py 
============================= test session starts ==============================
platform linux -- Python 3.7.5, pytest-5.3.2, py-1.8.0, pluggy-0.13.1
collected 6 items                                                             

tests/test_schema_validation.py ......                                    [100%]
(.venv) $
```


### Validating Data Against Schema

> The Invoke `validate` task provides a wrapper for this test.

The data validation test validates that inventory data conforms to the defined Schemas.
Each host must have its variable data stored in its own directory, and each YAML file inside the directory must use the same filename as the Schema definition file, and use the `.yml` extension.
Only variables defined in the corresponding Schema definition file will be validated.
Having additional variables defined will not cause an issue, but those variables will not be validated.
Any host that does not have data defined for the Schema will be silently ignored for that Schema validation check.

#### Optional Vars

##### Schema (list)

The list of Schemas to validate against. Passing multiple schemas is done by passing multiple schema flags: `--schema=ntp --schema=dns`.
The default will use all Schemas defined in `json_schema_definitions` in the ``pyproject.toml`` file.

##### hostvars (str)

The directory where all hosts define their variable data. The default uses `device_variables` defined in the ``pyproject.toml`` file.

##### hosts (list)

The list of hosts that should have data validated against the Schema. This variable is used by passing a single host flag with a comma separated string of hosts: `--hosts=host1,host2`.
The default will use all the directory names from the directories under the `hostvars` option.

#### Example

Environment
***********

**schemas**

```shell
(.venv) $ ls schema/json/schemas/
ntp.json    snmp.json
(.venv) $ less schema/json/schemas/ntp.json
{
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id": "schemas/ntp",
    "description": "NTP Configuration schema.",
    "type": "object",
    "properties": {
        "ntp_servers": {
            "$ref": "../definitions/arrays/ip.json#ipv4_hosts"
        },
        "ntp_authentication": {
            "type": "boolean"
        },
        "ntp_logging": {
            "type": "boolean"
        }
    },
    "required": [
        "ntp_servers"
    ]
}
(.venv) $
```

**hostvars**
```shell
(.venv) $ ls hostvars/
host1    host2    host3
(.venv) $ ls hostvars/host1/
ntp.yml    snmp.yml
(.venv) $ ls hostvars/host2/
ntp.yml
(.venv) $ less hostvars/host1/ntp.yml
---
ntp_servers:
  - address: "10.1.1.1"
    vrf: "mgmt"
ntp_authentication: true
(.venv) $
```

Using Pytest
************

```shell
(.venv) $ pytest tests/test_data_against_schema.py --hosts=host1,host2
============================= test session starts ==============================
platform linux -- Python 3.7.5, pytest-5.3.2, py-1.8.0, pluggy-0.13.1
collected 3 items                                                             

tests/test_schema_validation.py ...                                       [100%]
(.venv) $
``` -->
