import cybera_utils
import json

import xml.etree.ElementTree as ET
from xml.dom.minidom import parseString
from passlib.hash import md5_crypt

import requests

from osc_lib import utils

class PANOS:
    def __init__(self):
        return

    def launch_instance(self, client_manager, bootstrap, password):
        object_client = client_manager.object_store
        heat_client = client_manager.orchestration

        hot = cybera_utils.get_object(object_client, "CyberaVFS", "hot.panos.yaml")
        env = cybera_utils.get_object(object_client, "CyberaVFS", "env.panos.yaml")
        initcfg = cybera_utils.get_object(object_client, "CyberaVFS", "init-cfg.txt").replace('\n', '\\n').strip()
        authcodes = cybera_utils.get_object(object_client, "CyberaVFS", "authcodes").replace('\n', '\\n').strip()

        try:
            if bootstrap is None:
                bootstrap = cybera_utils.get_object(object_client, "CyberaVFS", "bootstrap.xml")
            else:
                bootstrap = cybera_utils.get_object(object_client, "CyberaVFS", bootstrap)
        except:
            raise Exception("bootstrap.xml not found")

        if password is not None:
            bootstrap = self.inject_phash(password, bootstrap)

        bootstrap = bootstrap.replace('"', "'").replace('\n', '\\n').strip()

        tpl = hot
        tpl = tpl.replace('%INITCFG%', initcfg)
        tpl = tpl.replace('%BOOTSTRAP%', bootstrap)
        tpl = tpl.replace('%AUTHCODES%', authcodes)

        fields = {
            'environment': env,
            'template': tpl,
            'stack_name': 'cybera_virtual_firewall',
            'timeout_mins': 10,
        }

        stack = heat_client.stacks.create(**fields)['stack']
        return json.dumps(stack)

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
