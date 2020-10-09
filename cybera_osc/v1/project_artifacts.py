import logging
import cybera_utils
import json

from osc_lib.command import command
from openstackclient.i18n import _

LOG = logging.getLogger(__name__)
class CliProjectArtifacts(command.Command):
    _description = _("Inventory a project")

    def get_parser(self, prog_name):
        parser = super(CliProjectArtifacts, self).get_parser(prog_name)
        parser.add_argument(
            '--project',
            metavar='<project>',
            required=True,
            help=_('Project to Inventory')
        )
        return parser

    def take_action(self, parsed_args):
        compute_client = self.app.client_manager.compute
        identity_client = self.app.client_manager.identity
        image_client = self.app.client_manager.image
        object_client = self.app.client_manager.object_store
        volume_client = self.app.client_manager.volume
        network_client = self.app.client_manager.network

        artifacts = {}

        projectid = cybera_utils.project_fuzzy_search(identity_client, parsed_args.project.strip())
        artifacts['project_id'] = projectid

        artifacts['security_groups'] = []
        filters = {}
        filters['project_id'] = projectid
        all_secgroups = network_client.security_groups(**filters)
        for sg in all_secgroups:
            artifacts['security_groups'].append("%s: %s" % (sg.id, sg.name))

        artifacts['floating_ips'] = []
        all_fip = network_client.ips(**filters)
        for fip in all_fip:
            artifacts['floating_ips'].append("%s: %s" % (fip.id, fip.floating_ip_address))

        artifacts['images'] = []
        search_opts = {
            'private': True,
        }
        images = image_client.images.list(search_opts=search_opts)
        for i in images:
            if 'owner_id' in i and i['owner_id'] == projectid:
                artifacts['images'].append("%s: %s" % (i.id, i.name))
            elif 'owner' in i and i['owner'] == projectid:
                artifacts['images'].append("%s: %s" % (i.id, i.name))

        artifacts['instances'] = []
        search_opts = {
            'tenant_id': projectid,
            'all_tenants': True,
            'deleted': False,
            }
        servers = compute_client.servers.list(search_opts=search_opts)
        for server in servers:
            artifacts['instances'].append("%s: %s" % (server.id, server.name))

        artifacts['volumes'] = []
        search_opts = {
            'all_tenants': True,
            'project_id': projectid,
        }
        volumes = volume_client.volumes.list(search_opts=search_opts)
        for v in volumes:
            artifacts['volumes'].append("%s: %s" % (v.id, v.name))

        artifacts['volume_snapshots'] = []
        snapshots = volume_client.volume_snapshots.list(search_opts=search_opts)
        for s in snapshots:
            artifacts['volume_snapshots'].append("%s: %s" % (s.id, s.name))

        print json.dumps(artifacts)
