import cybera_utils
import json
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
        return p

    def take_action(self, parsed_args):
        panos = vfs_utils.PANOS()
        stack = panos.launch_instance(self.app.client_manager, parsed_args.bootstrap, parsed_args.password)

        print stack
