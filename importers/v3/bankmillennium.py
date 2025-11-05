#!/usr/bin/env python
# -*- coding: utf-8 -*-
###############################################################################
#
# Copyright (c) 2022-2025, Gianluca Fiore
#
###############################################################################

__author__ = "Gianluca Fiore"

from beangulp import Importer, Transaction, Posting, Amount, Flag, Metadata
from datetime import datetime
import csv
import os
import re

class MillenniumPLNImporter(Importer):
    def __init__(self, account, lastfour):
        self.account = account
        self.lastfour = lastfour

    def identify(self, filepath: str):
        """Regular expression to match the Bank Millennium csv export's filename"""
        return re.match(r'Account_activity_[0-9_]*PLN\.csv', os.path.basename(filepath))

    def extract(self, filepath: str):
        entries = []

        with open(filepath) as f:
            for index, row in enumerate(csv.DictReader(f)):
                trans_date = datetime.strptime(row['Transaction date'], '%Y-%m-%d').date()
                trans_desc = row['Transaction Type'] + ' ' + row['Description']
                trans_amt = row['Debits'] if row['Debits'] else row['Credits']

                meta = Metadata(file.name, index)

                txn = Transaction(
                    meta=meta,
                    date=trans_date,
                    flag=Flag.OKAY,
                    payee=trans_desc,
                    narration="",
                    tags=set(),
                    links=set(),
                    postings=[
                        Posting(self.account, Amount(trans_amt, 'PLN'))
                    ],
                )
                entries.append(txn)

        return entries


class MillenniumEURImporter(Importer):
    def __init__(self, account, lastfour):
        self.account = account
        self.lastfour = lastfour

    def identify(self, filepath: str):
        """Regular expression to match the Bank Millennium csv export's filename"""
        return re.match(r'Account_activity_[0-9_]*EUR\.csv', os.path.basename(filepath))

    def extract(self, filepath: str):
        entries = []

        with open(filepath, encoding='utf-8-sig') as f:
            for index, row in enumerate(csv.DictReader(f)):
                trans_date = datetime.strptime(row['Transaction date'], '%Y-%m-%d').date()
                trans_desc = row['Transaction Type'] + ' ' + row['Description']
                trans_amt = row['Debits'] if row['Debits'] else row['Credits']

                meta = Metadata(file.name, index)

                txn = Transaction(
                    meta=meta,
                    date=trans_date,
                    flag=Flag.OKAY,
                    payee=trans_desc,
                    narration="",
                    tags=set(),
                    links=set(),
                    postings=[
                        Posting(self.account, Amount(trans_amt, 'EUR'))
                    ],
                )
                entries.append(txn)

        return entries


class MillenniumUSDImporter(Importer):
    def __init__(self, account, lastfour):
        self.account = account
        self.lastfour = lastfour

    def identify(self, filepath: str):
        """Regular expression to match the Bank Millennium csv export's filename"""
        return re.match(r'Account_activity_[0-9_]*USD\.csv', os.path.basename(filepath))

    def extract(self, filepath: str):
        entries = []

        with open(filepath) as f:
            for index, row in enumerate(csv.DictReader(f)):
                trans_date = datetime.strptime(row['Transaction date'], '%Y-%m-%d').date()
                trans_desc = row['Transaction Type'] + ' ' + row['Description']
                trans_amt = row['Debits'] if row['Debits'] else row['Credits']

                meta = Metadata(file.name, index)

                txn = Transaction(
                    meta=meta,
                    date=trans_date,
                    flag=Flag.OKAY,
                    payee=trans_desc,
                    narration="",
                    tags=set(),
                    links=set(),
                    postings=[
                        Posting(self.account, Amount(trans_amt, 'USD'))
                    ],
                )
                entries.append(txn)

        return entries

