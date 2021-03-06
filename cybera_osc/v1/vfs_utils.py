import cybera_utils
import json
import time

import xml.etree.ElementTree as ET
from xml.dom.minidom import parseString
from passlib.hash import md5_crypt

import requests

from osc_lib import utils

def get_vfs_projects(identity_client):
    projects = []

    projects_list = identity_client.projects.list()
    for project in projects_list:
        if "-vfs" in project.name.lower():
            projects.append(project)

    return projects

def get_firewall_class(firewall_type):
    if firewall_type.lower() == "panos":
        return PANOS()
    elif firewall_type.lower() == "fortios":
        return Fortigate()
    elif firewall_type.lower() == "ubuntu":
        return Ubuntu()

    raise Exception('Unidentified firewall type')

class BaseFirewall:
    def get_stack(self, heat_client, name=None):
        stack_name = "cybera_virtual_firewall"
        if name is not None:
            stack_name = name

        filters = {
            'stack_name': stack_name,
        }

        res = heat_client.stacks.list(**filters)
        stacks = []
        for stack in res:
            stacks.append(stack)

        return stacks

    def destroy_instance(self, client_manager, name):
        heat_client = client_manager.orchestration
        stacks = self.get_stack(heat_client, name)
        if len(stacks) == 0:
            raise Exception("No stacks found")

        if len(stacks) > 1:
            raise Exception("More than 1 stack found")

        stack = stacks[0]

        heat_client.stacks.delete(stack.id)

        destroyed = False
        for _ in range(60):
            stacks = self.get_stack(heat_client, name)
            if len(stacks) == 0:
                destroyed = True
                break
            time.sleep(10)

        if not destroyed:
            raise Exception("Instance was not cleanly destroyed")


class PANOS(BaseFirewall):
    def launch_instance(self, client_manager, bootstrap, password, name):
        object_client = client_manager.object_store
        heat_client = client_manager.orchestration

        container_name = "CyberaVFS"
        if name is not None:
            container_name = "%s/%s" % (container_name, name)

        hot = cybera_utils.get_object(object_client, container_name, "hot.panos.yaml")
        env = cybera_utils.get_object(object_client, container_name, "env.panos.yaml")
        initcfg = cybera_utils.get_object(object_client, container_name, "init-cfg.txt").replace('\n', '\\n').strip()

        try:
            if bootstrap is None:
                bootstrap = cybera_utils.get_object(object_client, container_name, "bootstrap.xml")
            else:
                bootstrap = cybera_utils.get_object(object_client, container_name, bootstrap)
        except:
            raise Exception("bootstrap.xml not found")

        if password is not None:
            bootstrap = self.inject_phash(password, bootstrap)

        bootstrap = bootstrap.replace('"', "'").replace('\n', '\\n').strip()

        tpl = hot
        tpl = tpl.replace('%INITCFG%', initcfg)
        tpl = tpl.replace('%BOOTSTRAP%', bootstrap)

        v = ""
        authcodes = cybera_utils.get_object(object_client, container_name, "authcodes")
        if len(authcodes) != 0:
            authcodes = authcodes.replace('\n', '\\n').strip()
            v = '/license/authcodes: "%s"' % (authcodes)
        tpl = tpl.replace('%AUTHCODES%', v)

        stack_name = "cybera_virtual_firewall"
        if name is not None:
            stack_name = name

        fields = {
            'environment': env,
            'template': tpl,
            'stack_name': stack_name,
            'timeout_mins': 10,
        }

        heat_client.stacks.create(**fields)['stack']

        time.sleep(2)

        created = False
        for _ in range(60):
            stacks = self.get_stack(heat_client, name)
            if len(stacks) == 1:
                stack = stacks[0]
                if stack.stack_status == 'CREATE_COMPLETE':
                    created = True
                    break
                if stack.stack_status == 'CREATE_FAILED':
                    break
            time.sleep(10)

        if not created:
            raise Exception("Unable to create instance")


    def inject_phash(self, password, bootstrap):
        """
        After the user creates a password for CyberaVFS-api-account it will need to be
        injected into bootstrap.xml
        """
        root = ET.fromstring(bootstrap)
        phash = root.find("./mgt-config/users/entry[@name='CyberaVFS-api-account']/phash")

        if phash is None:
            user = ET.fromstring('<entry name="CyberaVFS-api-account"><permissions><role-based><superuser>yes</superuser></role-based></permissions><phash></phash></entry>')
            users = root.find("./mgt-config/users")
            users.append(user)
            phash = root.find("./mgt-config/users/entry[@name='CyberaVFS-api-account']/phash")

        phash.text = md5_crypt.hash(password)
        return ET.tostring(root)

    #def recover_instance(request, backup_id, deact_key, password):
    #    bootstrap = swift.swift_get_object(request, "CyberaVFS", backup_id).data.read()
    #    delicense_instance(request, deact_key, password)
    #    destroy_instance(request)
    #    launch_instance(request, bootstrap)

    def create_backup(self, client_manager, uuid, username, password, description):
        compute_client = client_manager.compute
        object_client = client_manager.object

        config = self.get_running_config(client_manager, uuid, username, password)
        object_name = datetime.now().strftime("backup-%Y-%m-%d-%H:%M%S.xml")
        headers = {}
        headers['X-Object-Meta-Description'] = description
        cybera_utils.put_object(object_client, "CyberaVFS/backups", object_name, config, headers)

    def get_running_config(self, client_manager, uuid, username, password):
        compute_client = client_manager.compute

        addr = cybera_utils.get_ipv4_address(compute_client, uuid)
        apikey = self.get_panos_api_key(client_manager, uuid, username, password)
        resp = requests.get("https://%s//api/?type=export&category=configuration&key=%s" % (addr, apikey), verify=False)
        resp.raise_for_status()
        return resp.text

    def get_panos_api_key(self, client_manager, uuid, username, password):
        compute_client = client_manager.compute

        addr = cybera_utils.get_ipv4_address(compute_client, uuid)
        r = requests.get("https://%s/api/?type=keygen&user=%s&password=%s" % (addr, username, password), verify=False)
        r.raise_for_status()
        x = parseString(r.text)
        apikey = x.getElementsByTagName('key')[0].childNodes[0].nodeValue
        return apikey

