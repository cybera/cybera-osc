import cybera_utils
import logging
import requests
import sys

from osc_lib.command import command
from openstackclient.i18n import _

LOG = logging.getLogger(__name__)
class CliProjectFuzzySearch(command.Command):
    _description = _("Search for a project based on rough input")

    def get_parser(self, prog_name):
        p = super(CliProjectFuzzySearch, self).get_parser(prog_name)
        p.add_argument(
            '--project',
            metavar='<project>',
            required=True,
            help=_('The project to search for'),
        )
        return p

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity
        project_id = cybera_utils.project_fuzzy_search(identity_client, parsed_args.project)
        sys.stdout.write(project_id)
        sys.stdout.flush()
