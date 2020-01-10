import logging
import json

from cybera_utils import project_search
from cybera_utils import user_search

from osc_lib.command import command
from openstackclient.i18n import _

LOG = logging.getLogger(__name__)

class CliUserRoleList(command.Command):
    _description = _("List the roles a user has in a project")

    def get_parser(self, prog_name):
        p = super(CliUserRoleList, self).get_parser(prog_name)
        p.add_argument(
            '--user',
            metavar='<user>',
            required=True,
            help=_('The user to query'),
        )
        p.add_argument(
            '--project',
            metavar='<project>',
            required=True,
            help=_('The project for the user'),
        )
        return p

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity
        user = user_search(identity_client, parsed_args.user.strip())
        project = project_search(identity_client, parsed_args.project.strip())

        base_url = "/role_assignments?user.id=%s&scope.project.id=%s" % (user, project)
        resp, body = identity_client.get(base_url)
        del body['links']

        roles = []
        for r in body['role_assignments']:
            roles.append(r['role']['id'])

        print json.dumps(roles)
