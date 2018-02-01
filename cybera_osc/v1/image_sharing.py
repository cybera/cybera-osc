import logging

from cybera_utils import project_fuzzy_search
from cybera_utils import image_fuzzy_search

from osc_lib import utils
from osc_lib.command import command
from openstackclient.i18n import _

LOG = logging.getLogger(__name__)

class CliImageSharing(command.Command):
    _description = _("Share an image between two projects.")

    def get_parser(self, prog_name):
        p = super(CliImageSharing, self).get_parser(prog_name)
        p.add_argument(
            '--project',
            metavar='<project>',
            required=True,
            help=_('The project to share the image with.'),
        )
        p.add_argument(
            '--image',
            metavar='<image>',
            required=True,
            help=_('The image to share.'),
        )
        return p

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity
        image_client = self.app.client_manager.image

        kwargs = {}
        image_id = image_fuzzy_search(image_client, parsed_args.image.strip())
        project_id = project_fuzzy_search(identity_client, parsed_args.project.strip())

        image_member = image_client.image_members.create(
            image_id,
            project_id,
        )
        image_client.image_members.update(
            image_id, project_id, 'accepted'
        )
