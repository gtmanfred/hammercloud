# -*- coding: utf-8 -*-
"""
Class to define how to launch html console
"""
import platform

import logging
log = logging.getLogger(__name__)


class ConsoleBrowser(object):
    """
    Class to define how to launch html console
    """
    def __init__(self, browser):
        if platform.system() == 'Linux':
            self._init_linux(browser)
        elif platform.system() == 'Darwin':
            self._init_mac(browser)
        else:
            raise Exception('Unknown OS')

    def _init_linux(self, browser):
        '''
        Define how to launch browser in linux
        '''
        self.command = browser.split(' ')

    def _init_mac(self, browser):
        '''
        Define how to launch browser in mac osx
        '''
        commands = {
            'firefox': ['open', '-a', '/Applications/Firefox.app'],
            'chrome': ['open', '-a', r'/Applications/Google\ Chrome.app'],
            'google-chrome': [
                'open', '-a', r'/Applications/Google\ Chrome.app'
            ],
        }
        if browser in commands:
            self.command = commands[browser]
        else:
            self.command = ['open', '-a', browser]

    def get_command(self, console_url):
        '''
        construct command to run on commandline
        '''
        return self.command + [console_url]
