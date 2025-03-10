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
from dateutil.parser import parse, ParserError
import csv
import os
import re

class WisePLNImporter(Importer):
    def __init__(self, account, lastfour):
        self.account = account
        self.lastfour = lastfour

    def identify(self, file):
        """Regular expression to match Wise csv export's filename"""
        return re.match('statement_1684353_PLN_[0-9-_]*\\.csv', os.path.basename(file.name))

    def extract(self, file):
        entries = []

        with open(file.name) as f:
            for index, row in enumerate(csv.DictReader(f)):
                try:
                    # dayfirst option must be present as the date format of Wise is %d-%m-%Y
                    trans_date = parse(row['Date'], dayfirst=True).date()
                except ParserError:
                    # Handle the parse error if necessary
                    continue
                trans_desc = row['Description']
                trans_amt = row['Amount']

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


class WiseEURImporter(Importer):
    def __init__(self, account, lastfour):
        self.account = account
        self.lastfour = lastfour

    def identify(self, file):
        """Regular expression to match Wise csv export's filename"""
        return re.match('statement_2476408_EUR_[0-9-_]*\\.csv', os.path.basename(file.name))

    def extract(self, file):
        entries = []

        with open(file.name, encoding='utf-8-sig') as f:
            for index, row in enumerate(csv.DictReader(f)):
                try:
                    # dayfirst option must be present as the date format of Wise is %d-%m-%Y
                    trans_date = parse(row['Date'], dayfirst=True).date()
                except ParserError:
                    # Handle the parse error if necessary
                    continue
                trans_desc = row['Description']
                trans_amt = row['Amount']

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


class WiseUSDImporter(Importer):
    def __init__(self, account, lastfour):
        self.account = account
        self.lastfour = lastfour

    def identify(self, file):
        """Regular expression to match Wise csv export's filename"""
        return re.match('statement_2100952_USD_[0-9-_]*\\.csv', os.path.basename(file.name))

    def extract(self, file):
        entries = []

        with open(file.name) as f:
            for index, row in enumerate(csv.DictReader(f)):
                try:
                    # dayfirst option must be present as the date format of Wise is %d-%m-%Y
                    trans_date = parse(row['Date'], dayfirst=True).date()
                except ParserError:
                    # Handle the parse error if necessary
                    continue
                trans_desc = row['Description']
                trans_amt = row['Amount']

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


class WiseIDRImporter(Importer):
    def __init__(self, account, lastfour):
        self.account = account
        self.lastfour = lastfour

    def identify(self, file):
        """Regular expression to match Wise csv export's filename"""
        return re.match('statement_39423616_IDR_[0-9-_]*\\.csv', os.path.basename(file.name))

    def extract(self, file):
        entries = []

        with open(file.name) as f:
            for index, row in enumerate(csv.DictReader(f)):
                try:
                    # dayfirst option must be present as the date format of Wise is %d-%m-%Y
                    trans_date = parse(row['Date'], dayfirst=True).date()
                except ParserError:
                    # Handle the parse error if necessary
                    continue
                trans_desc = row['Description']
                trans_amt = row['Amount']

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
                        Posting(self.account, Amount(trans_amt, 'IDR'))
                    ],
                )
                entries.append(txn)

        return entries
