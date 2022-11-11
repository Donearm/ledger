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

class RevolutPLNImporter(importer.ImporterProtocol):
    def __init__(self, account, lastfour):
        self.account = account
        self.lastfour = lastfour

    def identify(self, f):
        """Regular expression to match Revolut csv export's filename"""

        return re.match('account-statement_[0-9-_]*_en_PLN_[a-z0-9]*\.csv', os.path.basename(f.name))

    def extract(self, f):
        entries = []

        with open(f.name) as f:
            for index, row in enumerate(csv.DictReader(f)):
                trans_date = parse(row['Completed Date']).date()
                trans_desc = row['Description']
                trans_amt = row['Amount']

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
                        data.Posting(self.account, amount.Amount(D(trans_amt), 'PLN'),
                            None, None, None, None)
                        )
                
                entries.append(txn)

        return entries


class RevolutEURImporter(importer.ImporterProtocol):
    def __init__(self, account, lastfour):
        self.account = account
        self.lastfour = lastfour

    def identify(self, f):
        """Regular expression to match Revolut csv export's filename"""

        return re.match('account-statement_[0-9-_]*_en_EUR_[a-z0-9]*\.csv', os.path.basename(f.name))

    def extract(self, f):
        entries = []

        with open(f.name, encoding='utf-8-sig') as f:
            for index, row in enumerate(csv.DictReader(f)):
                trans_date = parse(row['Completed Date']).date()
                trans_desc = row['Description']
                trans_amt = row['Amount']

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

class RevolutUSDImporter(importer.ImporterProtocol):
    def __init__(self, account, lastfour):
        self.account = account
        self.lastfour = lastfour

    def identify(self, f):
        """Regular expression to match Revolut csv export's filename"""

        return re.match('account-statement_[0-9-_]*_en_USD_[a-z0-9]*\.csv', os.path.basename(f.name))

    def extract(self, f):
        entries = []

        with open(f.name) as f:
            for index, row in enumerate(csv.DictReader(f)):
                trans_date = parse(row['Completed Date']).date()
                trans_desc = row['Description']
                trans_amt = row['Amount']

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
                        data.Posting(self.account, amount.Amount(D(trans_amt), 'USD'),
                            None, None, None, None)
                        )
                
                entries.append(txn)

        return entries
