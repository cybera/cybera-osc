import json
import logging
import six
import sys

from osc_lib.command import command
from osc_lib import utils

from openstackclient.i18n import _

LOG = logging.getLogger(__name__)

class CliNetworkList(command.Command):
    _description = _("List Networks")

    def get_parser(self, prog_name):
        parser = super(CliNetworkList, self).get_parser(prog_name)
        parser.add_argument(
            '--project',
            metavar='<project>',
            help=_('Show networks from project')
        )
        parser.add_argument(
            '--name',
            metavar='<name>',
            help=_('Filter networks by a name')
        )
        return parser

    def take_action(self, parsed_args):
        args = {}

        args['tenant_id'] = parsed_args.project
        args['project_id'] = parsed_args.project

        if parsed_args.name:
            args['name'] = parsed_args.name

        network_client = self.app.client_manager.network
        data = network_client.networks(**args)
        networks = []
        for s in data:
            networks.append(s.to_dict())
        print json.dumps(networks)
