#!/usr/bin/env python
# -*- coding: utf-8 -*-
###############################################################################
#
# Copyright (c) 2024, Gianluca Fiore
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

from dateutil.parser import parse, ParserError

import csv
import os
import re

class N26Importer(importer.ImporterProtocol):
    def __init__(self, account, lastfour):
        self.account = account
        self.lastfour = lastfour
        self.headers = ['Booking Date', 'Value Date', 'Partner Name', 'Partner Iban', 'Type', 'Payment Reference', 'Account Name', 'Amount (EUR)', 'Original Amount', 'Original Currency', 'Exchange Rate']

    def identify(self, f):
        """Regular expression to match N26 csv export's filename"""

        return re.match('MainAccount_[0-9-]*_[0-9-]*.csv', os.path.basename(f.name))

    def extract(self, f):
        entries = []

        with open(f.name) as f:
            for index, row in enumerate(csv.DictReader(f, fieldnames=self.headers)):
                #try:
                #    trans_date = parse(row['Completed Date']).date()
                #except ParserError as e:
                #    print(repr(e))
                #finally:
                #    print("This is absurd")
                #    print(index)
                #    print(row)
                trans_date = parse(row['Booking Date'], yearfirst=True, fuzzy=True)
                trans_desc = row['Partner Name']
                trans_amt = row['Amount (EUR)']

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
                        data.Posting(self.account, amount.Amount(D(trans_amt), 'EUR'),
                            None, None, None, None)
                        )
                
                entries.append(txn)

        return entries


