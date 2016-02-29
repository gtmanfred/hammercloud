# -*- coding: utf-8 -*-
"""
Allow for calling shell functions directly with logininfo
"""
from __future__ import absolute_import

import hammercloud


def main():
    hcshell = hammercloud.Shell(hammercloud.hcconfig)

    _, parser = hammercloud.parser(parse=False)

    parser.add_argument(
        '--function',
        metavar='FUNCTION',
        type=str,
        help='Function to run from shell',
    )
    args = parser.parse_args()
    getattr(hcshell, args.function)(hammercloud.Server(args.servers[0], args))

if __name__ == '__main__':
    main()
