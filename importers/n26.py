#!/usr/bin/env python
# -*- coding: utf-8 -*-
###############################################################################
#
# Copyright (c) 2024-2026, Gianluca Fiore
#
###############################################################################

__author__ = "Gianluca Fiore"
__copyright__ = "Copyright (c) 2024-2026, Gianluca Fiore"
__credits__ = []
__license__ = "MIT"
__version__ = "1.1.0"
__maintainer__ = "Gianluca Fiore"
__date__ = "2026"
__email__ = ""
__status__ = "Production"

from beancount.core import data, amount, flags
from beancount.core.number import D
from beangulp.importer import Importer
from dateutil.parser import parse, ParserError
from datetime import date
import csv
import os
import re
from typing import Optional

class N26Importer(Importer):
    """Beancount importer for N26 CSV exports."""
    
    def __init__(self, account, lastfour):
        self._account = account
        self.lastfour = lastfour
        self.headers = ['Booking Date', 'Value Date', 'Partner Name', 'Partner Iban', 'Type', 'Payment Reference', 'Account Name', 'Amount (EUR)', 'Original Amount', 'Original Currency', 'Exchange Rate']

    def name(self) -> str:
        return f"N26_{self.lastfour}"

    def account(self, filepath: str) -> str:
        """Required by beangulp Importer."""
        return self._account

    def identify(self, filepath: str) -> bool:
        """Match N26 CSV export filenames."""
        basename = os.path.basename(filepath)
        return bool(re.match(r'MainAccount_[0-9-]*_[0-9-]*\.csv', basename))

    def date(self, filepath: str) -> Optional[date]:
        """Extract transaction date from file."""
        try:
            with open(filepath, encoding='utf-8') as f:
                reader = csv.DictReader(f, fieldnames=self.headers)
                next(reader)  # Skip header
                first_row = next(reader, None)
                if first_row and first_row.get('Booking Date'):
                    return parse(first_row['Booking Date'], yearfirst=True, fuzzy=True).date()
        except (FileNotFoundError, ParserError):
            pass
        return None

    def filename(self, filepath: str) -> str:
        return os.path.basename(filepath)

    def extract(self, filepath: str, existing: data.Entries) -> data.Entries:
        entries = []

        with open(filepath, encoding='utf-8') as f:
            for index, row in enumerate(csv.DictReader(f, fieldnames=self.headers)):
                try:
                    booking_date_str = row.get('Booking Date', '')
                    if not booking_date_str:
                        continue
                    trans_date = parse(booking_date_str, yearfirst=True, fuzzy=True).date()
                except ParserError:
                    continue
                
                trans_desc = row.get('Partner Name', '') or ''
                trans_amt_str = row.get('Amount (EUR)', '')

                meta = data.new_metadata(filepath, index)

                txn = data.Transaction(
                    meta=meta,
                    date=trans_date,
                    flag=flags.FLAG_OKAY,
                    payee=trans_desc,
                    narration=row.get('Payment Reference', ''),
                    tags=set(),
                    links=set(),
                    postings=[
                        data.Posting(
                            account=self._account,
                            units=amount.Amount(D(trans_amt_str), 'EUR'),
                            cost=None,
                            price=None,
                            flag=None,
                            meta=None
                        )
                    ],
                )
                entries.append(txn)

        return entries
