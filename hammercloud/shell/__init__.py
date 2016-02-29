# -*- coding: utf-8 -*-
"""
different shell plugins
"""
from __future__ import absolute_import, print_function

import os
import requests
import subprocess
import sys

from hammercloud import Constants as const
from hammercloud.shell import expect, pshell  # noqa


def spam():
    '''
    plesk... shhhh
    '''
    # pylint: disable=line-too-long
    this = """PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09CnwgLGRQIiI4YSAiODg4
              ODg4YiwgIGQ4YiAgICAiODg4YiAgLDg4OCIgfAp8IDg4YiAgICIgIDg4OCAgZDg4IGRQWThiICAg
              IDg4WThiLDg4ODggIHwgCnwgYCJZODg4OGEgODg4YWQ4UCdkUGFhWThiICAgODggWTg4UDg4OCAg
              fAp8IGEgICAgWTg4IDg4OCAgICBkUCAgICBZOGIgIDg4ICBZUCA4ODggIHwKfCBgIjhhZDhQJ2E4
              ODhhICBhODhhOyphODg4YWE4OGEgICBhODg4YSB8CnwgICAgICAgICAgICAgICAgOyo7Ozs7Kjs7
              Oyo7OzsqLCwgICAgICAgfAp8ICAgICAgICBfLC0tLScnOjo6JzsqOzs7Kjs7Oyo7OypkOywgICAg
              IHwKfCAgICAgLi0nICAgICAgOjo6Ojo6Ojo6Oic7Kjs7KjtkSUk7ICAgICB8CnwgICAuJyAsPDw8
              LC4gIDo6Ojo6Ojo6Ojo6Ojo6OmZmZmZmZmAuICAgfAp8ICAvICw8PDw8PDw8PCw6Ojo6Ojo6Ojo6
              Ojo6Ojo6ZmZmZmZJLFwgIHwKfCAuLDw8PDw8PDw8PDxJOzo6Ojo6Ojo6Ojo6Ojo6OmZmZmZLSVAi
              LCB8CnwgfDw8PDw8PDw8PDxkUDssPz47LDo6Ojo6Ojo6OjpmZmZLS0lQIHwgfAp8IGBgPDw8PDw8
              PGRQOzs7OztcPj4+Pj47LDo6OjpmZmZLS0lQZiAnIHwKfCAgXCBgbVlNTVY/Ozs7Ozs7O1w+Pj4+
              Pj4+Pj4sWUlJUFAiYCAvICB8CnwgICBgLiAiIjo7Ozs7Ozs7OztpPj4+Pj4+Pj4+Pj4+PiwgICwn
              ICAgfAp8ICAgICBgLS5fYGAiOjs7O3NQJ2AiPz4+Pj4+PT09PT09PT09LiAgIHwKfCAgICAgICAg
              ICAgLS0uLi5fX19fX19fLi4ufDxbSG9ybWVsIHwgICB8CnwgICAgICAgICAgICAgICAgICAgICAg
              ICAgIGA9PT09PT09PT0nICAgfAo9PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09
              PUZMPT0K"""
    import base64
    print(base64.b64decode(this).decode())


def exec_html_console(console_url, logininfo, browser):
    '''
    launch console in html5
    '''
    output = []

    output.append(
        '{0}Device:{1} {2}'.format(const.BLUE,
                                   const.RESET,
                                   logininfo.hostname)
    )
    if logininfo.hostname != logininfo.display_name:
        output.append('{0}Display Name:{1} {2}'.format(
            const.BLUE, const.RESET, logininfo.display_name
        ))

    output.append('{0}UUID:{1} {2}'.format(const.BLUE,
                                           const.RESET,
                                           logininfo.instance_id))
    output.append('{0}Account:{1} {2}'.format(const.BLUE,
                                              const.RESET,
                                              logininfo.tenantid))
    output.append('{0}Primary IP:{1} {2}'.format(const.BLUE,
                                                 const.RESET,
                                                 logininfo.ip))
    if logininfo.access_ip != logininfo.public_ip:
        output.append('{0}Initial Public IP: {1} {2}'.format(
            const.BLUE, const.RESET, logininfo.public_ip
        ))
    output.append('{0}Private IP: {1} {2}'.format(
        const.BLUE, const.RESET, logininfo.private_ip
    ))
    output.append('{0}User:{1} {2} / {3}'.format(
        const.BLUE, const.RESET, logininfo.ssh_user,
        logininfo.admin_password
    ))
    print('\n'.join(output))
    subprocess.Popen(browser.get_command(console_url))


