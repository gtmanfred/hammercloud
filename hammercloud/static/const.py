# -*- coding: utf-8 -*-
"""
Constants
"""
import re

# Datacenters for bastion vips
DCS = {}

# Bastions in each datacenter
CBASTS = {}


# Colors
GREEN = '\033[92m'
RESET = '\033[0m'
RED = '\033[91m'
YELLOW = '\033[93m'
WHITE = '\033[97m'
CYAN = '\033[96m'
PINK = '\033[95m'
BLUE = '\033[94m'

# RE colors
REGREEN = re.escape('\033[92m')
RERESET = re.escape('\033[0m')
RERED = re.escape('\033[91m')
REYELLOW = re.escape('\033[93m')
REWHITE = re.escape('\033[97m')
RECYAN = re.escape('\033[96m')
REPINK = re.escape('\033[95m')
REBLUE = re.escape('\033[94m')
