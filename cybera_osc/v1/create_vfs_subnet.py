import json
import logging

from cybera_utils import project_fuzzy_search
from openstackclient.identity import common as identity_common

from openstackclient.network import common
from openstackclient.network import sdk_utils
from openstackclient.network.v2 import _tag

from osc_lib import utils
from osc_lib.command import command
from openstackclient.i18n import _

LOG = logging.getLogger(__name__)

class CliCreateVFSSubnet(command.Command):
    _description = _("Create a Neutron subnet on behalf of a VFS project.")

    def get_parser(self, prog_name):
        p = super(CliCreateVFSSubnet, self).get_parser(prog_name)
        p.add_argument(
            'name',
            metavar='<name>',
            help=_('The name of the network.'),
        )
        p.add_argument(
            '--project',
            metavar='<project>',
            required=True,
            help=_('The project to create the subnet under.'),
        )
        p.add_argument(
            '--network',
            metavar='<network>',
            required=True,
            help=_('The network to attach the subnet to'),
        )
        p.add_argument(
            '--subnet_range',
            metavar='<subnet_range>',
            required=True,
            help=_('The CIDR of the subnet'),
        )
        p.add_argument(
            '--gateway',
            metavar='<gateway>',
            default='auto',
            help=_('The gateway of the subnet'),
        )
        return p

    def _get_attrs(self, client_manager, parsed_args):
        attrs = {}
        attrs['name'] = str(parsed_args.name)
        identity_client = client_manager.identity
        project_id = project_fuzzy_search(
                identity_client,
                parsed_args.project.strip()
        )
        attrs['project_id'] = project_id
        attrs['network_id'] = parsed_args.network
        attrs['cidr'] = parsed_args.subnet_range
        attrs['gateway'] = parsed_args.gateway
        attrs['no_dhcp'] = True
        attrs['ip_version'] = 4

        return attrs

    def take_action(self, parsed_args):
        attrs = self._get_attrs(self.app.client_manager, parsed_args)
        network_client = self.app.client_manager.network
        result = network_client.create_subnet(**attrs)
        print json.dumps(result.to_dict())