def exec_console(console_url, logininfo, blocking=True):
    '''
    launch console in java VncViewer.jar
    '''
    output = []

    output.append(
        '{0}Device:{1} {2}'.format(const.BLUE,
                                   const.RESET,
                                   logininfo.hostname)
    )
    if logininfo.hostname != logininfo.display_name:
        output.append('{0}Display Name:{1} {2}'.format(
            const.BLUE, const.RESET, logininfo.display_name
        ))

    output.append('{0}UUID:{1} {2}'.format(const.BLUE,
                                           const.RESET,
                                           logininfo.instance_id))
    output.append('{0}Account:{1} {2}'.format(const.BLUE,
                                              const.RESET,
                                              logininfo.tenantid))
    output.append('{0}Primary IP:{1} {2}'.format(const.BLUE,
                                                 const.RESET,
                                                 logininfo.ip))
    if logininfo.access_ip != logininfo.public_ip:
        output.append('{0}Initial Public IP: {1} {2}'.format(
            const.BLUE, const.RESET, logininfo.public_ip
        ))
    output.append('{0}Private IP: {1} {2}'.format(
        const.BLUE, const.RESET, logininfo.private_ip
    ))
    output.append('{0}User:{1} {2} / {3}'.format(
        const.BLUE, const.RESET, logininfo.ssh_user,
        logininfo.admin_password
    ))
    print('\n'.join(output))
    vncviewer = os.path.join(sys.prefix, 'share', 'hammercloud', 'VncViewer.jar')
    if blocking:
        subprocess.call(['java', '-jar', vncviewer, 'URL', console_url])
    else:
        subprocess.Popen(['java', '-jar', vncviewer, 'URL', console_url])


def info(logininfo):
    '''
    print information about server
    '''
    output = []

    output.append('{0}Device:{1} {2}'.format(
        const.BLUE, const.RESET, logininfo.hostname
    ))
    if logininfo.hostname != logininfo.display_name:
        output.append('{0}Display Name:{1} {2}'.format(
            const.BLUE, const.RESET, logininfo.display_name
        ))
    output.append('{0}UUID:{1} {2}'.format(const.BLUE,
                                           const.RESET,
                                           logininfo.instance_id))
    output.append('{0}Image:{1} {2}'.format(const.BLUE,
                                            const.RESET,
                                            logininfo.image))
    if logininfo.vm_mode:
        output.append('{0}VM mode:{1} {2}'.format(
            const.BLUE, const.RESET, logininfo.vm_mode
        ))
    output.append('{0}Account:{1} {2}'.format(const.BLUE,
                                              const.RESET,
                                              logininfo.tenantid))
    output.append('{0}Primary IP:{1} {2}'.format(const.BLUE,
                                                 const.RESET,
                                                 logininfo.ip))
    if logininfo.access_ip != logininfo.public_ip:
        output.append('{0}Initial Public IP: {1} {2}'.format(
            const.BLUE, const.RESET, logininfo.public_ip
        ))
    output.append('{0}Private IP:{1} {2}'.format(
        const.BLUE, const.RESET, logininfo.private_ip
    ))
    output.append('{0}User:{1} {2} / {3}'.format(
        const.BLUE, const.RESET, logininfo.ssh_user,
        logininfo.admin_password
    ))
    output.append('{0}DC:{1} {2}'.format(const.BLUE,
                                         const.RESET,
                                         logininfo.datacenter))
    if logininfo.host:
        output.append('{0}Host:{1} {2}'.format(const.BLUE,
                                               const.RESET,
                                               logininfo.host))
    if logininfo.cell:
        output.append('{0}Cell:{1} {2}'.format(const.BLUE,
                                               const.RESET,
                                               logininfo.cell))
    print('\n'.join(output))


class BaseShell(object):
    '''
    Base shell class for making shells modular
    '''
    config = None
    shell = None

    def __new__(cls, config=None):
        if cls.config is None:
            cls.config = config
            cls.shell = globals()[cls.config.get('shelltype', 'expect')]
        return super(BaseShell, cls).__new__(cls)

    def __getattr__(self, func):
        if hasattr(self.shell, func):
            return getattr(self.shell, func)
        if func in globals():
            return globals()[func]
        return getattr(expect, func)
