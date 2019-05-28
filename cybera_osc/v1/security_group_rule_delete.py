import logging

from osc_lib.command import command
from openstackclient.i18n import _

LOG = logging.getLogger(__name__)
class CliSecurityGroupRuleDelete(command.Command):
    _description = _("Delete a security group rule")

    def get_parser(self, prog_name):
        parser = super(CliSecurityGroupRuleDelete, self).get_parser(prog_name)
        parser.add_argument(
            'rule_id',
            metavar='<rule_id>',
            help=_('ID to delete')
        )
        return parser

    def take_action(self, parsed_args):
        network_client = self.app.client_manager.network

        obj = network_client.find_security_group_rule(
            parsed_args.rule_id, ignore_missing=False)
        network_client.delete_security_group_rule(obj)
