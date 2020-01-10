import logging

from cybera_utils import project_search
from osc_lib.cli import parseractions
from osc_lib.command import command
from osc_lib import exceptions
from osc_lib import utils
import six

from openstackclient.i18n import _

from keystoneauth1 import session
from keystoneauth1.identity import v3
from swiftclient import client as swc

LOG = logging.getLogger(__name__)

class CliCreateObject(command.Command):
    _description = _("Upload objects to container")

    def get_parser(self, prog_name):
        parser = super(CliCreateObject, self).get_parser(prog_name)
        parser.add_argument(
            '--project',
            metavar='<project>',
            required = True,
            help=_('Project to create container under.'),
        )
        parser.add_argument(
            '--name',
            metavar='<name>',
            help=_('Upload a file and rename it. '
                   'Can only be used when uploading a single object')
        )
        parser.add_argument(
            'container',
            metavar='<container>',
            help=_('Container for new objects'),
        )
        parser.add_argument(
            'objects',
            metavar='<filename>',
            nargs="+",
            help=_('Local filename(s) to upload'),
        )
        return parser

    def take_action(self, parsed_args):

        auth = self.app.client_manager.auth
        identity_client = self.app.client_manager.identity
        user_project = project_search(identity_client, parsed_args.project.strip())

	new_auth = v3.Password(auth_url=auth.auth_url + "/v3",
                   username=auth._username,
                   password=auth._password,
                   user_domain_name='Default',
                   project_id=user_project,
                   project_domain_name='Default')

        keystone_session = session.Session(auth=new_auth)
        conn = swc.Connection(session=keystone_session)

        if parsed_args.name:
	    if len(parsed_args.objects) > 1:
	        msg = _('Attempting to upload multiple objects and '
                        'using --name is not permitted')
                raise exceptions.CommandError(msg)

        for obj in parsed_args.objects:
            if len(obj) > 1024:
                LOG.warning(
                    _('Object name is %s characters long, the default limit'
                      ' is 1024'), len(obj))
            with open(obj, 'r') as content:
                data = conn.put_object(
                    parsed_args.container,
                    parsed_args.name,
                    content
            )
