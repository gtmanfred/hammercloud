# -*- coding: utf-8 -*-
"""
SSH commands using paramiko
"""
from __future__ import print_function
import sys
import select
import os
import subprocess
import socket
import termios
import tty
try:
    import paramiko
    HAS_PARAMIKO = True
except ImportError:
    HAS_PARAMIKO = False


def virtual():
    return HAS_PARAMIKO


def _socket():
    '''
    open socket
    '''
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('127.0.0.1', 0))
    return sock.getsockname()


class Connection(object):
    '''
    SSH Connection class
    '''
    channel = None
    sock = None
    client = None
    transport = None
    proxy_client = None

    def __init__(self, logininfo, proxy=False):
        '''
        Initialize SSH Connection
        '''
        self.logininfo = logininfo
        self.proxy = proxy if logininfo.no_proxy is None else not logininfo.no_proxy

    def __enter__(self):
        self._open_connection()
        self.channel = self.client.invoke_shell()
        return self

    def __exit__(self, exctype, value, traceback):
        self.client.close()

    def _skip_for_prompt(self, prompt=None, printout=True):
        if prompt is None:
            prompt = '# '
        ret = ''
        while True:
            ret = ret + self.channel.recv(1024)
            if ret.endswith(prompt):
                break
        if printout:
            for line in ret.split('\n')[1:-1]:
                print(line)

    def wait_for_prompt(self, prompt=None, printout=True):
        if prompt is None:
            prompt = '# '
        ret = ''
        while True:
            ret = ret + self.channel.recv(1024)
            if ret.endswith(prompt):
                break
        if printout:
            print(ret.split('\n')[-1])

    def exec_command(self, command, prompt=None):
        if prompt is None:
            prompt = '# '
        self._skip_for_prompt(printout=False)
        self.channel.send(command + '\n')
        self.wait_for_prompt()
        self.channel.shutdown(2)

    def open_shell(self):
        """
        Opens a PTY on a remote server, and allows interactive commands to be
        run.  Reassigns stdin to the PTY so that it functions like a full
        shell, as would be given by the OpenSSH client.

        Differences between the behavior of OpenSSH and the existing Paramiko
        connection can cause mysterious errors, especially with respect to
        authentication. By keeping the entire SSH2 connection within Paramiko,
        such inconsistencies are eliminated.
        """
        if self.channel is None:
            self.channel = self.client.invoke_shell()
        # get the current TTY attributes to reapply after
        # the remote shell is closed
        oldtty_attrs = termios.tcgetattr(sys.stdin)

        # invoke_shell with default options is vt100 compatible
        # which is exactly what you want for an OpenSSH imitation
        if self.logininfo.skip_root is False:
            self.channel.send('exec sudo su -\n')

        def resize_pty():
            '''
            resize pty for terminal
            '''
            # resize to match terminal size
            tty_height, tty_width = \
                subprocess.check_output(['stty', 'size']).split()

            # try to resize, and catch it if we fail due to a closed connection
            try:
                self.channel.resize_pty(
                    width=int(tty_width), height=int(tty_height)
                )
            except paramiko.ssh_exception.SSHException:
                pass

        # wrap the whole thing in a try/finally construct to ensure
        # that exiting code for TTY handling runs
        try:
            stdin_fileno = sys.stdin.fileno()
            tty.setraw(stdin_fileno)
            tty.setcbreak(stdin_fileno)

            self.channel.settimeout(0.0)

            is_alive = True

            while is_alive:
                # resize on every iteration of the main loop
                resize_pty()

                # use a unix select call to wait until the remote shell
                # and stdin are ready for reading
                # this is the block until data is ready
                read_ready, _, _ = \
                    select.select([self.channel, sys.stdin], [], [])

                # if the channel is one of the ready objects, print
                # it out 1024 chars at a time
                if self.channel in read_ready:
                    # try to do a read from the remote end and print to screen
                    try:
                        out = self._read()

                        # remote close
                        if len(out) == 0:
                            is_alive = False
                        elif out.endswith('Log into: '):
                            is_alive = False
                        else:
                            # rely on 'print' to correctly handle encoding
                            print(out, end='')
                            sys.stdout.flush()

                    # do nothing on a timeout, as this is an ordinary condition
                    except socket.timeout:
                        pass

                # if stdin is ready for reading
                if sys.stdin in read_ready and is_alive:
                    # send a single character out at a time this is typically
                    # human input, so sending it one character at a time is the
                    # only correct action we can take use an os.read to prevent
                    # nasty buffering problem with shell history
                    char = os.read(stdin_fileno, 1)

                    # if this side of the connection closes, shut down
                    # gracefully
                    if len(char) == 0:
                        is_alive = False
                    else:
                        self.channel.send(char)

            # close down the channel for send/recv
            # this is an explicit call most likely redundant with the
            # operations that caused an exit from the REPL, but unusual exit
            # conditions can cause this to be reached uncalled
            self.channel.shutdown(2)

        # regardless of errors, restore the TTY to working order
        # upon exit and print that connection is closed
        finally:
            termios.tcsetattr(sys.stdin, termios.TCSAFLUSH, oldtty_attrs)
            print('Paramiko channel to {0} closed.'.format(
                self.logininfo.ip
            ))

    def _read(self):
        '''
        read output of channel
        '''
        return self.channel.recv(1024)

    def _open_connection(self):
        '''
        open connection to server
        '''
        if self.proxy is True:
            ssh_ip, ssh_port = _socket()

            proxy_hostname = self.logininfo.bastion
            proxy_username = self.logininfo.bastion_user
            proxy_port = 22
            k = paramiko.RSAKey.from_private_key_file(self.logininfo.bastion_key)

            # Instantiate a client and connect to the proxy server
            self.proxy_client = paramiko.SSHClient()
            self.proxy_client.set_missing_host_key_policy(
                paramiko.AutoAddPolicy()
            )
            self.proxy_client.connect(
                proxy_hostname,
                port=proxy_port,
                username=proxy_username,
                pkey=k
            )
            # Get the client's transport and open a `direct-tcpip` channel
            # passing the destination hostname:port and the local hostname:port
            self.transport = self.proxy_client.get_transport()
            dest_addr = (self.logininfo.ip, self.logininfo.port)
            local_addr = (ssh_ip, ssh_port)
            self.sock = self.transport.open_channel(
                "direct-tcpip", dest_addr, local_addr
            )
        else:
            ssh_ip = self.logininfo.ip
            ssh_port = self.logininfo.port
        # Create a NEW client and pass this channel to it as the `sock` (along
        # with whatever credentials you need to auth into your REMOTE box
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.client.connect(
            ssh_ip, port=ssh_port,
            username=self.logininfo.ssh_user, timeout=30,
            sock=self.sock, password=self.logininfo.admin_password
        )


def ssh(logininfo):
    '''
    SSH to server
    '''
    with Connection(logininfo, proxy=True) as conn:
        conn.open_shell()


def host(logininfo):
    '''
    SSH to next gen host
    '''
    with Connection(logininfo) as conn:
        conn.channel.send('{0}\n'.format(logininfo.host))
        if logininfo.args.command is None:
            conn.wait_for_prompt(printout=False)
            conn.open_shell()
        else:
            print('### {0} ###'.format(logininfo.hostname))
            conn.exec_command(logininfo.args.command)

# vim: set ft=python:
