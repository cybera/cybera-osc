import logging
import six

from osc_lib.command import command
from osc_lib import utils

from openstackclient.i18n import _

from openstackclient.network import common
from openstackclient.network.v2 import floating_ip
from openstack.network.v2 import floating_ip as _floating_ip

LOG = logging.getLogger(__name__)

class CliFloatingIPDelete(command.Command):
    _description = _("Delete a floating IP")

    def get_parser(self, prog_name):
        parser = super(CliFloatingIPDelete, self).get_parser(prog_name)
        parser.add_argument(
            'floating_ip',
            metavar='<floating-ip>',
            nargs="+",
            help=_('Floating IP(s) to delete (IP address or ID)')
        )
        return parser

    def take_action(self, parsed_args):
        resources = getattr(parsed_args, 'floating_ip', [])
        network_client = self.app.client_manager.network

        for r in resources:
            match = _floating_ip.FloatingIP.existing(id=r)
            network_client.delete_ip(match)
