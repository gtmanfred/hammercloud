from __future__ import absolute_import, print_function

import functools
import logging
import multiprocessing
import os
import six
import subprocess

import hammercloud
import hammercloud.handle
import hammercloud.terminal

log = logging.getLogger(__name__)


def main():
    servers = []

    kwargs, parser = hammercloud.parser()

    hcconfig = hammercloud.hcconfig

    hammercloud.Shell(config=hcconfig)

    if kwargs.with_spam is True:
        hammercloud.spam()

    if kwargs.log and kwargs.log.upper() in ('DEBUG', 'WARNING', 'CRITICAL'):
        hammercloud.log.setLevel(getattr(logging, kwargs.log.upper()))

    if kwargs.version is True:
        print('HammerCloud Version {0}'.format(hammercloud.__version__))

    elif kwargs.token is not None:
        hammercloud.tokens.set(name=hcconfig.get('user'), key='identity', value=kwargs.token)

    elif kwargs.nova is not None:
        with hammercloud.Account(username=kwargs.username, region=kwargs.nova[1].upper()) as sess:
            sess.setup_keyring()

    elif kwargs.ipfinder:
        for ip_ in kwargs.ipfinder:
            device = hammercloud.Server.ipfinder(ip_)

            if device is not None:
                servers.append(device)

    elif kwargs.list_servers:
        auth = hammercloud.Account(username=kwargs.username, tenantid=kwargs.tenantid, apikey=kwargs.apikey)
        hammercloud.Server.list_servers(auth)

    elif kwargs.list_scripts:
        autorun_script_path = os.path.expanduser(
            '~/.config/hammercloud/autorun'
        )
        autorund_script_path = '{0}.d'.format(autorun_script_path)
        if os.path.exists(autorun_script_path):
            print('<=== Script: {0} ===>'.format(autorun_script_path))
            with open(autorun_script_path, 'r') as autorun_script:
                print(autorun_script.read())
        if os.path.exists(autorund_script_path):
            for scriptfile in sorted(os.listdir(autorund_script_path)):
                print('<=== Script: {0} ===>'.format(scriptfile))
                scriptfile = os.path.join(autorund_script_path, scriptfile)
                with open(scriptfile, 'r') as autorund_script:
                    print(autorund_script.read())

    elif kwargs.copy:
        if ':' in kwargs.copy[0]:
            servers, _ = kwargs.copy[0].split(':')
        elif ':' in kwargs.copy[1]:
            servers, _ = kwargs.copy[1].split(':')

    elif kwargs.bastion:
        hammercloud.hcshell.bastion(hammercloud.Constants.CBASTS[kwargs.bastion.upper()],
                                    hcconfig.get('bastion_key'),
                                    hcconfig.get('user'))

    elif not kwargs.servers and kwargs.username:
        auth = hammercloud.Account(username=kwargs.username, tenantid=kwargs.tenantid, apikey=kwargs.apikey)
        serverlist = hammercloud.Server.list_servers(auth, printout=False)
        servers.extend([str(s['uuid']) for s in serverlist])

    elif not kwargs.servers:
        parser.print_help()

    if not servers:
        servers = kwargs.servers

    if len(servers) == 1:
        servers = servers[0]

    handle = functools.partial(hammercloud.handle.handle, args=kwargs)
    if isinstance(servers, six.string_types):
        try:
            ret = handle(servers)
        except KeyboardInterrupt:
            return
        if ret:
            subprocess.call('{0}/{1}.sh'.format(hammercloud.cachedir, ret), shell=True)
    elif isinstance(servers, list):
        pool = multiprocessing.Pool(len(servers))
        myterm = hcconfig.get('terminal')
        if myterm is None:
            print('No terminal specified in ~/.config/hammercloud/config.yml')
        else:
            myterm = myterm.replace('-', '_')
        names = []
        results = pool.map(handle, servers)
        names = [result[0] for result in results if result[0]]
        if names:
            terminal = hammercloud.terminal.HammerCloudTerminal()
            method = getattr(terminal, myterm)
            method(names)
