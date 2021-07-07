import logging
import os
import cybera_utils
import json

from osc_lib.command import command
from osc_lib import utils

from openstackclient.i18n import _
from openstackclient.identity import common as identity_common
from openstackclient.compute.v2 import server

LOG = logging.getLogger(__name__)

class CliVFSClearVLANFirewalls(command.Command):
    _description = _("List VFS firewalls with clear VLAN property set")

    def get_parser(self, prog_name):
        parser = super(CliVFSClearVLANFirewalls, self).get_parser(prog_name)
        return parser

    def take_action(self, parsed_args):
        compute_client = self.app.client_manager.compute
        image_client = self.app.client_manager.image

        image_kwargs = {
            'filters': {
                'clear_vlans': 'true',
            },
        }

        image_ids = []
        images = image_client.images.list(**image_kwargs)
        for i in images:
            image_ids.append(i['id'])

        search_opts = {
            'all_tenants': True,
            'status': 'ACTIVE',
        }
        servers = compute_client.servers.list(search_opts=search_opts)

        results = []
        for s in servers:
            if s.image is not None and s.image != "" and s.image['id'] in image_ids:
                results.append({
                    'id': s.id,
                    'host': getattr(s, 'OS-EXT-SRV-ATTR:hypervisor_hostname'),
                })

        print(json.dumps(results))
