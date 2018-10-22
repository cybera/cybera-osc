import cybera_utils
import logging
import json
import vfs_utils

from osc_lib import utils
from osc_lib.command import command
from openstackclient.i18n import _

LOG = logging.getLogger(__name__)
class CliVFSInstanceUpgradeable(command.Command):
    _description = _("Determine if a VFS instance can be upgraded")

    def get_parser(self, prog_name):
        p = super(CliVFSInstanceUpgradeable, self).get_parser(prog_name)
        p.add_argument(
            '--instance',
            metavar='<instance>',
            required=True,
            help=_('The instance to check'),
        )
        return p

    def take_action(self, parsed_args):
        compute_client = self.app.client_manager.compute
        image_client = self.app.client_manager.image

        try:
            instance = cybera_utils.get_instance(compute_client, parsed_args.instance)
            instance_image = cybera_utils.get_image(image_client, instance.image['id'])
            images = cybera_utils.get_latest_image(image_client, instance_image['name'])
        except:
            print False

        if len(images) == 0:
            print False

        image = images[0]
        print instance.image['id'] != image['id']
