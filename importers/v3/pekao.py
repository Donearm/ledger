#!/usr/bin/env python
# -*- coding: utf-8 -*-
###############################################################################
#
# Copyright (c) 2026, Gianluca Fiore
#
###############################################################################

from beangulp.importer import Importer

from beancount.core.number import D
from beancount.core import amount, flags, data

from dateutil.parser import parse

import csv
import os
import re


class PekaoImporter(Importer):
    def __init__(self, account, lastfour):
        self._account = account
        self.lastfour = lastfour
        self.headers = ['Data księgowania', 'Data waluty', 'Nadawca / Odbiorca', 'Adres nadawcy / odbiorcy', 'Rachunek źródłowy', 'Rachunek docelowy', 'Tytułem', 'Kwota operacji', 'Waluta', 'Numer referencyjny', 'Typ operacji', 'Kategoria']

    def name(self) -> str:
        """Unique dotted name for this importer, used for logging and dedup"""
        return 'importers.pekao'

    def identify(self, filepath: str) -> bool:
        """Regular expression to match the Bank Pekao csv export's filename"""

        return re.match('Lista_operacji_[0-9]*_[0-9]*\\.csv',
                        os.path.basename(filepath)) is not None

    def account(self, filepath) -> str:
        """Protocol method: the account this importer files statements to"""
        return self._account

    @staticmethod
    def _clean(text):
        """Locale-normalise a Polish-formatted decimal string for beancount to understand"""
        if text is None:
            return None
        return (text.replace('\xa0', '')
                    .replace(' ', '')
                    .replace('+', '')
                    .replace(',', '.'))

    def extract(self, filepath, existing=None):
        entries = []

        with open(filepath) as fh:
            # Here delimiter is necessary because Pekao uses ; instead of , as separator...
            for index, row in enumerate(csv.DictReader(fh, delimiter=';',
                                                       fieldnames=self.headers)):
                if index == 0:
                    # skip the embedded header line
                    continue

                trans_date = parse(row['Data waluty'], dayfirst=True).date()
                trans_desc = row['Tytułem'] or row['Nadawca / Odbiorca'] or ''
                trans_amt = row['Kwota operacji']
                if trans_amt is None:
                    continue

                meta = data.new_metadata(filepath, index)

                txn = data.Transaction(
                        meta=meta,
                        date=trans_date,
                        flag=flags.FLAG_OKAY,
                        payee=trans_desc.strip(),
                        narration=(row['Nadawca / Odbiorca'] or '') + ' ' +
                                  (row['Typ operacji'] or ''),
                        tags=set(),
                        links=set(),
                        postings=[],
                )

                txn.postings.append(
                        data.Posting(self._account,
                                     amount.Amount(D(self._clean(trans_amt)), 'PLN'),
                                     None, None, None, None)
                        )

                entries.append(txn)

        return entries
