import argparse
import sys


def parser(parse=True):
    extraargs = None

    if '--' in sys.argv:
        index = sys.argv.index('--')
        extraargs = ' '.join(sys.argv[index + 1:])
        sys.argv = sys.argv[:index]

    if '--with-spam' in sys.argv:
        with_spam = True
        sys.argv.remove('--with-spam')
    else:
        with_spam = False

    parser = argparse.ArgumentParser(description='Login to cloud servers')

    config = parser.add_argument_group(
        title='Configuration',
        description='Help setting up hammercloud.'
    )

    config.add_argument(
        '--setup-bastion',
        dest='datacenter',
        metavar='datacenter',
        choices=('ALL', 'IAD', 'DFW', 'ORD', 'HKG', 'SYD', 'LON1', 'LON3'),
        type=str,
        help='Setup ssh key and syncprof for specified datacenter.'
    )

    objects = parser.add_argument_group(
        title='Server Info',
        description='Information to help find the server.'
    )
    objects.add_argument(
        'servers',
        metavar='SERVER',
        nargs='*',
        help='Server to login to (uuid or servername)'
    )
    objects.add_argument(
        '--log', '-l',
        metavar='level',
        default=None,
        type=str,
        choices=('debug', 'warning', 'critical'),
        help='display log messages'
    )
    objects.add_argument(
        '--auth', '--account', '-a', '--username',
        dest='username', metavar='username', default=None, nargs='?',
        help='Authenticate manually (username required for using servername)'
    )
    objects.add_argument(
        '--tenantid', default=None, nargs='?',
        help='tenantid to auth with'
    )
    objects.add_argument(
        '--apikey', default=None, nargs='?',
        help='apikey to auth with'
    )
    objects.add_argument(
        '--ipfinder',
        nargs='*', default=[],
        help='Check ipfinder for server'
    )

    actions = parser.add_argument_group(
        title='Actions',
        description='Actions to do with the server.'
    )
    actions.add_argument(
        '--bastion', '-b', type=str,
        choices=('IAD', 'DFW', 'ORD', 'HKG', 'SYD', 'LON1', 'LON3'),
        help='Log into bastion'
    )
    actions.add_argument(
        '--info',
        action='store_true',
        help='Display information about server'
    )
    actions.add_argument(
        '--host',
        dest='use_host',
        action='store_true',
        help='Log into hypervisor'
    )
    actions.add_argument(
        '--webconsole',
        action='store_true',
        help='Log into webconsole on hypervisor'
    )
    actions.add_argument(
        '--nova',
        metavar=('username', 'region'), nargs=2,
        help='Setup supernova (using username)'
    )
    actions.add_argument(
        '-s', '--script',
        default=None,
        help='Script to run on server'
    )
    actions.add_argument(
        '--console',
        action='store_true',
        help='Launch vnc console'
    )
    actions.add_argument(
        '--rescue',
        action='store_true',
        help='Rescue server'
    )
    actions.add_argument(
        '--unrescue',
        action='store_true',
        help='Unrescue server'
    )
    actions.add_argument(
        '--list',
        dest='list_servers', action='store_true',
        help='List servers on account'
    )
    actions.add_argument(
        '-c', '--copy',
        metavar=('source', 'destination'), type=str, nargs=2, default=False,
        help='Transfer file to server'
    )
    actions.add_argument(
        '-C', '--command',
        default=None, type=str,
        help='Command to run on server'
    )
    actions.add_argument(
        '--list-scripts',
        dest='list_scripts', action='store_true',
        help='List scripts that can be run'
    )
    actions.add_argument(
        '--skip-scripts',
        dest='skip_scripts', action='store_true',
        help='Skip running autorun scripts'
    )

    options = parser.add_argument_group(
        title='Extra Options',
        description='Options to modify actions'
    )
    options.add_argument(
        '--no-clean',
        dest='no_clean', action='store_true',
        help="Don't remove script after running it (Default: False)"
    )
    options.add_argument(
        '--port',
        type=int,
        default=0,
        help='ssh port'
    )
    options.add_argument(
        '--password',
        dest='password', type=str, default=None,
        help='ssh password'
    )
    options.add_argument(
        '--ssh-user',
        dest='ssh_user', type=str,
        default='rack', help='ssh user'
    )
    options.add_argument(
        '--version',
        action='store_true',
        help='Get version'
    )
    options.add_argument(
        '--expect-timeout',
        dest='expect_timeout', metavar='time', type=int, default=10,
        help='Time for expect to timeout waiting'
    )
    options.add_argument(
        '-t', '--token',
        default=None, type=str,
        help='Racker token'
    )
    options.add_argument(
        '--private',
        dest='use_private', action='store_true',
        help='Login using the private ip address.'
    )
    options.add_argument(
        '--public',
        dest='use_public', action='store_true',
        help='Force login to use public ip.'
    )
    options.add_argument(
        '--skip-root',
        dest='skip_root', action='store_true',
        help='do not escalate to root'
    )
    options.add_argument(
        '--no-proxy',
        dest='no_proxy', action='store_true',
        help='do not proxy through bastions'
    )
    options.add_argument(
        '--bastion-key',
        dest='bastion_key', type=str, default=None,
        help='SSH key for --setup-bastion'
    )

    if parse is True:
        args = parser.parse_args()
        args.extraargs = extraargs
        args.with_spam = with_spam
        return args, parser
    return None, parser
