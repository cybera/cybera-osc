import logging

from cybera_utils import project_fuzzy_search
from cybera_utils import image_fuzzy_search

from osc_lib import utils
from osc_lib.command import command
from openstackclient.i18n import _

LOG = logging.getLogger(__name__)

class CliImageUnshare(command.Command):
    _description = _("Revoke access to an image for a project.")

    def get_parser(self, prog_name):
        p = super(CliImageUnshare, self).get_parser(prog_name)
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

        image_id = image_fuzzy_search(image_client, parsed_args.image.strip())
        project_id = project_fuzzy_search(identity_client, parsed_args.project.strip())

        image_client.image_members.delete(
            image_id,
            project_id
        )
