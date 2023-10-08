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

class SantanderPolskaImporter(importer.ImporterProtocol):
    def __init__(self, account, lastfour):
        self.account = account
        self.lastfour = lastfour
        self.headers = ['Charge Date', 'Date', 'Description', None, None, 'Amount', 'Balance', 'Index']

    def identify(self, f):
        """Regular expression to match the Bank Santander Polska csv export's filename"""

        # Santander Polska doesn't make a difference between credit card's statements and saving account's ones in the name
        # Therefore, the format is identical
        return re.match('[nowa\s]?histor[iy]a?_[0-9]*-[0-9]*-[0-9]*_[0-9]*(_PLN)?\.csv', os.path.basename(f.name))

    def extract(self, f):
        entries = []

        with open(f.name) as f:
            #for index, row in enumerate(csv.DictReader(f)):
            for index, row in enumerate(csv.DictReader(f, fieldnames=self.headers)):
                trans_date = parse(row['Date'], dayfirst=True).date()
                trans_desc = row['Description']
                # Santander Polska use periods to separate thousands and commas to separate integer with decimal numbers
                # As beancount's D function doesn't support this yet (https://github.com/beancount/beancount/issues/204)
                # it is simpler to just replace the commas with periods in the amount's column
                trans_amt = row['Amount'].replace(",", ".")

                #trans_date = parse(row[1]).date()
                #trans_desc = row[2]
                #trans_amt = row[5]

                #trans_date = parse(row['Transaction date']).date()
                #trans_desc = row['Transaction Type'] + ' ' + row['Description']
                #if row['Debits']:
                #    trans_amt = row['Debits']
                #else:
                #    trans_amt = row['Credits']

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

class SantanderPolskaEURImporter(importer.ImporterProtocol):
    def __init__(self, account, lastfour):
        self.account = account
        self.lastfour = lastfour
        self.headers = ['Charge Date', 'Date', 'Description', None, None, 'Amount', 'Balance', 'Index']

    def identify(self, f):
        """Regular expression to match the Bank Santander Polska csv export's filename"""

        # Santander Polska doesn't make a difference between credit card's statements and saving account's ones in the name
        # Therefore, the format is identical
        # For EUR account, add '_EUR' at the end of filename to differentiate them from the PLN one
        return re.match('[nowa\s]?histor[yi]a?_[0-9]*-[0-9]*-[0-9]*_[0-9]*_EUR\.csv', os.path.basename(f.name))

    def extract(self, f):
        entries = []

        with open(f.name) as f:
            #for index, row in enumerate(csv.DictReader(f)):
            for index, row in enumerate(csv.DictReader(f, fieldnames=self.headers)):
                trans_date = parse(row['Date'], dayfirst=True).date()
                trans_desc = row['Description']
                # Santander Polska use periods to separate thousands and commas to separate integer with decimal numbers
                # As beancount's D function doesn't support this yet (https://github.com/beancount/beancount/issues/204)
                # it is simpler to just replace the commas with periods in the amount's column
                trans_amt = row['Amount'].replace(",", ".")

                #trans_date = parse(row[1]).date()
                #trans_desc = row[2]
                #trans_amt = row[5]

                #trans_date = parse(row['Transaction date']).date()
                #trans_desc = row['Transaction Type'] + ' ' + row['Description']
                #if row['Debits']:
                #    trans_amt = row['Debits']
                #else:
                #    trans_amt = row['Credits']

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
