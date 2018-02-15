import logging

from cybera_utils import project_fuzzy_search

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
            help=_('The project to share the image with.'),
        )
        p.add_argument(
            '--description',
            metavar='<description>',
            required=True,
            help=_('Description'),
        )
        p.add_argument(
            '--provider-physical-network',
            metavar='<provider-physical-network>',
            dest='physical_network',
            help=_("Name of the physical network over which the virtual network is implemented")
        )
        p.add_argument(
            '--provider-network-type',
            metavar='<provider-network-type>',
            help=_("The physical mechanism by which the virtual network "
               "is implemented. For example: "
               "flat, geneve, gre, local, vlan, vxlan.")
        )
        p.add_argument(
            '--provider-segment',
            metavar='<provider-segment>',
            dest='segmentation_id',
            help=_("VLAN ID for VLAN networks or Tunnel ID for GENEVE/GRE/VXLAN networks")
        )
        p.add_argument(
            '--disable-port-security',
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
        return p

    def _get_attrs(self, client_manager, parsed_args):
        attrs = {}
        if parsed_args.name is not None:
            attrs['name'] = str(parsed_args.name)
        if 'project' in parsed_args and parsed_args.project is not None:
            identity_client = client_manager.identity
            project_id = project_fuzzy_search(
                identity_client,
                parsed_args.project.strip()
            ).id
            attrs['project_id'] = project_id
        if parsed_args.description:
            attrs['description'] = parsed_args.description
        if parsed_args.provider_network_type:
            attrs['provider:network_type'] = parsed_args.provider_network_type
        if parsed_args.physical_network:
            attrs['provider:physical_network'] = parsed_args.physical_network
        if parsed_args.segmentation_id:
            attrs['provider:segmentation_id'] = parsed_args.segmentation_id
        if parsed_args.external:
            attrs['router:external'] = True
        if parsed_args.disable_port_security:
            attrs['port_security_enabled'] = False
        return attrs

    def take_action(self, parsed_args):
        attrs = _get_attrs(self.app.client_manager, parsed_args)

        identity_client = self.app.client_manager.identity
        network_client = self.app.client_manager.network

        project_id = project_fuzzy_search(identity_client, parsed_args.project.strip())

        network_client.create_network(**attrs)
