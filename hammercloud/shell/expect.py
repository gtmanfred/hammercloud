# -*- coding: utf-8 -*-
"""
Functions to create expect scripts
"""
from __future__ import print_function, absolute_import, with_statement

import re
import os
import subprocess
import pexpect
import struct
import fcntl
import termios
import signal
import sys
import requests

import hammercloud
from hammercloud import Constants as const
from hammercloud.templates import env


# pylint: disable=no-method-argument
class DevNull(object):
    '''
    don't print out log stuff from pexpect
    '''
    def write(*args):
        '''
        fake write
        '''
        pass

    def flush(*args):
        '''
        fake flush
        '''
        pass


def host(logininfo):
    '''
    login to hypervisor
    '''
    raise NotImplemented('Function not implemented: {0}'.format('host'))


def ssh(logininfo):
    '''
    ssh into managed cloud server using /usr/bin/env expect
    '''
    template = env.get_template('ssh.jinja')
    script_path = logininfo.script_path
    with open(script_path, 'w') as expectfile:
        print(template.render(login=logininfo, consts=hammercloud.Constants), file=expectfile)
    os.chmod(script_path, 448)
    return logininfo.hostname


def sftp(logininfo, transfer, src, dest, quiet=False, executable=False):
    '''
    ssh into managed cloud server using /usr/bin/env expect
    '''
    if not logininfo.admin_password:
        raise Exception('Unmanaged Cloud Server: no rack password')

    child = pexpect.spawn(
        (u'sftp -o PubkeyAuthentication=no -o RSAAuthentication=no '
         u'-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null '
         u'-o GSSAPIAuthentication=no -P {login.port} {login.ssh_args} '
         u'{login.ssh_user}@{login.ip}').format(login=logininfo),
        timeout=logininfo.timeout,
        logfile=DevNull() if quiet is True else sys.stdout,
        echo=False,
        encoding='utf-8'
    )

    child.expect([u'.*[P|p]assword: '])
    child.sendline(logininfo.admin_password)
    child.expect(u"sftp>")
    child.sendline(u"{0} {1} {2}".format(transfer, src, dest))
    if executable is True:
        child.expect(u"sftp>")
        child.sendline(u"chmod 755 {0}".format(dest))
    child.expect(u"sftp>")
    child.sendeof()


def cmd(logininfo, returnresp=False):
    '''
    run a command on a server
    '''
    if not logininfo.admin_password:
        raise Exception('Unmanaged Cloud Server: no rack password')

    thescript = []
    thescript.append(u'ssh -ttt -l {login.ssh_user} -p '
                     u'{login.port} -o NumberOfPasswordPrompts=1 '
                     u'-o StrictHostKeyChecking=no -o '
                     u'UserKnownHostsFile=/dev/null -o '
                     u'GSSAPIAuthentication=no {login.ssh_args} '
                     u'{login.ip} -- ')
    if logininfo.skip_root:
        thescript.append(u'"{0}"'.format(logininfo.command))
    else:
        thescript.append(u'"sudo -k {0}"'.format(logininfo.command))

    result = pexpect.run(
        u''.join(thescript).format(login=logininfo),
        timeout=-1,
        withexitstatus=True,
        events={
            u'{login.ssh_user}@{login.ip}\'s password:'.format(login=logininfo):
                u'{login.admin_password}\n'.format(login=logininfo),
            u'Password:': u'{login.admin_password}\n'.format(login=logininfo),
            u'password for {login.ssh_user}:'.format(login=logininfo):
                u'{login.admin_password}\n'.format(login=logininfo)
        }
    )
    response = re.sub(u'.*Warning: Permanently.*', '', result[0].decode('utf-8'))
    response = re.sub(
        u'.*{login.ssh_user}@{login.ip}\'s password:'.format(login=logininfo),
        '',
        response
    )
    response = re.sub(
        u'.*password for {login.ssh_user}:'.format(login=logininfo),
        '',
        response
    )
    response = re.sub(u'.*Password:.*', '', response)
    response = re.sub(u'Connection to .* closed.', '', response)
    if returnresp is True:
        return response.strip()

    print('### {0} ###'.format(logininfo.hostname))
    print('\n{0}\n'.format(response.strip()))


