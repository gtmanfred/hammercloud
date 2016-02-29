# -*- coding: utf-8 -*-
"""
Handler function for handling all possiblities
"""
from __future__ import print_function, absolute_import

import hammercloud as hc

# python2-3 input
try:
    # pylint: disable=redefined-builtin,invalid-name,undefined-variable
    input = raw_input
except NameError:
    pass

import logging
log = logging.getLogger(__name__)


# pylint: disable=too-many-branches
def handle(server, args):
    '''
    Function to handle inputs
    '''
    shell = hc.Shell()
    logininfo = hc.Server(server, args)

    ret = None
    # (gtmanfred) this is a seperate if statement so that it will hit the
    # ssh at the end of the next if statement
    if args.rescue:
        logininfo.admin_password = logininfo.rescue()
        logininfo.ssh_user = 'root'
    elif args.unrescue:
        logininfo.unrescue()
        return None

    if args.info:
        shell.info(logininfo)
    elif args.use_host:
        shell.host(logininfo)
    elif args.webconsole:
        if getattr(server, 'firstgen', False):
            return None
        print('Initializing webconsole on {hypervisor}: {uuid}'.format(
            **logininfo
        ))
        logininfo.webconsole(comm=args.command)
        return None
    elif args.console:
        browser = logininfo.config.get('consolebrowser')
        consoletype = 'xvpvnc' if browser is None else 'novnc'
        console_url = logininfo.console(consoletype=consoletype)
        if not console_url:
            print('Failed to retrieve console url.')
            return None

        if browser is None:
            shell.exec_console(console_url, logininfo)
        else:
            shell.exec_html_console(console_url,
                                    logininfo,
                                    hc.consolebrowser.ConsoleBrowser(browser))

    elif args.copy:
        if args.copy[0].find(':') != -1:
            retrieve = 'get'
            server, src = args.copy[0].split(':')
            dest = args.copy[1]
        else:
            retrieve = 'put'
            server, dest = args.copy[1].split(':')
            src = args.copy[0]
        shell.sftp(logininfo, retrieve, src, dest)
    elif args.script:
        shell.script(logininfo, args.script)
    elif args.command:
        shell.cmd(logininfo)
    else:
        ret = shell.ssh(logininfo)
    return ret
