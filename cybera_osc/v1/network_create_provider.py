import json
import logging

from cybera_utils import project_search
from openstackclient.identity import common as identity_common

from openstackclient.network import common
from openstackclient.network import sdk_utils
from openstackclient.network.v2 import _tag

from osc_lib import utils
from osc_lib.command import command
from openstackclient.i18n import _

LOG = logging.getLogger(__name__)

class CliCreateProvider(command.Command):
    _description = _("Create a Neutron provider network on behalf of a project.")

    def get_parser(self, prog_name):
        p = super(CliCreateProvider, self).get_parser(prog_name)
        p.add_argument(
            'name',
            metavar='<name>',
            help=_('The name of the network.'),
        )
        p.add_argument(
            '--project',
            metavar='<project>',
            required=True,
            help=_('The project to own the network.'),
        )
        p.add_argument(
            '--description',
            metavar='<description>',
            required=True,
            help=_('Description'),
        )
        p.add_argument(
            '--provider_physical_network',
            metavar='<provider-physical-network>',
            dest='physical_network',
            help=_("Name of the physical network over which the virtual network is implemented")
        )
        p.add_argument(
            '--provider_network_type',
            metavar='<provider-network-type>',
            dest='provider_network_type',
            help=_("The physical mechanism by which the virtual network "
               "is implemented. For example: "
               "flat, geneve, gre, local, vlan, vxlan.")
        )
        p.add_argument(
            '--provider_segment',
            metavar='<provider-segment>',
            dest='segmentation_id',
            help=_("VLAN ID for VLAN networks or Tunnel ID for GENEVE/GRE/VXLAN networks")
        )
        identity_common.add_project_domain_option_to_parser(p)
        p.add_argument(
            '--availability-zone-hint',
            action='append',
            dest='availability_zone_hints',
            metavar='<availability-zone>',
            help=_("Availability Zone in which to create this network "
                   "(Network Availability Zone extension required, "
                   "repeat option to set multiple availability zones)")
        )
        p.add_argument(
            '--disable_port_security',
            action='store_true',
            help=_("Disable port security by default for ports created on "
                   "this network")
        )
        p.add_argument(
            '--external',
            action='store_true',
            help=_("Set this network as an external network "
                   "(external-net extension required)")
        )
        p.add_argument(
            '--no-share',
            action='store_true',
            help=_("Do not share the network between projects")
        )
        return p

    def _get_attrs(self, client_manager, parsed_args):
        attrs = {}
        if parsed_args.name is not None:
            attrs['name'] = str(parsed_args.name)
        if parsed_args.project:
            identity_client = client_manager.identity
            project_id = project_search(
                    identity_client,
                    parsed_args.project.strip()
            )
            attrs['project_id'] = project_id
        if parsed_args.description:
            attrs['description'] = parsed_args.description
        if parsed_args.provider_network_type:
            attrs['provider:network_type'] = parsed_args.provider_network_type
        if parsed_args.physical_network:
            attrs['provider:physical_network'] = parsed_args.physical_network
        if parsed_args.segmentation_id:
            attrs['provider:segmentation_id'] = parsed_args.segmentation_id
        if parsed_args.availability_zone_hints:
            attrs['availability_zone_hints'] = parsed_args.availability_zone_hints
        if parsed_args.external:
            attrs['router:external'] = False
        if parsed_args.disable_port_security:
            attrs['port_security_enabled'] = False
        if parsed_args.no_share:
            attrs['shared'] = False

        return attrs

    def take_action(self, parsed_args):
        attrs = self._get_attrs(self.app.client_manager, parsed_args)
        network_client = self.app.client_manager.network
        result = network_client.create_network(**attrs)
        print json.dumps(result.to_dict())
