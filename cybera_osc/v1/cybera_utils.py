import logging
import os

from osc_lib.command import command
from osc_lib import utils

def project_fuzzy_search(identity_client, project_name=""):
    projects_list = identity_client.projects.list()
    found = fuzzy_search(project_name, projects_list)

    if found is None:
        return None

    if len(found) > 1:
        raise Exception("More than one project found")
    if len(found) == 0:
        raise Exception("No project found")

    return found[0]

def user_fuzzy_search(identity_client, username=""):
    users_list = identity_client.users.list()
    found = fuzzy_search(username, users_list)

    if found is None:
        return None

    if len(found) > 1:
        raise Exception("More than one user found")
    if len(found) == 0:
        raise Exception("No user found")

    return found[0]

def image_fuzzy_search(image_client, image_name=""):
    image_list = list(image_client.images.list())
    found = fuzzy_search(image_name, image_list)

    if found is None:
        return None

    if len(found) > 1:
        raise Exception("More than one image found")
    if len(found) == 0:
        raise Exception("No image found")

    return found[0]

def fuzzy_search(search_string, search_list):
    """ All objects in search_list must have name and id attributes """
    if search_string == "":
        return None

    found = []

    # Look for uuid match first
    match = False
    for x in search_list:
        if search_string.lower() == x.id.lower():
            found.append(x.id)
            match = True
            break

    # Look for exact name match
    if not match:
        for x in search_list:
            if search_string.lower() == x.name.lower():
                found.append(x.id)
                match = True
                break

    # Look for substring
    if not match:
        for x in search_list:
            if x.name.lower().find(search_string.lower()) != -1:
                found.append(x.id)

    return found
