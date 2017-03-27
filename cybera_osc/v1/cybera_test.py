import logging
import os
import cybera_utils

from osc_lib.command import command
from osc_lib import utils

from openstackclient.i18n import _

class CliTest(command.Command):
    _description = _("Test")

    def get_parser(self, prog_name):
        parser = super(CliTest, self).get_parser(prog_name)
        parser.add_argument(
            '--project',
            metavar='<project>',
            help=_('Project to search for')
        )
        return parser

    def take_action(self, parsed_args):
        print cybera_utils.user_fuzzy_search(self.app.client_manager, parsed_args.project)
