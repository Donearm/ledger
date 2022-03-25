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

from beancount.core.number import D
from beancount.ingest import importer
from beancount.core import account, amount, flags, data
from beancount.core.position import Cost

from dateutil.parser import parse

import csv
import os
import re

class PaypalImporter(importer.ImporterProtocol):
    def __init__(self, account, lastfour):
        self.account = account
        self.lastfour = lastfour

    def identify(self, f):
        """Regular expression to match the Paypal csv export's filename"""

        # Paypal exports needs to be renamed to this
        return re.match('Paypal.csv', os.path.basename(f.name))

    def extract(self, f):
        entries = []

        # opening the Paypal file with this encoding as otherwise there's a \ufeff character at the beginning that doesn't make the 'Date' key being recognized by DictReader
        with open(f.name, encoding='utf-8-sig') as f:
            for index, row in enumerate(csv.DictReader(f)):
                trans_date = parse(row['Date']).date()
                trans_desc = row['Type'] + ' ' + row['Note']
                trans_amt = row['Balance']
                trans_currency = row['Currency']

                meta = data.new_metadata(f.name, index)

                txn = data.Transaction(
                        meta = meta,
                        date = trans_date,
                        flag = flags.FLAG_OKAY,
                        payee = trans_desc,
                        narration = "",
                        tags = set(),
                        links = set(),
                        postings = [],
                        )

                txn.postings.append(
                        data.Posting(self.account, amount.Amount(D(trans_amt), trans_currency),
                            None, None, None, None)
                        )

                entries.append(txn)

        return entries
