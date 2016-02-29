from __future__ import absolute_import
import os
import yaml

import hammercloud


class Account(hammercloud.BaseAccount):

    def __init__(self, username, tenantid=None, apikey=None, **kwargs):
        config = os.path.expanduser('~/.config/hammercloud/accounts/{0}.yml'.format(username))
        with open(config, 'r') as accountfile:
            config = yaml.load(accountfile)
        super(Account, self).__init__(config['username'],
                                      tenantid or config['tenantid'],
                                      apikey or config['apikey'],
                                      **kwargs)
