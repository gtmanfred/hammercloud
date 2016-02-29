from hammercloud.api import CloudAPI

import logging
log = logging.getLogger(__name__)

IDENTITY = 'https://identity.api.rackspacecloud.com/v2.0'


class HammerFirst(CloudAPI):
    '''
    Firstgen api library for hammercloud
    '''
    def list_servers(self):
        '''
        get firstgen servers
        '''
        try:
            endpoint = self._get_endpoint('compute', type_name='cloudServers')
        except Exception:
            log.debug((
                'Exception: HammerFirst.list_servers no firstgen endpoint'
            ))
            return []
        if endpoint is None:
            return []

        headers = {
            'X-Auth-Token': self.auth.token,
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

        if endpoint:
            return self.sess.get(
                '{0}/servers/detail'.format(endpoint),
                headers=headers,
                verify=False
            ).json()['servers']
        else:
            return {}

    def get_server(self, server):
        '''
        get server based on an attribute
        '''
        endpoint = self._get_endpoint('compute', type_name='cloudServers')

        headers = {
            'X-Auth-Token': self.auth.token,
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

        return self.sess.get(
            '{0}/servers/{1}'.format(endpoint, server),
            headers=headers,
            verify=False
        ).json()['server']
