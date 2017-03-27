# Cybera OSC Plugin

This is a `python-openstackclient` plugin that adds subcommands specific to clouds used at Cybera.

## Installation

```shell
$ python setup.py develop
```

This is best done in a virtualenv with the rest of the `python-openstack` dependencies.

## Usage

Just use it like any other `openstack` command:

```shell
$ openstack cybera server list
```

## Adding a command

1. Go to the `cybera_osc/cybera_osc/v1` directory.
2. Copy an existing command to a new file.
3. Rename `CliOLDNAME` with `CliNEWNAME`
4. Edit `__init__.py` and import the new file.
5. Edit `cybera_osc/setup.cfg` and add the new command.
