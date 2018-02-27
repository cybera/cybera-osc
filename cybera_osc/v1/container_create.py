import logging

from cybera_utils import project_fuzzy_search
from osc_lib.cli import parseractions
from osc_lib.command import command
from osc_lib import utils
import six

from openstackclient.i18n import _

from keystoneauth1 import session
from keystoneauth1.identity import v3
from swiftclient import client as swc

LOG = logging.getLogger(__name__)

class CliCreateContainer(command.Command):
    _description = _("Create new container")

    def get_parser(self, prog_name):
        parser = super(CliCreateContainer, self).get_parser(prog_name)
        parser.add_argument(
                '--project',
                metavar='<project>',
                required = True,
                help=_('Project to create container under.'),
        )
        parser.add_argument(
                'containers',
                metavar='<container-name>',
                nargs="+",
                help=_('New container name(s)'),
        )
        return parser

    def take_action(self, parsed_args):

        auth = self.app.client_manager.auth
        identity_client = self.app.client_manager.identity
        user_project = project_fuzzy_search(identity_client, parsed_args.project.strip())

	new_auth = v3.Password(auth_url=auth.auth_url + "/v3",
                   username=auth._username,
                   password=auth._password,
                   user_domain_name='Default',
                   project_id=user_project,
                   project_domain_name='Default')

        keystone_session = session.Session(auth=new_auth)
        conn = swc.Connection(session=keystone_session)

        results = []
        for container in parsed_args.containers:
            if len(container) > 256:
                LOG.warning(
                    _('Container name is %s characters long, the default limit'
                      ' is 256'), len(container))
            data = conn.put_container(container)
