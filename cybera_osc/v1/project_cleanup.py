import logging
import os
import cybera_utils

from osc_lib.command import command
from openstackclient.i18n import _

LOG = logging.getLogger(__name__)
class CliProjectCleanup(command.Command):
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

        projectid = cybera_utils.project_fuzzy_search(identity_client, parsed_args.project)

        if not parsed_args.noop:
            LOG.warn("Disabling project: %s" % parsed_args.project)
            #identity_client.users.update(userid, {'enabled': False})
        else:
            LOG.warn("(noop) Disabling user account: %s" % parsed_args.project)

        all_secgroups = compute_client.security_groups.list(search_opts={'all_tenants': True})
        to_delete = []
        for sg in all_secgroups:
            if sg.tenant_id == projectid:
                to_delete.append(sg)
        print to_delete
        if len(to_delete) > 0:
            for sg in to_delete:
                if not parsed_args.noop:
                    LOG.warn("Deleting security group: %s (%s)" % (sg.name, sg.id))
                    #compute_client.security_groups.delete(sg.id)
                else:
                    LOG.warn("(noop) Deleting security group: %s (%s)" % (sg.name, sg.id))

        all_fip = compute_client.floating_ips_bulk.list()
        to_delete = []
        for fip in all_fip:
            if fip.project_id == projectid:
                to_delete.append(fip)
        if len(to_delete) > 0:
            for fip in to_delete:
                if not parsed_args.noop:
                    LOG.warn("Deleting floating ip: %s" % fip.address)
                    #compute_client.floating_ips.delete(fip.address)
                else:
                    LOG.warn("(noop) Deleting floating ip: %s" % fip.address)

        search_opts = {
            'private': True,
        }
        images = image_client.images.list(search_opts=search_opts)
        to_delete = []
        for i in images:
            if 'owner_id' in i and i['owner_id'] == projectid:
                to_delete.append(i)
            elif 'owner' in i and i['owner'] == projectid:
                to_delete.append(i)
        if len(to_delete) > 0:
            for i in to_delete:
                if not parsed_args.noop:
                    LOG.warn("Deleting image: %s (%s)" % (i.name, i.id))
                    #image_client.images.delete(i.id)
                else:
                    LOG.warn("(noop) Deleting image: %s (%s)" % (i.name, i.id))
