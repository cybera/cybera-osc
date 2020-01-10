import StringIO
import logging
import os

from osc_lib.command import command
from osc_lib import utils
from six.moves import urllib

def project_fuzzy_search(identity_client, project_name=""):
    # First do a get to see if the exact id matches
    try:
        project = identity_client.projects.get(project_name)
        return project.id
    except:
        pass

    # If not found, query for all projects and do a fuzzy-search
    projects_list = identity_client.projects.list()
    found = fuzzy_search(project_name, projects_list)

    if found is None:
        return None

    if len(found) > 1:
        raise Exception("More than one project found")
    if len(found) == 0:
        raise Exception("No project found")

    return found[0]

def project_search(identity_client, project_name=""):
    # First do a get to see if the exact id matches
    try:
        project = identity_client.projects.get(project_name)
        return project.id
    except:
        pass

    # If not found, query for all projects and do a search
    projects_list = identity_client.projects.list()
    found = search(project_name, projects_list)

    if found is None:
        return None

    if len(found) > 1:
        raise Exception("More than one project found")
    if len(found) == 0:
        raise Exception("No project found")

    return found[0]

def user_fuzzy_search(identity_client, username=""):
    # First do a get to see if the exact id matches
    try:
        user = identity_client.users.get(username)
        return user.id
    except:
        pass

    # If not found, query for all users and do a fuzzy-search
    users_list = identity_client.users.list()
    found = fuzzy_search(username, users_list)

    if found is None:
        return None

    if len(found) > 1:
        raise Exception("More than one user found")
    if len(found) == 0:
        raise Exception("No user found")

    return found[0]

def user_search(identity_client, username=""):
    # First do a get to see if the exact id matches
    try:
        user = identity_client.users.get(username)
        return user.id
    except:
        pass

    # If not found, query for all users and do a search
    users_list = identity_client.users.list()
    found = search(username, users_list)

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

def image_search(image_client, image_name=""):
    image_list = list(image_client.images.list())
    found = search(image_name, image_list)

    if found is None:
        return None

    if len(found) > 1:
        raise Exception("More than one image found")
    if len(found) == 0:
        raise Exception("No image found")

    return found[0]

def flavor_fuzzy_search(compute_client, flavor_name=""):
    flavor_list = list(compute_client.flavors.list())
    found = fuzzy_search(flavor_name, flavor_list)

    if found is None:
        return None

    if len(found) > 1:
        raise Exception("More than one flavor found")
    if len(found) == 0:
        raise Exception("No flavor found")

    return found[0]

def flavor_search(compute_client, flavor_name=""):
    flavor_list = list(compute_client.flavors.list())
    found = search(flavor_name, flavor_list)

    if found is None:
        return None

    if len(found) > 1:
        raise Exception("More than one flavor found")
    if len(found) == 0:
        raise Exception("No flavor found")

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

def search(search_string, search_list):
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

    return found

def get_image(image_client, uuid):
    return utils.find_resource(image_client.images, uuid)

def get_latest_image(image_client, image_name):
    kwargs = {}
    kwargs['filters'] = {
        'name': image_name,
        'sort_key': 'created_at',
        'sort_dir': 'desc',
    }
    image_list = list(image_client.images.list(**kwargs))

    return image_list

def get_object(object_client, container, object):
    content = StringIO.StringIO()
    response = object_client._request(
        'GET',
        '%s/%s' % (urllib.parse.quote(container),
                   urllib.parse.quote(object)),
        stream=True,
    )

    if response.status_code == 200:
        for chunk in response.iter_content(64 * 1024):
            content.write(chunk)

    return content.getvalue()

def put_object(object_client, container_name, object_name, contents, headers):
    full_url = "%s/%s" % (urllib.parse.quote(container_name),
                          urllib.parse.quote(object_name))
    object_client.create(full_url, method='PUT', data=contents, headers=headers)

def get_instance(compute_client, uuid):
    try:
        instance = utils.find_resource(compute_client.servers, uuid)
    except:
        instance = None

    return instance

def get_ipv4_address(compute_client, uuid):
    instance = get_instance(compute_client, uuid)
    if instance is None:
        return None

    for i in instance.addresses['default']:
        if i['version'] == 4:
            return i['addr']
