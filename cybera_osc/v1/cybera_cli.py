import logging
import os

from osc_lib.command import command
from osc_lib import utils

from openstackclient.i18n import _
from openstackclient.identity import common as identity_common
from openstackclient.compute.v2 import server

LOG = logging.getLogger(__name__)

class CliAddCyberabotToProjects(command.Command):
    _description = _("Add cyberabot to projects")

    def get_parser(self, prog_name):
        parser = super(CliAddCyberabotToProjects, self).get_parser(prog_name)
        parser.add_argument(
            '--noop',
            action='store_true',
            default=False,
            help=_('No-operation test mode'),
        )
        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity
        member_role = utils.find_resource(identity_client.roles, '_member_')
        reseller_role = utils.find_resource(identity_client.roles, 'ResellerAdmin')
        cyberabot_user = utils.find_resource(identity_client.users, 'cyberabot')

        member_added_to = []
        reseller_added_to = []

        projects_list = self.app.client_manager.identity.tenants.list()
        for project in projects_list:
            LOG.debug("Cybera: Checking for cyberabot membership in %s" % project.name)
            is_member = False
            is_reseller = False
            assignments = identity_client.roles.roles_for_user(cyberabot_user.id, project.id)
            for assignment in assignments:
                if assignment.name == '_member_':
                    is_member = True
                if assignment.name == 'Member':
                    is_member = True
                if assignment.name == 'ResellerAdmin':
                    is_reseller = True

            if not is_member:
                LOG.debug("Cybera: cyberabot is not a member of %s" % project.name)
                if not parsed_args.noop:
                    result = identity_client.roles.add_user_role(
                            cyberabot_user.id,
                            member_role.id,
                            project.id,
                    )
                member_added_to.append(project.name)
            if not is_reseller:
                LOG.debug("Cybera: cyberabot is not a reselleradmin of %s" % project.name)
                if not parsed_args.noop:
                    result = identity_client.roles.add_user_role(
                            cyberabot_user.id,
                            member_role.id,
                            project.id,
                    )
                reseller_added_to.append(project.name)

        print("cyberabot was added to the following projects as a _member_:")
        for p in member_added_to:
            print(p)
        print("cyberabot was added to the following projects as a ResellerAdmin:")
        for p in reseller_added_to:
            print(p)


