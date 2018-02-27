#   Licensed under the Apache License, Version 2.0 (the "License"); you may
#   not use this file except in compliance with the License. You may obtain
#   a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#   License for the specific language governing permissions and limitations
#   under the License.
#

"""Network action implementations"""

from osc_lib.command import command
from osc_lib import utils

from openstackclient.i18n import _
from openstackclient.identity import common as identity_common
from openstackclient.network import common
from openstackclient.network import sdk_utils
from openstackclient.network.v2 import _tag


def _get_attrs_network(client_manager, parsed_args):
    attrs = {}
    if parsed_args.name is not None:
        attrs['name'] = str(parsed_args.name)
    if parsed_args.enable:
        attrs['admin_state_up'] = True
    if parsed_args.disable:
        attrs['admin_state_up'] = False
    if parsed_args.share:
        attrs['shared'] = True
    if parsed_args.no_share:
        attrs['shared'] = False
    if parsed_args.enable_port_security:
        attrs['port_security_enabled'] = True
    if parsed_args.disable_port_security:
        attrs['port_security_enabled'] = False

    # "network set" command doesn't support setting project.
    if 'project' in parsed_args and parsed_args.project is not None:
        identity_client = client_manager.identity
        project_id = identity_common.find_project(
            identity_client,
            parsed_args.project,
            parsed_args.project_domain,
        ).id
        # TODO(dtroyer): Remove tenant_id when we clean up the SDK refactor
        attrs['tenant_id'] = project_id

    # "network set" command doesn't support setting availability zone hints.
    if 'availability_zone_hints' in parsed_args and \
       parsed_args.availability_zone_hints is not None:
        attrs['availability_zone_hints'] = parsed_args.availability_zone_hints

    # set description
    if parsed_args.description:
        attrs['description'] = parsed_args.description

    # update_external_network_options
    if parsed_args.internal:
        attrs['router:external'] = False
    if parsed_args.external:
        attrs['router:external'] = True
    if parsed_args.no_default:
        attrs['is_default'] = False
    if parsed_args.default:
        attrs['is_default'] = True
    # Update Provider network options
    if parsed_args.provider_network_type:
        attrs['provider:network_type'] = parsed_args.provider_network_type
    if parsed_args.physical_network:
        attrs['provider:physical_network'] = parsed_args.physical_network
    if parsed_args.segmentation_id:
        attrs['provider:segmentation_id'] = parsed_args.segmentation_id
    if parsed_args.qos_policy is not None:
        network_client = client_manager.network
        _qos_policy = network_client.find_qos_policy(parsed_args.qos_policy,
                                                     ignore_missing=False)
        attrs['qos_policy_id'] = _qos_policy.id
    if 'no_qos_policy' in parsed_args and parsed_args.no_qos_policy:
        attrs['qos_policy_id'] = None
    return attrs


# TODO(sindhu): Use the SDK resource mapped attribute names once the
# OSC minimum requirements include SDK 1.0.
class CliCreateProvider(command.Command):
    _description = _("Create new network")

    def get_parser(self, prog_name):
        parser = super(CliCreateProvider, self).get_parser(prog_name)
        parser.add_argument(
            'name',
            metavar='<name>',
            help=_("New network name")
        )
        share_group = parser.add_mutually_exclusive_group()
        share_group.add_argument(
            '--share',
            action='store_true',
            default=None,
            help=_("Share the network between projects")
        )
        share_group.add_argument(
            '--no-share',
            action='store_true',
            help=_("Do not share the network between projects")
        )
        admin_group = parser.add_mutually_exclusive_group()
        admin_group.add_argument(
            '--enable',
            action='store_true',
            default=True,
            help=_("Enable network (default)")
        )
        admin_group.add_argument(
            '--disable',
            action='store_true',
            help=_("Disable network")
        )
        parser.add_argument(
            '--project',
            metavar='<project>',
            help=_("Owner's project (name or ID)")
        )
        parser.add_argument(
            '--description',
            metavar='<description>',
            help=_("Set network description")
        )
        identity_common.add_project_domain_option_to_parser(parser)
        parser.add_argument(
            '--availability-zone-hint',
            action='append',
            dest='availability_zone_hints',
            metavar='<availability-zone>',
            help=_("Availability Zone in which to create this network "
                   "(Network Availability Zone extension required, "
                   "repeat option to set multiple availability zones)")
        )
        port_security_group = parser.add_mutually_exclusive_group()
        port_security_group.add_argument(
            '--enable-port-security',
            action='store_true',
            help=_("Enable port security by default for ports created on "
                   "this network (default)")
        )
        port_security_group.add_argument(
            '--disable-port-security',
            action='store_true',
            help=_("Disable port security by default for ports created on "
                   "this network")
        )
        external_router_grp = parser.add_mutually_exclusive_group()
        external_router_grp.add_argument(
            '--external',
            action='store_true',
            help=_("Set this network as an external network "
                   "(external-net extension required)")
        )
        external_router_grp.add_argument(
            '--internal',
            action='store_true',
            help=_("Set this network as an internal network (default)")
        )
        default_router_grp = parser.add_mutually_exclusive_group()
        default_router_grp.add_argument(
            '--default',
            action='store_true',
            help=_("Specify if this network should be used as "
                   "the default external network")
        )
        default_router_grp.add_argument(
            '--no-default',
            action='store_true',
            help=_("Do not use the network as the default external network "
                   "(default)")
        )
        parser.add_argument(
            '--qos-policy',
            metavar='<qos-policy>',
            help=_("QoS policy to attach to this network (name or ID)")
        )
        vlan_transparent_grp = parser.add_mutually_exclusive_group()
        vlan_transparent_grp.add_argument(
            '--transparent-vlan',
            action='store_true',
            help=_("Make the network VLAN transparent"))
        vlan_transparent_grp.add_argument(
            '--no-transparent-vlan',
            action='store_true',
            help=_("Do not make the network VLAN transparent"))

        _tag.add_tag_option_to_parser_for_create(parser, _('network'))
        parser.add_argument(
            '--provider-network-type',
            metavar='<provider-network-type>',
            help=_("The physical mechanism by which the virtual network "
                   "is implemented. For example: "
                   "flat, geneve, gre, local, vlan, vxlan."))
        parser.add_argument(
            '--provider-physical-network',
            metavar='<provider-physical-network>',
            dest='physical_network',
            help=_("Name of the physical network over which the virtual "
                   "network is implemented"))
        parser.add_argument(
            '--provider-segment',
            metavar='<provider-segment>',
            dest='segmentation_id',
            help=_("VLAN ID for VLAN networks or Tunnel ID for "
                   "GENEVE/GRE/VXLAN networks"))
        return parser

    def take_action(self, parsed_args):
        attrs = _get_attrs_network(self.app.client_manager, parsed_args)
        if parsed_args.transparent_vlan:
            attrs['vlan_transparent'] = True
        if parsed_args.no_transparent_vlan:
            attrs['vlan_transparent'] = False

        client = self.app.client_manager.network
        obj = client.create_network(**attrs)


