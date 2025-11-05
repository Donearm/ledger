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

class SantanderPolskaPLNImporter(Importer):
    def __init__(self, account, lastfour):
        self.account = account
        self.lastfour = lastfour
        self.headers = ['Charge Date', 'Date', 'Description', None, None, 'Amount', 'Balance', 'Index']

    def identify(self, filepath: str):
        """Regular expression to match the Bank Santander Polska csv export's filename"""
        return re.match('[nowa\s]?histor[iy]a?_[0-9]*-[0-9]*-[0-9]*_[0-9]*(_PLN)?\.csv', os.path.basename(filepath))

    def extract(self, filepath: str):
        entries = []

        with open(filepath) as f:
            for index, row in enumerate(csv.DictReader(f, fieldnames=self.headers)):
                trans_date = datetime.strptime(row['Date'], '%Y-%m-%d').date()
                trans_desc = row['Description']
                trans_amt = row['Amount'].replace(",", ".")

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


class SantanderPolskaEURImporter(Importer):
    def __init__(self, account, lastfour):
        self.account = account
        self.lastfour = lastfour
        self.headers = ['Charge Date', 'Date', 'Description', None, None, 'Amount', 'Balance', 'Index']

    def identify(self, filepath: str):
        """Regular expression to match the Bank Santander Polska csv export's filename"""
        return re.match('[nowa\s]?histor[yi]a?_[0-9]*-[0-9]*-[0-9]*_[0-9]*_EUR\.csv', os.path.basename(filepath))

    def extract(self, filepath: str):
        entries = []

        with open(filepath) as f:
            for index, row in enumerate(csv.DictReader(f, fieldnames=self.headers)):
                trans_date = datetime.strptime(row['Date'], '%Y-%m-%d').date()
                trans_desc = row['Description']
                trans_amt = row['Amount'].replace(",", ".")

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
