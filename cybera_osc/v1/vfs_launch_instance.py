import logging
import vfs_utils

from osc_lib import utils
from osc_lib.command import command
from openstackclient.i18n import _

LOG = logging.getLogger(__name__)
class CliVFSLaunchInstance(command.Command):
    _description = _("Launch a VFS instance from its Heat configuration")

    def get_parser(self, prog_name):
        p = super(CliVFSLaunchInstance, self).get_parser(prog_name)
        p.add_argument(
            '--bootstrap',
            metavar='<bootstrap>',
            help=_('Use a custom bootstrap file'),
        )
        p.add_argument(
            '--password',
            metavar='<password>',
            help=_('Initial firewall password'),
        )
        p.add_argument(
            '--name',
            metavar='<name>',
            help=_('Name of the firewall'),
        )
        p.add_argument(
            '--firewall-type',
            metavar='<firewall_type>',
            default="panos",
            help=_('Type of firewall (panos, fortinet, etc)'),
        )
        return p

    def take_action(self, parsed_args):
        panos = vfs_utils.PANOS()
        stack = panos.launch_instance(
                self.app.client_manager,
                bootstrap=parsed_args.bootstrap,
                password=parsed_args.password,
                name=parsed_args.name,
                firewall_type=parsed_args.firewall_type)
