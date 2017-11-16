import logging
import os

from osc_lib.command import command
from osc_lib import utils

from openstackclient.identity import common as identity_common

def project_fuzzy_search(identity_client, project_name=""):
    if project_name == "":
        return None

    projects_list = identity_client.projects.list()
    found = []

    # Look for uuid match first
    match = False
    for project in projects_list:
        if project_name.lower() == project.id.lower():
            found.append(project.id)
            match = True
            break

    # Look for exact name match
    if not match:
        for project in projects_list:
            if project_name.lower() == project.name.lower():
                found.append(project.id)
                match = True
                break

    # Look for substring
    if not match:
        for project in projects_list:
            if project.name.lower().find(project_name.lower()) != -1:
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

    # Look for uuid match first
    match = False
    for user in users_list:
        if username.lower() == user.id.lower():
            found.append(user.id)
            match = True
            break

    # Look for exact username match
    if not match:
        for user in users_list:
            if username.lower() == user.name.lower():
                match = True
                found.append(user.id)
                break

    # Look for substring match
    if not match:
        for user in users_list:
            if user.name.lower().find(username.lower()) != -1:
                found.append(user.id)

    if len(found) > 1:
        raise Exception("More than one user found")
    if len(found) == 0:
        raise Exception("No user found")

    return found[0]

