from hammercloud.api import CloudAPI


class Preferences(CloudAPI):
    '''
    get information from cloud preferences
    '''
    def __init__(self, auth, instance_id, os_type=None):
        super(Preferences, self).__init__(auth)
        self.instance_id = instance_id
        self.os_type = os_type

    @property
    def _default_port(self):
        '''
        Get default port for each os
        '''
        return {'windows': 445,
                'linux': 22, }.get(self.os_type, 22)

    @property
    def default_port(self):
        '''
        try and get default port from cloud preferences
        '''
        headers = {
            'X-Auth-Token': self.auth.token,
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'X-Tenant-ID': self.auth.tenantid,
        }

        endpoint = (
            'https://preferences.api.rackspacecloud.com/v2/{tenantid}/'
            'servermill_automation/default_{os_type}_port?'
            'server_id={instance_id}'
        ).format(
            os_type=self.os_type, tenantid=self.auth.tenantid,
            instance_id=self.instance_id
        )
        resp = self.sess.get(endpoint, headers=headers, verify=False)
        if resp.status_code == 200:
            return int(resp.json()['default_{0}_port'.format(self.os_type)])
        return int(self._default_port)
