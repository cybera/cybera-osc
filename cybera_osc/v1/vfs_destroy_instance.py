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
        return p

    def take_action(self, parsed_args):
        panos = vfs_utils.PANOS()
        stack = panos.destroy_instance(self.app.client_manager)
