#!/usr/bin/env python
# -*- coding: utf-8 -*-
###############################################################################
#
# Copyright (c) 2024-2026, Gianluca Fiore
#
###############################################################################

from beangulp.importer import Importer

from beancount.core.number import D
from beancount.core import amount, flags, data

from dateutil.parser import parse

import csv
import os
import re

class N26Importer(Importer):
    def __init__(self, account, lastfour):
        self._account = account
        self.lastfour = lastfour
        self.headers = ['Booking Date', 'Value Date', 'Partner Name', 'Partner Iban', 'Type', 'Payment Reference', 'Account Name', 'Amount (EUR)', 'Original Amount', 'Original Currency', 'Exchange Rate']

    def name(self) -> str:
        return 'importers.n26'

    def identify(self, filepath: str) -> bool:
        """Regular expression to match N26 csv export's filename"""

        return re.match('MainAccount_[0-9-]*_[0-9-]*.csv',
                        os.path.basename(filepath)) is not None

    def account(self, filepath) -> str:
        return self._account

    def extract(self, filepath, existing=None):
        entries = []

        with open(filepath) as fh:
            for index, row in enumerate(csv.DictReader(fh, fieldnames=self.headers)):
                if index == 0:
                    # skip the embedded header line
                    continue

                trans_date = parse(row['Booking Date'], yearfirst=True, fuzzy=True)
                trans_desc = row['Partner Name']
                trans_amt = row['Amount (EUR)']

                meta = data.new_metadata(filepath, index)

                txn = data.Transaction(
                        meta=meta,
                        date=trans_date,
                        flag=flags.FLAG_OKAY,
                        payee=trans_desc,
                        narration='',
                        tags=set(),
                        links=set(),
                        postings=[],
                )

                txn.postings.append(
                        data.Posting(self._account,
                                     amount.Amount(D(trans_amt), 'EUR'),
                                     None, None, None, None)
                        )

                entries.append(txn)

        return entries
