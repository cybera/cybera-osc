import logging

from cybera_utils import image_search
from vfs_utils import get_vfs_projects

from osc_lib import utils
from osc_lib.command import command
from openstackclient.i18n import _

LOG = logging.getLogger(__name__)

class CliVFSShareImageToAll(command.Command):
    _description = _("Share an image with all VFS projects")

    def get_parser(self, prog_name):
        p = super(CliVFSShareImageToAll, self).get_parser(prog_name)
        p.add_argument(
            '--image',
            metavar='<image>',
            required=True,
            help=_('The image to share with all VFS projects'),
        )
        return p

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity
        image_client = self.app.client_manager.image

        image_id = image_search(image_client, parsed_args.image.strip())
        projects = get_vfs_projects(identity_client)
        if len(projects) == 0:
            raise Exception("No projects found")

        already_shared = []
        for image_member in image_client.image_members.list(image_id):
            already_shared.append(image_member.member_id)

        projects_added = []
        for project in projects:
            if project.id not in already_shared:
                image_client.image_members.create(
                    image_id,
                    project.id,
                )
                image_client.image_members.update(
                    image_id, project.id, 'accepted'
                )
                projects_added.append(project.name)

        print(projects_added)
