import json
import logging
import six
import sys

from osc_lib.command import command
from osc_lib import utils

from openstackclient.i18n import _

from openstackclient.network import common
from openstackclient.network.v2 import floating_ip

from keystoneauth1 import session
from keystoneauth1.identity import v3
from swiftclient import client as swc

LOG = logging.getLogger(__name__)

class CliJTTest(command.Command):
    _description = _("Test")

    def get_parser(self, prog_name):
        parser = super(CliJTTest, self).get_parser(prog_name)
        return parser

    def take_action(self, parsed_args):

        auth = self.app.client_manager.auth

	new_auth = v3.Password(auth_url=auth.auth_url + "/v3",
                   username=auth._username,
                   password=auth._password,
                   user_domain_name='Default',
                   project_id='9aa5f9f66b4b417d84d778a23acdf45b',
                   project_domain_name='Default')

        keystone_session = session.Session(auth=new_auth)
        conn = swc.Connection(session=keystone_session)
        resp_headers, containers = conn.get_account()
        for container in containers:
            print(container)

        sys.exit(0)

        #network_client = self.app.client_manager.network
        #params = {}
        #params["name"] = "jttest"
        #params["admin_state_up"] = True
        #params["tenant_id"] = "9aa5f9f66b4b417d84d778a23acdf45b"
        #obj = network_client.create_network(**params)
        #print json.dumps(obj)
