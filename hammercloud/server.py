from __future__ import absolute_import
import os
import pprint
import re
import yaml

try:
    import supernova.credentials
    HAS_SUPERNOVA = True
except ImportError as exc:
    HAS_SUPERNOVA = False

from ._utils import valid_uuid, get_entry
from . import api

import logging
log = logging.getLogger(__name__)


class BaseServer(object):
    _config = None

    def __init__(self, instance_id, args, account=None, **kwargs):
        self.instance_id = instance_id
        self.args = args
        self._username = account.username if account is not None else args.username
        self._tenantid = account.tenantid if account is not None else args.tenantid
        self._apikey = account.apikey if account is not None else args.apikey
        self._datacenter = kwargs.get('datacenter', None)
        if HAS_SUPERNOVA:
            self.supernova = supernova.credentials
        self.auth = account or self.Account(username=args.username,
                                            tenantid=args.tenantid,
                                            apikey=args.apikey,
                                            **kwargs)

    @property
    def server(self):
        if not hasattr(self, '_server'):
            if self.firstgen is True:
                self._server = self._first_gen_server
            elif self.firstgen is False:
                self._server = self._next_gen_server
            else:
                self._server, self.datacenter = self.lookup(self.instance_id,
                                                            auth=self.auth,
                                                            datacenter=self.datacenter)
                self.instance_id = str(self._server['id'])
        return self._server

    @property
    def firstgen(self):
        if valid_uuid(self.instance_id):
            return False
        elif self.instance_id.isdigit():
            return True
        return None

    @property
    def username(self):
        return self._username

    @property
    def ssh_user(self):
        if hasattr(self, '_ssh_user'):
            return self._ssh_user
        return self.args.ssh_user

    @ssh_user.setter
    def ssh_user(self, value):
        self._ssh_user = value

    @property
    def apikey(self):
        return self._apikey

    @property
    def tenantid(self):
        return self._tenantid

    @property
    def novaconn(self):
        instance_id = self.instance_id
        if not hasattr(self, '_novaconn'):
            if valid_uuid(instance_id):
                self._novaconn = api.HammerNova(self.auth)
            elif instance_id.isdigit():
                self._novaconn = api.HammerFirst(self.auth)
        return self._novaconn

    @property
    def ip(self):
        if self.args.use_public is True:
            return self.public_ip
        elif self.args.use_private is True:
            return self.private_ip
        return self.access_ip

    @property
    def use_bastion(self):
        return ''

    @property
    def host_ip(self):
        raise NotImplemented('host ip is not implemented in the base class')

    @property
    def config(self):
        if self._config is None:
            with open(os.path.expanduser('~/.config/hammercloud/config.yml')) as configfile:
                self._config = yaml.load(configfile).get('hammercloud', {})
        return self._config

    @property
    def command(self):
        if hasattr(self, '_command'):
            return self._command
        return self.args.command

    @command.setter
    def command(self, value):
        self._command = value

    @property
    def script_path(self):
        confdir = '{0}/.cache/hammercloud/'.format(os.path.expanduser('~'))
        script_path = '{0}/{1}.sh'.format(confdir, self.hostname)
        return script_path

    @property
    def _next_gen_server(self):
        if self.datacenter is None:
            ret, self.datacenter = self.novaconn.get_server_by_id(self.instance_id)
            return ret
        return self.novaconn.get_server(region=self.datacenter, instance_id=self.instance_id)

    @property
    def _first_gen_server(self):
        return self.novaconn.get_server(self.instance_id)

    @property
    def image(self):
        server = self.server
        if self.firstgen:
            return server.get('imageId', 'Unavailable')
        return server.get('image', {}).get('id', 'Unavailable')

    @property
    def access_ip(self):
        server = self.server
        if self.firstgen is True:
            return self.public_ip
        return server['accessIPv4']

    @property
    def public_ip(self):
        server = self.server
        if self.firstgen is True and 'public' in server['addresses']:
            return server['addresses']['public'][0]
        if 'public' in server['addresses']:
            return get_entry(server['addresses']['public'], 'version', 4)['addr']
        return 'none'

    @property
    def private_ip(self):
        server = self.server
        if self.firstgen is True:
            return self.server['addresses']['private'][0]
        if 'private' in server['addresses']:
            return get_entry(server['addresses']['private'], 'version', 4)['addr']
        return 'none'

    @property
    def hostname(self):
        return self.server['name']

    @property
    def display_name(self):
        return self.hostname

    @property
    def os_type(self):
        return 'linux'

    @property
    def password(self):
        raise NotImplemented('password api must be implemented in plugin')

    @property
    def admin_password(self):
        if hasattr(self, '_admin_password'):
            return self._admin_password
        return self.password

    @admin_password.setter
    def admin_password(self, value):
        self._admin_password = value

    @property
    def timeout(self):
        return self.config.get('expect_timeout', getattr(self.args, 'expect_timeout', None)) or 10

    @property
    def skip_root(self):
        if hasattr(self, '_skip_root'):
            return self._skip_root
        return self.args.skip_root

    @skip_root.setter
    def skip_root(self, value):
        self._skip_root = value

    @property
    def skip_scripts(self):
        if hasattr(self, '_skip_scripts'):
            return self._skip_scripts
        return self.args.skip_scripts

    @skip_scripts.setter
    def skip_scripts(self, value):
        self._skip_scripts = value

    @property
    def no_clean(self):
        if hasattr(self, '_no_clean'):
            return self._no_clean
        return self.args.no_clean

    @no_clean.setter
    def no_clean(self, value):
        self._no_clean = value

    @property
    def no_proxy(self):
        if hasattr(self, '_no_proxy'):
            return self._no_proxy
        return self.args.no_proxy or None

    @no_proxy.setter
    def no_proxy(self, value):
        self._no_proxy = value

    @property
    def extraargs(self):
        if hasattr(self, '_extraargs'):
            return self._extraargs
        return self.args.extraargs

    @extraargs.setter
    def extraargs(self, value):
        self._extraargs = value

    @property
    def port(self):
        return self.args.port or 22

    def console(self, consoletype='xvpvnc'):
        '''
        return link for servers vnc console link
        '''
        instance_id = self.server['id']
        link = self.novaconn.get_vnc_console(instance_id, region=self.datacenter, consoletype=consoletype)
        log.debug('Console Link: %s', link)
        return link

    def rescue(self, test=False):
        '''
        put server into rescue mode
        '''
        instance_id = self.server['id']
        ret = self.novaconn.rescue(instance_id, self.datacenter, test)
        log.debug('Rescue Server: \n%s', pprint.pformat(ret))
        return ret

    def unrescue(self):
        '''
        remove server from rescue mode
        '''
        instance_id = self.server['id']
        ret = self.novaconn.unrescue(instance_id, self.datacenter)
        print('Server {0} unrescued.'.format(self.instance_id))
        log.debug('UnRescue Server: \n%s', pprint.pformat(ret))

    @property
    def enforce_server_ssh_key(self):
        return False

    @property
    def server_key(self):
        if self.config.get('server_key'):
            return '-i {0}'.format(os.path.expanduser(
                self.config.get('server_key')
            ))
        return ''

    @property
    def bastion_key(self):
        if self.args.bastion_key:
            return os.path.expanduser(self.args.bastion_key)
        elif self.config.get('bastion_key'):
            return os.path.expanduser(self.config.get('bastion_key'))
        raise Exception('Configuration not specified: {0}'.format('bastion_key'))

    @property
    def bastion(self):
        return self.config.get('bastion')

    @property
    def bastion_user(self):
        return self.config.get('user')

    @property
    def ssh_args(self):
        return ' '.join([os.path.expanduser(arg) for arg in self.config.get('ssh_args', '').split()])

    @property
    def vm_mode(self):
        return 'none'

    @staticmethod
    def lookup(servername, auth, datacenter=None):
        '''
        lookup uuid for server based on any variable in the details list
        requries a username
        '''
        conn = api.HammerNova(auth)
        if datacenter is not None:
            cs_ = conn.get_server(region=datacenter, name=servername)
        else:
            cs_, datacenter = conn.get_server_by_name(name=servername)

        if cs_:
            log.debug('Nextgen Server: \n%s', pprint.pformat(cs_))
            return cs_, datacenter

        conn = api.HammerFirst(auth)
        firstgen = conn.list_servers()
        log.debug('Firstgen Servers: \n%s', pprint.pformat(firstgen))
        if firstgen:
            server = get_entry(firstgen, 'name', servername)
            if server:
                return server, None

        return {}, None

    @staticmethod
    def list_servers(auth, printout=True):
        '''
        list all servers on account
        '''
        conn = api.HammerNova(auth)
        servers = []
        for region in ['ORD', 'DFW', 'IAD', 'SYD', 'LON', 'HKG']:
            try:
                for server in conn.list_servers(region):
                    log.debug(
                        '%s-%s: \n%s', region,
                        server['name'], pprint.pformat(server)
                    )
                    servers.append({
                        'name': server['name'],
                        'uuid': server['id'],
                        'region': region
                    })
            except Exception:
                log.debug((
                    'Exception: servers.list_servers: failed to list_servers, '
                    'most likely because of not having ORD endpoint.'
                ))
        firstgen = api.HammerFirst(auth)
        for server in firstgen.list_servers():
            log.debug('firstgen-%s: \n%s', server['name'], pprint.pformat(server))
            servers.append({
                'name': server['name'],
                'uuid': str(server['id']),
                'region': ''
            })
        if printout:
            print('Account User: {0}'.format(auth.username))
            print('{0: <50}{1: <56}{2}'.format('Name', 'UUID', 'Region'))
            for serv in servers:
                print('{name: <50} {uuid: <56} {region}'.format(**serv))
        return servers

    @classmethod
    def get_serverlist(self, auth):
        '''
        Return a list of UUID's for the listed account.
        '''
        servers = []
        for server in self.list_servers(auth, printout=False):
            servers.append(server['uuid'])
        log.debug('Server UUIDs: \n%s', servers)

        return servers

    @property
    def autorun_commands(self):
        if self.skip_scripts is True:
            return []
        autorun_script_path = os.path.expanduser('~/.config/hammercloud/autorun')
        autorund_script_path = '{0}.d'.format(autorun_script_path)
        commands = []
        if os.path.exists(autorun_script_path):
            with open(autorun_script_path, 'r') as autorun_script:
                commands.extend([re.escape(line.rstrip()) for line in autorun_script.readlines() if line])
        if os.path.exists(autorund_script_path):
            for scriptfile in sorted(os.listdir(autorund_script_path)):
                autoscriptd = os.path.join(autorund_script_path, scriptfile)
                with open(autoscriptd, 'r') as autorund_script:
                    commands.extend([re.escape(line.rstrip()) for line in autorund_script.readlines() if line])
        return commands
