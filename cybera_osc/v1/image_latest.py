import cybera_utils
import logging
import json

from osc_lib.command import command
from openstackclient.i18n import _

LOG = logging.getLogger(__name__)
class CliImageLatest(command.Command):
    _description = _("Return the latest image based on a name")

    def get_parser(self, prog_name):
        i = super(CliImageLatest, self).get_parser(prog_name)
        i.add_argument(
            '--image',
            metavar='<image>',
            required=True,
            help=_('The image to search for'),
        )
        return i

    def take_action(self, parsed_args):
        image_client = self.app.client_manager.image
        images = cybera_utils.get_latest_image(image_client, parsed_args.image)

        if len(images) > 0:
            print json.dumps(images[0])
            return

        print json.dumps([])