class Fortigate(BaseFirewall):
    def launch_instance(self, client_manager, bootstrap, password, name):
        if password is None:
            raise Exception('Password is required')

        object_client = client_manager.object_store
        heat_client = client_manager.orchestration

        container_name = "CyberaVFS"
        if name is not None:
            container_name = "%s/%s" % (container_name, name)

        hot = cybera_utils.get_object(object_client, container_name, "hot.fortios.yaml")
        env = cybera_utils.get_object(object_client, container_name, "env.fortios.yaml")

        tpl = hot
        tpl = tpl.replace('%PASSWORD%', password)

        v = ""
        license = cybera_utils.get_object(object_client, container_name, "license")
        if len(license) != 0:
            license_lines = license.split('\n')
            license_lines.insert(0, 'license: |')
            first_line = True
            for l in license_lines:
                if not first_line:
                    spaces = len(l)+18
                    l = l.rjust(spaces)
                first_line = False
                v += l + '\n'
        tpl = tpl.replace('%LICENSE%', v)

        stack_name = "cybera_virtual_firewall"
        if name is not None:
            stack_name = name

        fields = {
            'environment': env,
            'template': tpl,
            'stack_name': stack_name,
            'timeout_mins': 10,
        }

        heat_client.stacks.create(**fields)['stack']

        time.sleep(2)

        created = False
        for _ in range(60):
            stacks = self.get_stack(heat_client, name)
            if len(stacks) == 1:
                stack = stacks[0]
                if stack.stack_status == 'CREATE_COMPLETE':
                    created = True
                    break
                if stack.stack_status == 'CREATE_FAILED':
                    break
            time.sleep(10)

        if not created:
            raise Exception("Unable to create instance")

    def create_backup(self, client_manager, uuid, username, password, description):
        pass

    def get_running_config(self, client_manager, uuid, username, password):
        pass

    def get_api_key(self, client_manager, uuid, username, password):
        pass

class Ubuntu(BaseFirewall):
    def launch_instance(self, client_manager, bootstrap, password, name):
        object_client = client_manager.object_store
        heat_client = client_manager.orchestration

        container_name = "CyberaVFS"
        if name is not None:
            container_name = "%s/%s" % (container_name, name)

        hot = cybera_utils.get_object(object_client, container_name, "hot.fortios.yaml")
        env = cybera_utils.get_object(object_client, container_name, "env.fortios.yaml")

        if password is None:
            raise Exception('Password is required')

        tpl = hot
        tpl = tpl.replace('%PASSWORD%', password)

        stack_name = "cybera_virtual_firewall"
        if name is not None:
            stack_name = name

        fields = {
            'environment': env,
            'template': tpl,
            'stack_name': stack_name,
            'timeout_mins': 10,
        }

        heat_client.stacks.create(**fields)['stack']

        time.sleep(2)

        created = False
        for _ in range(60):
            stacks = self.get_stack(heat_client, name)
            if len(stacks) == 1:
                stack = stacks[0]
                if stack.stack_status == 'CREATE_COMPLETE':
                    created = True
                    break
                if stack.stack_status == 'CREATE_FAILED':
                    break
            time.sleep(10)

        if not created:
            raise Exception("Unable to create instance")

    def create_backup(self, client_manager, uuid, username, password, description):
        pass

    def get_running_config(self, client_manager, uuid, username, password):
        pass

    def get_api_key(self, client_manager, uuid, username, password):
        pass
