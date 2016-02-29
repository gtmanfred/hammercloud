import os
import requests
import yaml

# disable urllib3 warnings
try:
    import requests.packages.urllib3
    requests.packages.urllib3.disable_warnings()
except (ImportError, AttributeError) as exc:
    pass

# setup logging
import logging
log = logging.getLogger(__name__)

IDENTITY = 'https://identity.api.rackspacecloud.com/v2.0'


class CloudAPI(object):
    '''
    Nova api library for hammercloud
    '''
    _config = None

    def __init__(self, auth):
        self.auth = auth
        self.sess = auth.sess

    @property
    def config(cls):
        if cls._config is None:
            with open(os.path.expanduser('~/.config/hammercloud/config.yml')) as configfile:
                cls._config = yaml.load(configfile).get('hammercloud', {})
        return cls._config

    def _get_endpoint(self, endpoint_type, region=None, type_name=None):
        '''
        get endpoint based on type and region
        '''
        endpoints = []
        for endpoint in self.auth.catalog:
            if type_name is not None and endpoint.get('name', '') != type_name:
                continue
            if endpoint.get('type', '') == endpoint_type:
                endpoints.extend(endpoint['endpoints'])

        endpoint = None
        if region is not None:
            region = region.upper()
            for reg in endpoints:
                if reg.get('region', None) == region:
                    endpoint = reg['publicURL']
                    break

        elif endpoints:
            endpoint = endpoints[0]['publicURL']
        else:
            raise Exception(
                'No endpoints found of type: {0}'.format(endpoint_type)
            )

        if endpoint is None:
            raise Exception('Region not available')

        log.debug('Endpoint: %s', endpoint)
        return endpoint
