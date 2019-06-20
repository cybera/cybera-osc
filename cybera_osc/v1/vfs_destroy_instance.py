import logging
import vfs_utils

from osc_lib import utils
from osc_lib.command import command
from openstackclient.i18n import _

LOG = logging.getLogger(__name__)
class CliVFSDestroyInstance(command.Command):
    _description = _("Destroy a VFS instance from its Heat configuration")

    def get_parser(self, prog_name):
        p = super(CliVFSDestroyInstance, self).get_parser(prog_name)
        p.add_argument(
            '--name',
            metavar='<name>',
            help=_('Name of the firewall / Heat stack'),
        )
        p.add_argument(
            '--firewall-type',
            metavar='<firewall_type>',
            default="panos",
            help=_('Type of firewall (panos, fortinet, etc)'),
        )
        return p

    def take_action(self, parsed_args):
        firewall_class = vfs_utils.get_firewall_class(parsed_args.firewall_type)
        stack = firewall_class.destroy_instance(self.app.client_manager, parsed_args.name)
