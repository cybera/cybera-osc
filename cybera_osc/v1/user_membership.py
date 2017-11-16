import logging
import json

from osc_lib.command import command
from openstackclient.i18n import _

LOG = logging.getLogger(__name__)

class CliUserMembership(command.Command):
    _description = _("List projects a user belongs to")

    def get_parser(self, prog_name):
        p = super(CliUserMembership, self).get_parser(prog_name)
        p.add_argument(
            '--user',
            metavar='<user>',
            required=True,
            help=_('The user to query'),
        )
        return p

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity
        base_url = "/users/%s/projects" % parsed_args.user.strip()
        resp, body = identity_client.get(base_url)
        del body['links']

        projects = []
        for p in body['projects']:
            del p['links']
            projects.append(p)

        print json.dumps(projects)
