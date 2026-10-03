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
from dateutil.parser import parse
from datetime import date
import csv
import os
import re
from typing import Optional

class _KrakenBase(Importer):
    """Shared base for Kraken importers."""
    
    def __init__(self, account, lastfour, file_pattern):
        self._account = account
        self.lastfour = lastfour
        self.file_pattern = file_pattern

    def name(self) -> str:
        return f"Kraken_{self.lastfour}"

    def account(self, filepath: str) -> str:
        """Required by beangulp Importer."""
        return self._account

    def date(self, filepath: str) -> Optional[date]:
        """Extract transaction date from file."""
        try:
            with open(filepath, encoding='utf-8') as f:
                reader = csv.DictReader(f)
                first_row = next(reader, None)
                if first_row and first_row.get('time'):
                    return parse(first_row['time']).date()
        except (FileNotFoundError, ValueError):
            pass
        return None

    def filename(self, filepath: str) -> str:
        return os.path.basename(filepath)

    def _extract_ledger(self, filepath):
        """Common extraction logic for ledger/trade files."""
        entries = []

        with open(filepath, encoding='utf-8') as f:
            for index, row in enumerate(csv.DictReader(f)):
                trans_date = parse(row['time']).date()
                
                # Handle withdrawals that may have txid or refid
                txid = row.get('txid') or ''
                refid = row.get('refid') or ''
                trans_type = row.get('type', '')
                
                if txid:
                    trans_desc = f"{trans_type} {txid}"
                else:
                    trans_desc = f"{trans_type} {refid}"

                trans_amt = row.get('amount', '')
                trans_asset = row.get('asset', 'XXX')
                trans_fee = row.get('fee', '0')

                meta = data.new_metadata(filepath, index)

                txn = data.Transaction(
                    meta=meta,
                    date=trans_date,
                    flag=flags.FLAG_OKAY,
                    payee=trans_desc,
                    narration=row.get('descr', ''),
                    tags=set(),
                    links=set(),
                    postings=[],
                )

                # Main posting
                txn.postings.append(
                    data.Posting(
                        account=self._account,
                        units=amount.Amount(D(trans_amt), trans_asset),
                        cost=None,
                        price=None,
                        flag=None,
                        meta=None
                    )
                )
                
                # Fee posting if applicable
                if float(trans_fee) != 0:
                    txn.postings.append(
                        data.Posting(
                            account="Expenses:Trading:Fees",
                            units=amount.Amount(D(trans_fee), trans_asset),
                            cost=None,
                            price=None,
                            flag=None,
                            meta=None
                        )
                    )
                
                entries.append(txn)

        return entries

class KrakenLedgerImporter(_KrakenBase):
    """Importer for Kraken ledger CSV exports."""
    
    def __init__(self, account, lastfour):
        super().__init__(account, lastfour, r'ledgers\.csv')

    def identify(self, filepath: str) -> bool:
        """Match Kraken ledger CSV export filenames."""
        basename = os.path.basename(filepath)
        return bool(re.match(self.file_pattern, basename))

    def extract(self, filepath: str, existing: data.Entries) -> data.Entries:
        return self._extract_ledger(filepath)

class KrakenTradeImporter(_KrakenBase):
    """Importer for Kraken trades CSV exports."""
    
    def __init__(self, account, lastfour):
        super().__init__(account, lastfour, r'trades\.csv')

    def identify(self, filepath: str) -> bool:
        """Match Kraken trades CSV export filenames."""
        basename = os.path.basename(filepath)
        return bool(re.match(self.file_pattern, basename))

    def extract(self, filepath: str, existing: data.Entries) -> data.Entries:
        return self._extract_ledger(filepath)
