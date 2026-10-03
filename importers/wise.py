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

class _WiseBase(Importer):
    """Shared base for Wise importers (multi-currency support)."""
    
    def __init__(self, account, lastfour, currency):
        self._account = account
        self.lastfour = lastfour
        self.currency = currency

    def name(self) -> str:
        return f"Wise_{self.lastfour}_{self.currency}"

    def account(self, filepath: str) -> str:
        """Required by beangulp Importer."""
        return self._account

    def date(self, filepath: str) -> Optional[date]:
        """Extract transaction date from file."""
        try:
            with open(filepath, encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                first_row = next(reader, None)
                if first_row and first_row.get('Date'):
                    return parse(first_row['Date'], dayfirst=True).date()
        except (FileNotFoundError, ParserError):
            pass
        return None

    def filename(self, filepath: str) -> str:
        return os.path.basename(filepath)

    def _extract_rows(self, filepath, currency):
        entries = []

        with open(filepath, encoding='utf-8-sig') as f:
            for index, row in enumerate(csv.DictReader(f)):
                try:
                    date_str = row.get('Date')
                    if not date_str:
                        continue
                    # Wise uses DD-MM-YYYY format
                    trans_date = parse(date_str, dayfirst=True).date()
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
                            units=amount.Amount(D(trans_amt_str), currency),
                            cost=None,
                            price=None,
                            flag=None,
                            meta=None
                        )
                    ],
                )
                entries.append(txn)

        return entries


class WisePLNImporter(_WiseBase):
    """Importer for Wise PLN account CSV exports."""
    
    def __init__(self, account, lastfour):
        super().__init__(account, lastfour, 'PLN')
        self.file_pattern = r'statement_1684353_PLN_[0-9-_]*\.csv'

    def identify(self, filepath: str) -> bool:
        """Match Wise PLN CSV export filenames."""
        basename = os.path.basename(filepath)
        return bool(re.match(self.file_pattern, basename))

    def extract(self, filepath: str, existing: data.Entries) -> data.Entries:
        return self._extract_rows(filepath, self.currency)


class WiseEURImporter(_WiseBase):
    """Importer for Wise EUR account CSV exports."""
    
    def __init__(self, account, lastfour):
        super().__init__(account, lastfour, 'EUR')
        self.file_pattern = r'statement_2476408_EUR_[0-9-_]*\.csv'

    def identify(self, filepath: str) -> bool:
        """Match Wise EUR CSV export filenames."""
        basename = os.path.basename(filepath)
        return bool(re.match(self.file_pattern, basename))

    def extract(self, filepath: str, existing: data.Entries) -> data.Entries:
        return self._extract_rows(filepath, self.currency)


class WiseUSDImporter(_WiseBase):
    """Importer for Wise USD account CSV exports."""
    
    def __init__(self, account, lastfour):
        super().__init__(account, lastfour, 'USD')
        self.file_pattern = r'statement_2100952_USD_[0-9-_]*\.csv'

    def identify(self, filepath: str) -> bool:
        """Match Wise USD CSV export filenames."""
        basename = os.path.basename(filepath)
        return bool(re.match(self.file_pattern, basename))

    def extract(self, filepath: str, existing: data.Entries) -> data.Entries:
        return self._extract_rows(filepath, self.currency)


class WiseIDRImporter(_WiseBase):
    """Importer for Wise IDR account CSV exports."""
    
    def __init__(self, account, lastfour):
        super().__init__(account, lastfour, 'IDR')
        self.file_pattern = r'statement_39423616_IDR_[0-9-_]*\.csv'

    def identify(self, filepath: str) -> bool:
        """Match Wise IDR CSV export filenames."""
        basename = os.path.basename(filepath)
        return bool(re.match(self.file_pattern, basename))

    def extract(self, filepath: str, existing: data.Entries) -> data.Entries:
        return self._extract_rows(filepath, self.currency)
