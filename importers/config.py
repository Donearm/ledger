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
import santanderpolska
import kraken
import paypal
import revolut
import wise

CONFIG = [
        #bankmillennium.MillenniumPLNImporter('Assets:Bank-Millennium', '0000'),
        #bankmillennium.MillenniumEURImporter('Assets:Bank-Millennium', '0000'),
        #bankmillennium.MillenniumUSDImporter('Assets:Bank-Millennium', '0000'),
        #santanderpolska.SantanderPolskaImporter('Assets:Bank-Santander', '0000'),
        #kraken.KrakenLedgerImporter('Assets:Kraken', '0000'),
        #kraken.KrakenTradeImporter('Assets:Kraken', '0000'),
        paypal.PaypalImporter('Assets:Paypal', '0000'),
        #revolut.RevolutUSDImporter('Assets:Revolut', '0000'),
        #revolut.RevolutPLNImporter('Assets:Revolut', '0000'),
        #revolut.RevolutEURImporter('Assets:Revolut', '0000'),
        #wise.WiseEURImporter('Assets:Wise', '0000'),
        #wise.WiseIDRImporter('Assets:Wise', '0000'),
        #wise.WisePLNImporter('Assets:Wise', '0000'),
        #wise.WiseUSDImporter('Assets:Wise', '0000'),
        ]
