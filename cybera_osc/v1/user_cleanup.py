import logging
import os
import cybera_utils

from osc_lib.command import command
from openstackclient.i18n import _

LOG = logging.getLogger(__name__)
class CliUserCleanup(command.Command):
    _description = _("Cleanup user account")

    def get_parser(self, prog_name):
        parser = super(CliUserCleanup, self).get_parser(prog_name)
        parser.add_argument(
            '--noop',
            action='store_true',
            default=False,
            help=_('No-operation test mode')
        )
        parser.add_argument(
            '--user',
            metavar='<user>',
            required=True,
            help=_('User to cleanup')
        )
        parser.add_argument(
            '--project',
            metavar='<project>',
            required=True,
            help=_('Only clean specified project')
        )
        return parser

    def take_action(self, parsed_args):
        compute_client = self.app.client_manager.compute
        identity_client = self.app.client_manager.identity
        image_client = self.app.client_manager.image
        object_client = self.app.client_manager.object_store
        volume_client = self.app.client_manager.volume

        userid = cybera_utils.user_fuzzy_search(identity_client, parsed_args.user)
        projectid = cybera_utils.project_fuzzy_search(identity_client, parsed_args.project)

        projects = identity_client.users.list(tenant_id=projectid)
        if len(projects) > 0:
            LOG.warn("Project has more than one user: %s" % parsed_args.project)

        if not parsed_args.noop:
            LOG.warn("Disabling user account: %s" % parsed_args.user)
            #identity_client.users.update(userid, {'enabled': False})
        else:
            LOG.warn("(noop) Disabling user account: %s" % parsed_args.user)

        search_opts = {
            'user_id': userid,
            'tenant_id': projectid,
            'all_tenants': True,
            'deleted': False,
        }
        servers = compute_client.servers.list(search_opts=search_opts)

        if len(servers) > 0:
            for server in servers:
                if not parsed_args.noop:
                    LOG.warn("Deleting server: %s (%s)" % (server.name, server.id))
                    #compute_client.servers.delete(server.id)
                else:
                    LOG.warn("(noop) Deleting server: %s (%s)" % (server.name, server.id))
        else:
            LOG.warn("No servers found")

        snapshots = volume_client.volume_snapshots.list(search_opts={'all_tenants': True})
        to_delete = []
        for s in snapshots:
            if s.project_id == projectid and s.user_id == userid:
                to_delete.append(s)
        if len(to_delete) > 0:
            for s in snapshots:
                if not parsed_args.noop:
                    LOG.warn("Deleting volume snapshot: %s (%s)" % (s.name, s.id))
                    #volume_client.snapshots.delete(s.id)
                else:
                    LOG.warn("(noop) Deleting volume snapshot: %s (%s)" % (s.name, s.id))
        else:
            LOG.warn("No snapshots found")

        search_opts = {
            'all_tenants': True,
            'project_id': projectid,
            'user_id': userid,
        }
        volumes = volume_client.volumes.list(search_opts=search_opts)
        if len(volumes) > 0:
            for v in volumes:
                if not parsed_args.noop:
                    LOG.warn("Deleting volume: %s (%s)" % (v.name, v.id))
                    #volume_client.volumes.delete(v.id)
                else:
                    LOG.warn("(noop) Deleting volume: %s (%s)" % (v.name, v.id))
        else:
            LOG.warn("No volumes found")
