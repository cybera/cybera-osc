import json
import logging

from cybera_utils import project_search

from osc_lib.command import command

from openstackclient.i18n import _

LOG = logging.getLogger(__name__)

class CliFloatingIPList(command.Command):
    _description = _("Show a floating IP")

    def get_parser(self, prog_name):
        parser = super(CliFloatingIPList, self).get_parser(prog_name)
        parser.add_argument(
            '--project',
            metavar='<project>',
            help=_('List floating IPs owned by the project')
        )
        return parser

    def take_action(self, parsed_args):
        network_client = self.app.client_manager.network

        query = {}
        if parsed_args.project is not None:
            identity_client = self.app.client_manager.identity
            project_id = project_search(identity_client, parsed_args.project.strip())
            query['project_id'] = project_id
            query['tenant_id'] = project_id

        data = network_client.ips(**query)
        all_ips = []
        for d in data:
            all_ips.append(d.floating_ip_address)
        print(json.dumps(all_ips))
