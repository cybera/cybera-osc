import json
import logging

from cybera_utils import image_search
from vfs_utils import get_vfs_projects

from osc_lib import utils
from osc_lib.command import command
from openstackclient.i18n import _

LOG = logging.getLogger(__name__)

class CliVFSUnshareImageFromAll(command.Command):
    _description = _("Unshares an image from all VFS projects")

    def get_parser(self, prog_name):
        p = super(CliVFSUnshareImageFromAll, self).get_parser(prog_name)
        p.add_argument(
            '--image',
            metavar='<image>',
            required=True,
            help=_('The image to unsuare from all VFS projects'),
        )
        return p

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity
        image_client = self.app.client_manager.image

        image_id = image_search(image_client, parsed_args.image.strip())

        already_shared = []
        for image_member in image_client.image_members.list(image_id):
            already_shared.append(image_member.member_id)

        projects_removed = []
        for project_id in already_shared:
            image_client.image_members.delete(
                image_id,
                project_id,
            )
            projects_removed.append(project_id)

        print(json.dumps(projects_removed))
