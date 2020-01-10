import logging

from cybera_utils import project_search
from cybera_utils import user_search

from osc_lib import utils
from osc_lib.command import command
from openstackclient.i18n import _

LOG = logging.getLogger(__name__)

class CliProjectUserAdd(command.Command):
    _description = _("Add a user to a project via role assignment")

    def get_parser(self, prog_name):
        p = super(CliProjectUserAdd, self).get_parser(prog_name)
        p.add_argument(
            '--user',
            metavar='<user>',
            required=True,
            help=_('The user being added'),
        )
        p.add_argument(
            '--project',
            metavar='<project>',
            required=True,
            help=_('The the project to add the user to'),
        )
        p.add_argument(
            '--role',
            metavar='<role>',
            required=True,
            help=_('The the role to grant to the user'),
        )
        return p

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity

        role = utils.find_resource(
            identity_client.roles,
            parsed_args.role.strip()
        )

        kwargs = {}
        kwargs['user'] = user_search(identity_client, parsed_args.user.strip())
        kwargs['project'] = project_search(identity_client, parsed_args.project.strip())

        identity_client.roles.grant(role.id, **kwargs)
