import logging
import os

from osc_lib.command import command
from osc_lib import utils

from openstackclient.identity import common as identity_common

def project_fuzzy_search(identity_client, project_name=""):
    if project_name == "":
        return None

    projects_list = identity_client.tenants.list()
    found = []
    for project in projects_list:
        if project.name.lower().find(project_name.lower()) != -1:
            found.append(project.id)
        if project_name.lower() == project.id.lower():
            found.append(project.id)

    if len(found) > 1:
        raise Exception("More than one project found")
    if len(found) == 0:
        raise Exception("No project found")

    return found[0]

def user_fuzzy_search(identity_client, username=""):
    if username == "":
        return None

    users_list = identity_client.users.list()
    found = []
    for user in users_list:
        if user.name.lower().find(username.lower()) != -1:
            found.append(user.id)
        if username.lower() == user.id.lower():
            found.append(user.id)

    if len(found) > 1:
        raise Exception("More than one user found")
    if len(found) == 0:
        raise Exception("No user found")

    return found[0]

