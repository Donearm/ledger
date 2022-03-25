#!/usr/bin/env python
# -*- coding: utf-8 -*-
###############################################################################
#
# Copyright (c) 2022, Gianluca Fiore
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

import os
import sys

# beancount doesn't run from this directory
sys.path.append(os.path.dirname(__file__))

import bankmillennium
import paypal

CONFIG = [
        #bankmillennium.MillenniumPLNImporter('Assets:Bank-Millennium', '0000'),
        #bankmillennium.MillenniumEURImporter('Assets:Bank-Millennium', '0000'),
        #bankmillennium.MillenniumUSDImporter('Assets:Bank-Millennium', '0000'),
        paypal.PaypalImporter('Assets:Paypal', '0000'),
        ]
