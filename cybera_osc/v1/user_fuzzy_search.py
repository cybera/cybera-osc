import cybera_utils
import logging
import sys

from osc_lib.command import command
from openstackclient.i18n import _

LOG = logging.getLogger(__name__)
class CliUserFuzzySearch(command.Command):
    _description = _("Search for a user based on rough input")

    def get_parser(self, prog_name):
        p = super(CliUserFuzzySearch, self).get_parser(prog_name)
        p.add_argument(
            '--user',
            metavar='<user>',
            required=True,
            help=_('The user to search for'),
        )
        return p

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity
        user_id = cybera_utils.user_fuzzy_search(identity_client, parsed_args.user)
        sys.stdout.write(user_id)
        sys.stdout.flush()
