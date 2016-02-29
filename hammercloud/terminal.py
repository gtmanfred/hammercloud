# -*- coding: utf-8 -*-
'''
Terminal classes
'''
from __future__ import absolute_import
import time
import os
from subprocess import call, Popen, PIPE
import shlex

import hammercloud


class HammerCloudTerminal(object):
    '''
    Multiplex multiple terminals
    '''
    def __init__(self):
        self.config = hammercloud.hcconfig
        self.termconfig = hammercloud.config.get('terminal', {})
        self.cachedir = hammercloud.cachedir
        self.geometry = self.config.get('geometry')
        self.terminal = self.config.get('terminal')

    def iterm(self, servers):
        '''
        Iterm
        '''
        ascript_path = "{0}/{1}.scpt".format(self.cachedir, int(time.time()))

        if self.geometry:
            (columns, rows) = self.geometry.split('x')

        ascript = []

        ascript.append('tell application "iTerm"')
        ascript.append('activate')
        ascript.append('set htiterm to (make new terminal)')
        ascript.append('tell htiterm')

        if self.geometry:
            ascript.append('set number of columns to {0}'.format(columns))
            ascript.append('set number of rows to {0}'.format(rows))

        for server in servers:
            script_path = '{0}/{1}.sh'.format(self.cachedir, server)
            ascript.append('launch session "Default"')
            ascript.append('tell the last session')
            ascript.append('write text "{0}"'.format(script_path))
            ascript.append('end tell')

        ascript.append('do shell script "rm -rf {0}"'.format(ascript_path))
        ascript.append('end tell')
        ascript.append('end tell')

        call("/usr/bin/osascript -e '{0}'".format(
            "' -e '".join(ascript)
        ), shell=True)
        return

    def gnome_terminal(self, servers):
        '''
        Gnome Terminal
        '''
        if self.geometry:
            geometry = '--geometry {0}'.format(self.geometry)
        else:
            geometry = ''

        command = []
        for server in servers:
            command.append("{0} --tab -t {1} -e {2}/{1}.sh ".format(
                geometry, server, self.cachedir
            ))

        call('{0} {1}'.format(self.terminal, ''.join(command)), shell=True)
        return

    mate_terminal = gnome_terminal

    def xfce4_terminal(self, servers):
        '''
        XFCE4 Terminal
        '''
        if self.geometry:
            geometry = '--geometry {0}'.format(self.geometry)
        else:
            geometry = ''

        command = []
        for server in servers:
            command.append("{0} --tab -T {1} -e {2}/{1}.sh ".format(
                geometry, server, self.cachedir
            ))

        call('{0} {1}'.format('xfce4-terminal', ''.join(command)), shell=True)
        return

    def konsole(self, servers):
        '''
        Konsole
        '''
        for server in servers:
            command = "--new-tab -e {0}/{1}.sh ".format(self.cachedir, server)
            call("{1} {2} &".format('konsole', command), shell=True)

        return

    def tmux(self, servers):
        '''
        Tmux
        '''
        def _tcall(cmd):
            '''
            Helper function for tmux
            '''
            proc = Popen(shlex.split(cmd), stdout=PIPE)
            output, _ = proc.communicate()
            proc.stdout.close()
            tmuxinfo = output.decode().strip()
            tmuxinfo = tmuxinfo.split(':')
            sess = tmuxinfo[0]
            window, pane = tmuxinfo[1].split('.')
            return {'sess': sess,
                    'wind': window,
                    'pane': pane}

        if 'TMUX_PANE' not in os.environ:
            call(r'tmux new-session \; detach', shell=True)

        layout = self.termconfig('tmux_layout', None)
        max_panes = self.termconfig('tmux_max_panes', None)

        if layout in ['even-horizontal', 'even-vertical', 'main-horizontal',
                      'main-vertical', 'tiled']:
            first = True
            pane_count = 0
            # window_count = 0
            windows = list()
            for server in servers:
                if pane_count % max_panes == 0:
                    first = True
                    pane_count = 0
                    # window_count += 1
                if first:
                    first = False
                    pane_count += 1
                    index = servers.index(server)
                    command = 'new-window -P -d -n "{0}" {1}/{2}.sh'.format(
                        ','.join(
                            str(item) for item in
                            servers[index:index + max_panes]
                        ), self.cachedir, server
                    )
                else:
                    pane_count += 1
                    command = (
                        'split-window -P -d -h -t "{0}" {1}/{2}.sh'
                    ).format(windows[-1], self.cachedir, server)
                winfo = _tcall('{0} {1}'.format('tmux', command))
                if winfo['wind'] not in windows:
                    windows.append(winfo['wind'])
            for win in windows:
                call('{0} {1}'.format(
                    'tmux', 'select-layout -t {1} {0} '.format(
                        layout, win)), shell=True)
        else:
            for server in servers:
                command = 'new-window -d -n {0} {1}/{0}.sh'.format(
                    server, self.cachedir
                )
                call('{0} {1}'.format('tmux', command), shell=True)

        if 'TMUX_PANE' not in os.environ:
            call('tmux kill-window -t 0', shell=True)
            call('tmux attach', shell=True)
        return

    def screen(self, servers):
        '''
        Screen
        '''
        first = True
        attach = ''
        session = 'ht{0}'.format(''.join([str(item) for item in servers]))

        for server in servers:
            if ('TERM' not in os.environ or
                    os.environ['TERM'].lower() != 'screen') and first:
                command = '-dmS {0} {1}/{2}.sh'.format(
                    session, self.cachedir, server
                )
                attach = '-x {0} -X eval'.format(session)
                call('{0} {1}'.format('screen', command), shell=True)
                first = False
            else:
                if attach:
                    command = '{0} "screen {1}/{2}.sh"'.format(
                        attach, self.cachedir, server
                    )
                else:
                    command = '{0}/{1}.sh'.format(self.cachedir, server)
                call('{0} {1}'.format('screen', command), shell=True)

        if attach:
            call('screen -r {0}'.format(session), shell=True)
        return