def script(logininfo, filepath):
    '''
    run script on managed cloud server using /usr/bin/env expect
    '''
    if not logininfo.admin_password:
        raise Exception('Unmanaged Cloud Server: no rack password')

    if '/' in filepath:
        logininfo.script = filepath.split('/')[-1]
    else:
        logininfo.script = filepath

    if filepath.startswith('https://'):
        newpath = os.path.expanduser(
            '~/.cache/hammercloud/{login.script}'.format(login=logininfo)
        )
        if not os.path.exists(newpath):
            with open(newpath, 'w') as newfile:
                resp = requests.get(filepath)
                print(resp.content, file=newfile)
        filepath = newpath

    sftp(
        logininfo, 'put', filepath, logininfo.script,
        quiet=True, executable=True
    )

    command = '/home/{login.ssh_user}/{login.script} {login.extraargs}; '

    if not logininfo.no_clean:
        command += 'rm /home/{login.ssh_user}/{login.script}'

    logininfo.command = command
    cmd(logininfo)


def setup_dc(datacenter, bastion_key, bastion_user):
    '''
    ssh-copy-id ssh keys to bastions
    '''
    output = []

    output.append('#!/usr/bin/env expect\n')

    output.append('exec rm -f $argv0\n')
    output.append('set timeout {timeout}\n'.format(timeout=30))
    output.append('log_user 0\n')
    output.append('match_max 100000\n')

    for cbast in const.CBASTS[datacenter]:
        output.append((
            'spawn -noecho ssh-copy-id -i {bastion_key} '
            '-o RSAAuthentication=no -o StrictHostKeyChecking=no '
            '-o UserKnownHostsFile=/dev/null -o ProxyCommand=none '
            '-o GSSAPIAuthentication=no {username}@{datacenter}\n'
        ).format(bastion_key=bastion_key, username=bastion_user, datacenter=cbast))
        output.append('match_max 100000\n')

        output.append('interact {\n')
        output.append('\t\\034 exit\n')
        output.append('}\n')

    confdir = '{0}/.cache/hammercloud/'.format(os.path.expanduser('~'))
    script_path = '{0}/{1}1.sh'.format(confdir, datacenter)
    with open(script_path, 'w') as fh_:
        fh_.write("".join(output))
    os.chmod(script_path, 448)

    subprocess.call(script_path)


def bastion(datacenter, bastion_key, bastion_user):
    '''
    ssh to the bastion in the datacenter
    '''
    output = []

    output.append('#!/usr/bin/env expect\n')

    output.append('exec rm -f $argv0\n')
    output.append('set timeout {timeout}\n'.format(timeout=30))
    output.append('log_user 0\n')
    output.append('match_max 100000\n')

    output.append((
        'spawn -noecho ssh -i {bastion_key} '
        '-o RSAAuthentication=no -o StrictHostKeyChecking=no '
        '-o UserKnownHostsFile=/dev/null -o ProxyCommand=none '
        '-o GSSAPIAuthentication=no {username}@{datacenter}\n'
    ).format(bastion_key=bastion_key, username=bastion_user, datacenter=const.DCS[datacenter]))
    output.append('match_max 100000\n')

    output.append('interact {\n')
    output.append('\t\\034 exit\n')
    output.append('}\n')

    confdir = '{0}/.cache/hammercloud/'.format(os.path.expanduser('~'))
    script_path = '{0}/{1}1.sh'.format(confdir, datacenter)
    with open(script_path, 'w') as fh_:
        fh_.write("".join(output))
    os.chmod(script_path, 448)

    subprocess.call(script_path)
