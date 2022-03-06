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
import re

from beancount.core.number import D
from beancount.ingest.importers import csv
from beancount.ingest.importers.csv import Col


class USBImporter(csv.Importer):
    """
    Importer for U.S. Bank
    """

    def __init__(self, account, file_pattern):
        self.file_pattern = file_pattern
        super().__init__({
            Col.DATE: 'Date',
            Col.NARRATION: 'Name',
            Col.NARRATION2: 'Memo',
            Col.AMOUNT: 'Amount',
        }, account, 'USD', [
            '^"Date","Transaction","Name","Memo","Amount"$',
        ])

    def identify(self, file):
        if file.mimetype() != "text/csv":
            return False

        if re.search(self.file_pattern, os.path.basename(file.name)):
            return True

        return False
