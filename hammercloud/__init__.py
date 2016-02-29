# -*- coding: utf-8 -*-
"""
Init file for hammercloud
"""
from __future__ import absolute_import, print_function

import base64
import logging
import os
import pkg_resources
import stevedore
import sys
import yaml

from hammercloud.parser import parser
from hammercloud._utils import valid_uuid, gettermsize
from hammercloud.server import BaseServer
from hammercloud.account import BaseAccount
from hammercloud.api.preferences import Preferences
from hammercloud.api.nova import HammerNova
from hammercloud.api.firstgen import HammerFirst

logging.getLogger("requests").setLevel(logging.WARNING)
logging.basicConfig(stream=sys.stdout, level=logging.WARNING)
log = logging.getLogger(__name__)

# pylint: disable=not-callable
PKG = pkg_resources.require("hammercloud")[0]
__version__ = PKG.version

with open(os.path.expanduser('~/.config/hammercloud/config.yml')) as configfile:
    config = yaml.load(configfile)

hcconfig = config.get('hammercloud', {})
cachedir = hcconfig.get('cachedir', os.path.expanduser('~/.cache/hammercloud'))

Server = stevedore.driver.DriverManager(
    namespace='.'.join(['hammercloud', hcconfig.get('plugin', 'static')]),
    name='Server',
    invoke_on_load=False,
).driver

Account = stevedore.driver.DriverManager(
    namespace='.'.join(['hammercloud', hcconfig.get('plugin', 'static')]),
    name='Account',
    invoke_on_load=False,
).driver

Constants = stevedore.driver.DriverManager(
    namespace='.'.join(['hammercloud', hcconfig.get('plugin', 'static')]),
    name='Constants',
    invoke_on_load=False,
).driver

Metrics = stevedore.driver.DriverManager(
    namespace='.'.join(['hammercloud', hcconfig.get('plugin', 'static')]),
    name='Metrics',
    invoke_on_load=False,
).driver

Shell = stevedore.driver.DriverManager(
    namespace='.'.join(['hammercloud', hcconfig.get('plugin', 'static')]),
    name='Shell',
    invoke_on_load=False,
).driver

Server.Account = Account


def spam():
    '''
    plesk... shhhh
    '''
    # pylint: disable=line-too-long
    print(base64.b64decode(
        """PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09CnwgLGRQIiI4YSAiODg4
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
        PUZMPT0K""").decode())

# flake8: noqa
