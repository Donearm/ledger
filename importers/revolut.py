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
from dateutil.parser import parse, ParserError
from datetime import date
import csv
import os
import re
from typing import Optional

class _RevolutBase(Importer):
    """Shared base for Revolut importers (multi-currency support)."""
    
    def __init__(self, account, lastfour, currency):
        self._account = account
        self.lastfour = lastfour
        self.currency = currency
        self.headers = ['Type', 'Product', 'Started Date', 'Completed Date', 'Description', 'Amount', 'Fee', 'Currency', 'State', 'Balance']

    def name(self) -> str:
        return f"Revolut_{self.lastfour}_{self.currency}"

    def account(self, filepath: str) -> str:
        """Required by beangulp Importer."""
        return self._account

    def date(self, filepath: str) -> Optional[date]:
        """Extract transaction date from file."""
        try:
            with open(filepath, encoding='utf-8-sig') as f:
                reader = csv.DictReader(f, fieldnames=self.headers)
                next(reader)  # Skip header
                first_row = next(reader, None)
                if first_row and first_row.get('Completed Date'):
                    return parse(first_row['Completed Date']).date()
        except (FileNotFoundError, ParserError):
            pass
        return None

    def filename(self, filepath: str) -> str:
        return os.path.basename(filepath)

    def _extract_rows(self, filepath):
        entries = []

        with open(filepath, encoding='utf-8-sig') as f:
            reader = csv.DictReader(f, fieldnames=self.headers)
            
            for index, row in enumerate(reader):
                try:
                    completed_date_str = row.get('Completed Date')
                    if not completed_date_str:
                        continue
                    trans_date = parse(completed_date_str).date()
                except ParserError:
                    continue
                
                trans_desc = row.get('Description', '') or ''
                trans_amt_str = row.get('Amount', '') or ''

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
                            units=amount.Amount(D(trans_amt_str), self.currency),
                            cost=None,
                            price=None,
                            flag=None,
                            meta=None
                        )
                    ],
                )
                entries.append(txn)

        return entries


class RevolutPLNImporter(_RevolutBase):
    """Importer for Revolut PLN account CSV exports."""
    
    def __init__(self, account, lastfour):
        super().__init__(account, lastfour, 'PLN')

    def identify(self, filepath: str) -> bool:
        """Match Revolut PLN CSV export filenames."""
        basename = os.path.basename(filepath)
        return bool(re.match(r'account-statement_[0-9-_]*_en-us_[a-z0-9]*_PLN.csv', basename))

    def extract(self, filepath: str, existing: data.Entries) -> data.Entries:
        return self._extract_rows(filepath)


class RevolutEURImporter(_RevolutBase):
    """Importer for Revolut EUR account CSV exports."""
    
    def __init__(self, account, lastfour):
        super().__init__(account, lastfour, 'EUR')

    def identify(self, filepath: str) -> bool:
        """Match Revolut EUR CSV export filenames."""
        basename = os.path.basename(filepath)
        return bool(re.match(r'account-statement_[0-9-_]*_en-us_[a-z0-9]*_EUR.csv', basename))

    def extract(self, filepath: str, existing: data.Entries) -> data.Entries:
        return self._extract_rows(filepath)


class RevolutUSDImporter(_RevolutBase):
    """Importer for Revolut USD account CSV exports."""
    
    def __init__(self, account, lastfour):
        super().__init__(account, lastfour, 'USD')

    def identify(self, filepath: str) -> bool:
        """Match Revolut USD CSV export filenames."""
        basename = os.path.basename(filepath)
        return bool(re.match(r'account-statement_[0-9-_]*_en-us_[a-z0-9]*_USD.csv', basename))

    def extract(self, filepath: str, existing: data.Entries) -> data.Entries:
        return self._extract_rows(filepath)


class RevolutTRYImporter(_RevolutBase):
    """Importer for Revolut TRY account CSV exports."""
    
    def __init__(self, account, lastfour):
        super().__init__(account, lastfour, 'TRY')

    def identify(self, filepath: str) -> bool:
        """Match Revolut TRY CSV export filenames."""
        basename = os.path.basename(filepath)
        return bool(re.match(r'account-statement_[0-9-_]*_en_TRY_[a-z0-9]*\.csv', basename))

    def extract(self, filepath: str, existing: data.Entries) -> data.Entries:
        return self._extract_rows(filepath)
