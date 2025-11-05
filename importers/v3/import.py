#!/usr/bin/env python
# -*- coding: utf-8 -*-
###############################################################################
#
# Copyright (c) 2025, Gianluca Fiore
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

# Import bank's importers
from bankmillennium import MillenniumPLNImporter, MillenniumEURImporter, MillenniumUSDImporter
from revolut import RevolutPLNImporter, RevolutEURImporter, RevolutUSDImporter
from santander import SantanderPolskaPLNImporter, SantanderPolskaEURImporter
from wise import WisePLNImporter, WiseEURImporter, WiseUSDImporter
from beangulp import Ingest
import sys

importers = (
        MillenniumPLNImporter(
            name="Assets:Bank-Millennium",
            currency="PLN",
            patterns={}
            )
        )


if __name__ == '__main__':
    ingest = Ingest(importers)
    ingest()

from beangulp import Importer, Transaction, Posting, Amount, Flag, Metadata
