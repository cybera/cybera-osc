import json
import logging
import six
import sys

from osc_lib.command import command
from osc_lib import utils

from openstackclient.i18n import _

LOG = logging.getLogger(__name__)

class CliSubnetList(command.Command):
    _description = _("List Subnets")

    def get_parser(self, prog_name):
        parser = super(CliSubnetList, self).get_parser(prog_name)
        parser.add_argument(
            '--project',
            metavar='<project>',
            help=_('Show subnets from project')
        )
        parser.add_argument(
            '--name',
            metavar='<name>',
            help=_('Filter subnets by a name')
        )
        return parser

    def take_action(self, parsed_args):
        projects = getattr(parsed_args, 'project', [])

        args = {}
        args['project_id'] = parsed_args.project
        args['name'] = parsed_args.name
        network_client = self.app.client_manager.network
        data = network_client.subnets(**args)
        subnets = []
        for s in data:
            subnets.append(s.to_dict())
        print json.dumps(subnets)
