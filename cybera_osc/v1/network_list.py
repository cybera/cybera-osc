import json
import logging
import six
import sys

from osc_lib.command import command
from osc_lib import utils

from openstackclient.i18n import _

from openstackclient.network import common
from openstackclient.network.v2 import network

LOG = logging.getLogger(__name__)

class CliNetworkList(command.Command):
    _description = _("List Networks")

    def get_parser(self, prog_name):
        parser = super(CliNetworkList, self).get_parser(prog_name)
        parser.add_argument(
            '--project',
            metavar='<project>',
            nargs="+",
            help=_('Show networks from project')
        )
        return parser

    def take_action(self, parsed_args):
        projects = getattr(parsed_args, 'project', [])

        if len(projects) == 1:
            args = {}
            args['project_id'] = projects[0]
            network_client = self.app.client_manager.network
            data = network_client.networks(**args)
            networks = []
            for s in data:
                networks.append(s.to_dict())
            print json.dumps(networks)
