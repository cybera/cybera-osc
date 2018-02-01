import cybera_utils
import logging
import requests
import sys

from osc_lib.command import command
from openstackclient.i18n import _

LOG = logging.getLogger(__name__)
class CliImageFuzzySearch(command.Command):
    _description = _("Search for an image based on rough input")

    def get_parser(self, prog_name):
        i = super(CliImageFuzzySearch, self).get_parser(prog_name)
        i.add_argument(
            '--image',
            metavar='<image>',
            required=True,
            help=_('The image to search for'),
        )
        return i

    def take_action(self, parsed_args):
        image_client = self.app.client_manager.image
        image_id = cybera_utils.image_fuzzy_search(image_client, parsed_args.image)
        sys.stdout.write(image_id)
        sys.stdout.flush()
