# -*- coding: utf-8 -*-
'''
Module for interfacing with nova and getting information about servers
'''
from __future__ import absolute_import
import json
import time

from hammercloud.api import CloudAPI

import logging
log = logging.getLogger(__name__)

IDENTITY = 'https://identity.api.rackspacecloud.com/v2.0'


class HammerNova(CloudAPI):
    '''
    Nova api library for hammercloud
    '''
    def list_servers(self, region):
        '''
        list all servers in a region
        '''
        endpoint = self._get_endpoint(
            'compute',
            region,
            type_name='cloudServersOpenStack'
        )

        headers = {
            'X-Auth-Token': self.auth.token,
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

        return self.sess.get(
            '{0}/servers/detail'.format(endpoint),
            headers=headers,
            verify=False
        ).json()['servers']

    def get_server_by_region(self, value, region):
        '''
        get server from attribute in a region
        '''
        for server in self.list_servers(region):
            if value in server.values():
                return server
        return {}

    def find_server(self, server_attr):
        '''
        get server based on an attribute, from any region
        '''
        for region in ['ORD', 'DFW', 'IAD', 'SYD', 'LON', 'HKG']:
            try:
                ret = self.get_server_by_region(server_attr, region)
            except Exception:
                log.debug((
                    'Exception: Hammernova.get_server() failed to '
                    'get server'
                ))
                continue
            if ret:
                return (ret, region)
        return ({}, None)

    def get_server(self, region, instance_id=None, name=None):
        '''
        list all servers in a region
        '''
        endpoint = self._get_endpoint(
            'compute',
            region,
            type_name='cloudServersOpenStack'
        )

        headers = {
            'X-Auth-Token': self.auth.token,
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

        if instance_id is not None:
            ret = self.sess.get(
                '{0}/servers/{1}'.format(endpoint, instance_id),
                headers=headers,
                verify=False
            ).json().pop('server', {})
        else:
            ret = self.sess.get(
                '{0}/servers/detail?name={1}'.format(endpoint, name),
                headers=headers,
                verify=False
            ).json()['servers'].pop()
        return ret

    def get_server_by_id(self, instance_id):
        '''
        get server based on an attribute, from any region
        '''
        for region in ['ORD', 'DFW', 'IAD', 'SYD', 'LON', 'HKG']:
            try:
                ret = self.get_server(region=region, instance_id=instance_id)
            except IndexError:
                continue
            if ret:
                return (ret, region)
        return ({}, None)

    def get_server_by_name(self, name):
        '''
        get server based on an attribute, from any region
        '''
        for region in ['ORD', 'DFW', 'IAD', 'SYD', 'LON', 'HKG']:
            try:
                ret = self.get_server(region=region, name=name)
            except Exception:
                log.debug((
                    'Exception: Hammernova.get_server() failed to '
                    'get server'
                ))
                continue
            if ret:
                return (ret, region)
        return ({}, None)

    def _do_action(self, endpoint, action, value):
        '''
        Api calls for actions
        '''
        headers = {
            'X-Auth-Token': self.auth.token,
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

        payload = {
            action: value
        }

        return self.sess.post(
            endpoint,
            data=json.dumps(payload),
            headers=headers,
            verify=False
        )

    def rescue(self, uuid, region, test=False):
        '''
        place server in rescue mode
        '''
        endpoint = self._get_endpoint('compute', region)
        resp = self._do_action(
            '{0}/servers/{1}/action'.format(endpoint, uuid),
            'rescue',
            'none'
        )

        while self.get_server_by_region(uuid, region).get('OS-EXT-STS:vm_state').lower() != 'rescued':
            time.sleep(5)

        if test:
            return resp
        password = resp.json().get('adminPass', None)

        return password

    def unrescue(self, uuid, region):
        '''
        place server in rescue mode
        '''
        endpoint = self._get_endpoint('compute', region)

        resp = self._do_action(
            '{0}/servers/{1}/action'.format(endpoint, uuid), 'unrescue', 'none'
        )
        return resp

    def get_vnc_console(self, instance_id, region=None, consoletype='xvpvnc'):
        '''
        get vnc console link from server, based on region or not
        '''
        endpoint = self._get_endpoint('compute', region)

        headers = {
            'X-Auth-Token': self.auth.token,
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

        payload = {
            'os-getVNCConsole': {
                'type': consoletype
            }
        }

        ret = self.sess.post(
            '{0}/servers/{1}/action'.format(endpoint, instance_id),
            data=json.dumps(payload),
            headers=headers,
            verify=False
        )
        return ret.json().get('console', {}).get('url', None)
