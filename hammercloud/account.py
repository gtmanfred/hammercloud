from __future__ import absolute_import
import json
import os
import pprint
import requests
import yaml

import logging
log = logging.getLogger(__name__)

IDENTITY = 'https://identity.api.rackspacecloud.com/v2.0'

try:
    import supernova.credentials
    HAS_SUPERNOVA = True
except ImportError as exc:
    HAS_SUPERNOVA = False


class BaseAccount(object):
    _config = None

    def __init__(self, username, tenantid, apikey, **kwargs):
        '''
        Authenticate and get users service catalog
        '''
        self.username = username
        self.tenantid = tenantid
        self.apikey = apikey
        self.sess = requests.Session()
        payload = {
            "auth": {
                "RAX-KSKEY:apiKeyCredentials": {
                    "username": username,
                    "apiKey": apikey
                },
                "tenantId": tenantid,
            }
        }

        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        self.service = self.sess.post(
            '{0}/tokens'.format(IDENTITY),
            data=json.dumps(payload),
            headers=headers,
            verify=False
        ).json()
        log.debug('Services: \n%s', pprint.pformat(self.service))
        self.catalog = self.service['access']['serviceCatalog']
        self.token = self.service['access']['token']['id']

    @classmethod
    def config(cls):
        if cls._config is None:
            with open(os.path.expanduser('~/.config/hammercloud/config.yml')) as configfile:
                cls._config = yaml.load(configfile).get('hammercloud', {})
        return cls._config

    def setup_keyring(self):
        '''
        Only used for the command line

        sets supernova temp keyring
        '''
        if not HAS_SUPERNOVA:
            return False
        snova = supernova.credentials
        env = 'temp'
        snova.password_set(env + ':OS_USERNAME', self.username)
        snova.password_set(env + ':OS_PASSWORD', self.api_key)
        snova.password_set(env + ':OS_REGION_NAME', self.region)
        snova.password_set(env + ':OS_TENANT_ID', str(self.tenantid))
