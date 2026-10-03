#!/usr/bin/env python
# -*- coding: utf-8 -*-
###############################################################################
#
# Copyright (c) 2026, Gianluca Fiore
#
###############################################################################

__author__ = "Gianluca Fiore"
__copyright__ = "Copyright (c) 2026, Gianluca Fiore"
__credits__ = []
__license__ = "MIT"
__version__ = "1.1.0"
__maintainer__ = "Gianluca Fiore"
__date__ = "2026"
__email__ = ""
__status__ = "Production"

from beancount.core.number import D
from beancount.core import amount, flags, data
from beancount.core.position import Cost

from beangulp.importer import Importer

from datetime import date
from dateutil.parser import parse

import csv
import os
import re
from typing import List, Optional, Set, Tuple

class PekaoImporter(Importer):
    """Beancount importer for Bank Pekao CSV exports (beancount v3 compatible).
    
    Migrates from beancount.ingest to beangulp framework.
    See: https://sgoel.dev/posts/moving-from-beancount-2x-to-3x/
    """
    
    def __init__(self, account: str, lastfour: str) -> None:
        self._account = account
        self.lastfour = lastfour
        self.headers = [
            'Data księgowania', 'Data waluty', 'Nadawca / Odbiorca',
            'Adres nadawcy / odbiorcy', 'Rachunek źródłowy', 'Rachunek docelowy',
            'Tytułem', 'Kwota operacji', 'Waluta', 'Numer referencyjny',
            'Typ operacji', 'Kategoria'
        ]

    def name(self) -> str:
        """Return importer name."""
        return f"Pekao_{self.lastfour}"

    def account(self, filepath: str) -> str:
        """Required by beangulp Importer - takes filepath argument."""
        return self._account

    def identify(self, filepath: str) -> bool:
        """Match Bank Pekao CSV export filenames."""
        basename = os.path.basename(filepath)
        return bool(re.match(r'Lista_operacji_[0-9]*_[0-9]*\.csv', basename))

    def date(self, filepath: str) -> Optional[date]:
        """Extract transaction date from file.
        
        Returns the valuation date from the first transaction.
        """
        try:
            with open(filepath, encoding='utf-8') as f:
                reader = csv.DictReader(f, delimiter=';', fieldnames=self.headers)
                next(reader)  # Skip header
                first_row = next(reader, None)
                if first_row and first_row.get('Data waluty'):
                    return parse(first_row['Data waluty'], dayfirst=True).date()
        except (FileNotFoundError, ValueError):
            pass
        return None

    def filename(self, filepath: str) -> str:
        """Return the original filename."""
        return os.path.basename(filepath)

    @staticmethod
    def _clean(text: Optional[str]) -> Optional[str]:
        """Convert Polish decimal format (comma) to beancount format (dot)."""
        if text is None:
            return None
        return (text.replace('\xa0', '')  # Non-breaking space
                    .replace(' ', '')
                    .replace('+', '')
                    .replace(',', '.'))

    @staticmethod
    def _build_narration(row: dict) -> str:
        """Build narration from available fields."""
        counterparty = row.get('Nadawca / Odbiorca', '') or ''
        operation_type = row.get('Typ operacji', '') or ''
        
        if operation_type and counterparty:
            return f"{counterparty} | {operation_type}"
        elif counterparty:
            return counterparty
        else:
            return row.get('Tytułem', '') or ''

    def extract(self, filepath: str, existing: data.Entries) -> data.Entries:
        """Extract transactions from a CSV file.
        
        Args:
            filepath: String path to CSV file
            existing: Existing entries (for duplicate detection if needed)
            
        Returns:
            List of Transaction objects
        """
        entries: data.Entries = []

        with open(filepath, encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter=';', fieldnames=self.headers)
            
            for index, row in enumerate(reader):
                if index == 0:
                    # Skip the embedded header line that's first in the file
                    continue
                
                # Parse transaction date (use valuta date as this represents settlement)
                valute_date_str = row.get('Data waluty')
                if not valute_date_str:
                    continue
                    
                try:
                    trans_date = parse(valute_date_str, dayfirst=True).date()
                except ValueError:
                    continue
                
                # Build payee and narration
                trans_desc = row.get('Tytułem') or row.get('Nadawca / Odbiorca') or ''
                trans_amt_str = row.get('Kwota operacji')
                
                if trans_amt_str is None:
                    continue

                # Create metadata
                meta = data.new_metadata(filepath, index + 1)

                # Build transaction with explicit keyword arguments (v3 safety)
                txn = data.Transaction(
                    meta=meta,
                    date=trans_date,
                    flag=flags.FLAG_OKAY,
                    payee=trans_desc.strip(),
                    narration=self._build_narration(row),
                    tags=set(),
                    links=set(),
                    postings=[]
                )
                
                # Clean amount and ensure PLN currency
                cleaned_amount = self._clean(trans_amt_str)
                if cleaned_amount is None:
                    continue
                    
                txn.postings.append(
                    data.Posting(
                        account=self._account,  # ← FIXED: was self.account()
                        units=amount.Amount(D(cleaned_amount), 'PLN'),
                        cost=None,
                        price=None,
                        flag=None,
                        meta=None
                    )
                )
                
                entries.append(txn)

        return entries
