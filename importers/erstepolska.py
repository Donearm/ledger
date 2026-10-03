#!/usr/bin/env python
# -*- coding: utf-8 -*-
###############################################################################
#
# Copyright (c) 2022-2026, Gianluca Fiore
#
###############################################################################

__author__ = "Gianluca Fiore"

from beancount.core import data, amount, flags
from beancount.core.number import D
from beangulp.importer import Importer
from datetime import datetime
import csv
import os
import re

class _ErsteBase(Importer):
    """Shared base for Erste Polska importers (PLN and EUR variants)."""

    def __init__(self, account, lastfour):
        self._account = account
        self.lastfour = lastfour
        self.headers = ['Charge Date', 'Date', 'Description', None, None, 'Amount', 'Balance', 'Index']

    def name(self) -> str:
        return f"ErstePolska_{self.lastfour}"

    def account(self, filepath: str) -> str:
        """Required by beangulp Importer - takes filepath argument."""
        return self._account

    @staticmethod
    def _clean(text):
        """Convert Polish decimal comma to dot."""
        return text.replace(",", ".")

    def _extract_rows(self, filepath):
        entries = []

        with open(filepath, encoding='utf-8') as f:
            for index, row in enumerate(csv.DictReader(f, fieldnames=self.headers)):
                if row['Date'] is None:
                    continue

                # Parse date (DD-MM-YYYY format)
                trans_date = datetime.strptime(row['Date'].strip(), '%d-%m-%Y').date()
                trans_desc = row['Description']
                trans_amt = self._clean(row['Amount'])

                meta = data.new_metadata(filepath, index)

                txn = data.Transaction(
                    meta=meta,
                    date=trans_date,
                    flag=flags.FLAG_OKAY,
                    payee=trans_desc,
                    narration="",
                    tags=set(),
                    links=set(),
                    postings=[
                        data.Posting(
                            account=self._account,
                            units=amount.Amount(D(trans_amt), self.currency),
                            cost=None,
                            price=None,
                            flag=None,
                            meta=None
                        )
                    ],
                )
                entries.append(txn)

        return entries

class ErstePolskaImporter(_ErsteBase):
    """Importer for Erste Polska PLN account CSV exports."""
    currency = 'PLN'

    def identify(self, filepath: str) -> bool:
        """Regular expression to match the Bank Erste Polska csv export's filename"""
        return re.match('[nowa\s]?histor[iy]a?_[0-9]*-[0-9]*-[0-9]*_[0-9]*(_PLN)?\.csv', os.path.basename(filepath))

    def extract(self, filepath: str, existing: data.Entries) -> data.Entries:
        return self._extract_rows(filepath)


class ErstePolskaEURImporter(_ErsteBase):
    """Importer for Erste Polska EUR account CSV exports."""
    currency = 'EUR'

    def identify(self, filepath: str) -> bool:
        """Regular expression to match the Bank Erste Polska csv export's filename"""
        return re.match('[nowa\s]?histor[yi]a?_[0-9]*-[0-9]*-[0-9]*_[0-9]*_EUR\.csv', os.path.basename(filepath))

    def extract(self, filepath: str, existing: data.Entries) -> data.Entries:
        return self._extract_rows(filepath)
