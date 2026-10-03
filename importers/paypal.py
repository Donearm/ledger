#!/usr/bin/env python
# -*- coding: utf-8 -*-
###############################################################################
#
# Copyright (c) 2022-2026, Gianluca Fiore
#
###############################################################################

__author__ = "Gianluca Fiore"
__copyright__ = "Copyright (c) 2022-2026, Gianluca Fiore"
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

class PaypalImporter(Importer):
    """Beancount importer for PayPal CSV exports."""
    
    def __init__(self, account, lastfour):
        self._account = account
        self.lastfour = lastfour

    def name(self) -> str:
        return f"PayPal_{self.lastfour}"

    def account(self, filepath: str) -> str:
        """Required by beangulp Importer."""
        return self._account

    def identify(self, filepath: str) -> bool:
        """Match PayPal CSV export filenames.
        
        Note: PayPal exports need to be renamed to exactly 'Paypal.csv'
        """
        basename = os.path.basename(filepath)
        return bool(re.match(r'Paypal\.csv', basename))

    def date(self, filepath: str) -> Optional[date]:
        """Extract transaction date from file."""
        try:
            with open(filepath, encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                first_row = next(reader, None)
                if first_row and first_row.get('Date'):
                    return parse(first_row['Date']).date()
        except (FileNotFoundError, ParserError):
            pass
        return None

    def filename(self, filepath: str) -> str:
        return os.path.basename(filepath)

    def extract(self, filepath: str, existing: data.Entries) -> data.Entries:
        entries = []

        # UTF-8-BOM encoding to handle \ufeff character at the beginning
        with open(filepath, encoding='utf-8-sig') as f:
            for index, row in enumerate(csv.DictReader(f)):
                try:
                    date_str = row.get('Date', '')
                    if not date_str:
                        continue
                    trans_date = parse(date_str).date()
                except ParserError:
                    continue
                
                bank_name = row.get('Bank Name', '') or ''
                bank_account = row.get('Bank Account', '') or ''
                description = row.get('Description', '') or ''
                trans_desc = ' '.join(filter(None, [bank_name, bank_account, description]))
                
                trans_amt_str = row.get('Net', '')
                trans_currency = row.get('Currency', 'USD')

                meta = data.new_metadata(filepath, index)

                txn = data.Transaction(
                    meta=meta,
                    date=trans_date,
                    flag=flags.FLAG_OKAY,
                    payee=trans_desc,
                    narration='',
                    tags=set(),
                    links=set(),
                    postings=[
                        data.Posting(
                            account=self._account,
                            units=amount.Amount(D(trans_amt_str), trans_currency),
                            cost=None,
                            price=None,
                            flag=None,
                            meta=None
                        )
                    ],
                )
                entries.append(txn)

        return entries