class CliServerList(command.Lister):
    _description = _("List servers")

    def get_parser(self, prog_name):
        parser = super(CliServerList, self).get_parser(prog_name)
        parser.add_argument(
            '--status',
            metavar='<status>',
            default='active',
            help=_('Search by server status'),
        )
        parser.add_argument(
            '--flavor',
            metavar='<flavor>',
            help=_('Search by flavor (name or ID)'),
        )
        parser.add_argument(
            '--image',
            metavar='<image>',
            help=_('Search by image (name or ID)'),
        )
        parser.add_argument(
            '--host',
            metavar='<hostname>',
            help=_('Search by hostname'),
        )
        parser.add_argument(
            '--all-projects',
            action='store_true',
            default=True,
            help=_('Include all projects (admin only)'),
        )
        parser.add_argument(
            '--project',
            metavar='<project>',
            help=_("Search by project (admin only) (name or ID)")
        )
        identity_common.add_project_domain_option_to_parser(parser)
        parser.add_argument(
            '--user',
            metavar='<user>',
            help=_('Search by user (admin only) (name or ID)'),
        )
        identity_common.add_user_domain_option_to_parser(parser)
        parser.add_argument(
            '--long',
            action='store_true',
            default=False,
            help=_('List additional fields in output'),
        )
        parser.add_argument(
            '--limit',
            metavar='<limit>',
            type=int,
            default=None,
            help=_("Maximum number of servers to display. If limit equals -1,"
                   " all servers will be displayed. If limit is greater than"
                   " 'osapi_max_limit' option of Nova API,"
                   " 'osapi_max_limit' will be used instead."),
        )
        return parser

    def take_action(self, parsed_args):
        compute_client = self.app.client_manager.compute
        identity_client = self.app.client_manager.identity

        project_id = None
        if parsed_args.project:
            project_id = identity_common.find_project(
                identity_client,
                parsed_args.project,
                parsed_args.project_domain,
            ).id
            parsed_args.all_projects = True

        user_id = None
        if parsed_args.user:
            user_id = identity_common.find_user(
                identity_client,
                parsed_args.user,
                parsed_args.user_domain,
            ).id

        # Nova only supports list servers searching by flavor ID. So if a
        # flavor name is given, map it to ID.
        flavor_id = None
        if parsed_args.flavor:
            flavor_id = utils.find_resource(compute_client.flavors,
                                            parsed_args.flavor).id

        # Nova only supports list servers searching by image ID. So if a
        # image name is given, map it to ID.
        image_id = None
        if parsed_args.image:
            image_id = utils.find_resource(compute_client.images,
                                           parsed_args.image).id

        search_opts = {
            'status': parsed_args.status,
            'flavor': flavor_id,
            'image': image_id,
            'host': parsed_args.host,
            'tenant_id': project_id,
            'all_tenants': parsed_args.all_projects,
            'user_id': user_id,
        }
        LOG.debug('search options: %s', search_opts)

	columns = (
	    'ID',
	    'Name',
	    'Project Name',
	    'User Name',
	    'Status',
	    'OS-EXT-STS:task_state',
	    'OS-EXT-STS:power_state',
	    'Networks',
	    'Image Name',
	    'Image ID',
	    'OS-EXT-SRV-ATTR:host',
	)
	column_headers = (
	    'ID',
	    'Name',
	    'Project Name',
	    'User Name',
	    'Status',
	    'Task State',
	    'Power State',
	    'Networks',
	    'Image Name',
	    'Image ID',
	    'Host',
	)
	mixed_case_fields = [
	    'OS-EXT-STS:task_state',
	    'OS-EXT-STS:power_state',
	    'OS-EXT-SRV-ATTR:host',
	]

        data = compute_client.servers.list(search_opts=search_opts)

        images = {}
        # Create a dict that maps image_id to image object.
        # Needed so that we can display the "Image Name" column.
        # "Image Name" is not crucial, so we swallow any exceptions.
        try:
            images_list = self.app.client_manager.image.images.list()
            for i in images_list:
                images[i.id] = i
        except Exception:
            pass

        projects = {}
        # Create a dict that maps project_id to project object.
        try:
            projects_list = self.app.client_manager.identity.tenants.list()
            for p in projects_list:
                projects[p.id] = p
        except Exception:
            pass

	users = {}
        try:
            users_list = self.app.client_manager.identity.users.list()
            for u in users_list:
                users[u.id] = u
        except Exception:
            pass

        # Create a dict that maps user_id to a user object
        # Populate image_name and image_id attributes of server objects
        # so that we can display "Image Name" and "Image ID" columns.
        for s in data:
            if 'id' in s.image:
                image = images.get(s.image['id'])
                if image:
                    s.image_name = image.name
                s.image_id = s.image['id']
            else:
                s.image_name = ''
                s.image_id = ''

            # Populate Project/Tenant name
            project = projects.get(s.tenant_id)
            if project:
                s.project_name = project.name
            else:
                s.project_name = s.tenant_id

	    # Populate User name
            user = users.get(s.user_id)
            if user:
                s.user_name = user.name
            else:
                s.user_name = s.user_id

        table = (column_headers,
                 (utils.get_item_properties(
                     s, columns,
                     mixed_case_fields=mixed_case_fields,
                     formatters={
                         'OS-EXT-STS:power_state':
                             server._format_servers_list_power_state,
                         'Networks': server._format_servers_list_networks,
                     },
                 ) for s in data))
        return table
