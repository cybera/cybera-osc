import cybera_utils
import logging
import requests
import sys

from osc_lib.command import command
from openstackclient.i18n import _

LOG = logging.getLogger(__name__)
class CliFlavorFuzzySearch(command.Command):
    _description = _("Search for an flavor based on rough input")

    def get_parser(self, prog_name):
        i = super(CliFlavorFuzzySearch, self).get_parser(prog_name)
        i.add_argument(
            '--flavor',
            metavar='<flavor>',
            required=True,
            help=_('The flavor to search for'),
        )
        return i

    def take_action(self, parsed_args):
        compute_client = self.app.client_manager.compute
        flavor_id = cybera_utils.flavor_fuzzy_search(compute_client, parsed_args.flavor)
        sys.stdout.write(flavor_id)
        sys.stdout.flush()
