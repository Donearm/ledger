#!/usr/bin/env python
# -*- coding: utf-8 -*-
###############################################################################
#
# Copyright (c) 2022, Gianluca Fiore
#
# Main importer file for beancount, calling all accounts' relative importers
#
###############################################################################

__author__ = "Gianluca Fiore"
__copyright__ = ""
__credits__ = ""
__license__ = ""
__version__ = ""
__mantainer__ = ""
__date__ = ""
__email__ = ""
__status__ = ""

import sys
from myimporters.bank import millennium

CONFIG = [
        millennium.Importer()
        ]

def __main__():
    continue

if __name__ == '__main__':
    status = main()
    sys.exit(status)

