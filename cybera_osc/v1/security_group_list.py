import logging
import cybera_utils
import json

from osc_lib.command import command
from openstackclient.i18n import _

LOG = logging.getLogger(__name__)
class CliSecurityGroupList(command.Command):
    _description = _("List Security Groups")

    def get_parser(self, prog_name):
        parser = super(CliSecurityGroupList, self).get_parser(prog_name)
        parser.add_argument(
            '--project',
            metavar='<project>',
            required=True,
            help=_('Project to Inventory')
        )
        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity
        network_client = self.app.client_manager.network

        artifacts = {}

        projectid = cybera_utils.project_search(identity_client, parsed_args.project.strip())

        artifacts['security_groups'] = {}
        filters = {}
        filters['project_id'] = projectid
        all_secgroups = network_client.security_groups(**filters)
        for sg in all_secgroups:
            sg_name = "%s: %s" % (sg.id, sg.name)
            artifacts['security_groups'][sg_name] = []

            filters['security_group_id'] = sg.id
            rules = network_client.security_group_rules(**filters)
            for rule in rules:
                artifacts['security_groups'][sg_name].append({
                    "id": rule.id,
                    "description": rule.description,
                    "direction": rule.direction,
                    "ethertype": rule.ether_type,
                    "protocol": rule.protocol,
                    "port_range_min": rule.port_range_min,
                    "port_range_max": rule.port_range_max,
                    "remote_ip_prefix": rule.remote_ip_prefix,
                    "remote_group_id": rule.remote_group_id,
                })


        print json.dumps(artifacts)
