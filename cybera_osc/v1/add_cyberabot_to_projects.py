import json
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
        member_role = utils.find_resource(identity_client.roles, 'Member')
        reseller_role = utils.find_resource(identity_client.roles, 'ResellerAdmin')
        cyberabot_user = utils.find_resource(identity_client.users, 'cyberabot')

        member_added_to = []
        reseller_added_to = []

        projects_list = self.app.client_manager.identity.projects.list(enabled=True)
        for project in projects_list:
            LOG.debug("Cybera: Checking for cyberabot membership in %s" % project.name)
            is_member = False
            is_reseller = False

            assignments = identity_client.role_assignments.list(
                user=cyberabot_user.id,
                project=project.id,
                include_names=True)

            for assignment in assignments:
                if assignment.role['name'] == 'Member':
                    is_member = True
                if assignment.role['name'] == 'ResellerAdmin':
                    is_reseller = True

            if not is_member:
                LOG.debug("Cybera: cyberabot is not a member of %s" % project.name)
                if not parsed_args.noop:
                    kwargs = {}
                    kwargs['user'] = cyberabot_user.id
                    kwargs['project'] = project.id
                    result = identity_client.roles.grant(member_role.id, **kwargs)

                    #result = identity_client.roles.add_user_role(
                    #        cyberabot_user.id,
                    #        member_role.id,
                    #        project.id,
                    #)
                member_added_to.append(project.name)
            if not is_reseller:
                LOG.debug("Cybera: cyberabot is not a reselleradmin of %s" % project.name)
                if not parsed_args.noop:
                    kwargs = {}
                    kwargs['user'] = cyberabot_user.id
                    kwargs['project'] = project.id
                    result = identity_client.roles.grant(reseller_role.id, **kwargs)

                    #result = identity_client.roles.add_user_role(
                    #        cyberabot_user.id,
                    #        reseller_role.id,
                    #        project.id,
                    #)
                reseller_added_to.append(project.name)

        pretty = ""
        if len(member_added_to) > 0:
            pretty = "cyberabot was added to the following projects as a Member:<br>"
            for p in member_added_to:
                pretty += "%s<br>" % p
            pretty += "<br>"
            pretty += "cyberabot was added to the following projects as a ResellerAdmin:<br>"
            for p in reseller_added_to:
                pretty += "%s<br>" % p
            pretty += "<br>"

        output = {}
        output['member_added_to'] = member_added_to
        output['reseller_added_to'] = reseller_added_to
        output['pretty']  = pretty
        print json.dumps(output)
