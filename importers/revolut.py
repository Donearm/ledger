#!/usr/bin/env python
# -*- coding: utf-8 -*-
###############################################################################
#
# Copyright (c) 2022, Gianluca Fiore
#
###############################################################################

__author__ = "Gianluca Fiore"
__copyright__ = ""
__credits__ = ""
__license__ = ""
__version__ = ""
__mantainer__ = ""
__date__ = ""
__email__ = ""
__status__ = ""

from beancount.core.number import D
from beancount.ingest import importer
from beancount.core import account, amount, flags, data
from beancount.core.position import Cost

from dateutil.parser import parse, ParserError

import csv
import os
import re
import logging

LOG = logging.getLogger(__name__)


def _make_identify_regex(currency):
    # Accept both _en_ and _en-us_ (and similar), be case-insensitive for safety
    return re.compile(r'^account-statement_[0-9\-_]*_en(?:-us)?_[a-z0-9]*_{}\.csv$'.format(re.escape(currency)),
                      flags=re.IGNORECASE)


def _parse_amount(value):
    """
    Normalize amount strings:
    - Remove whitespace
    - Remove thousands separators (commas)
    - Handle parentheses as negative amounts, e.g. (1,234.56)
    """
    if value is None:
        return None
    s = str(value).strip()
    if s == '':
        return None
    # Remove any currency symbols or non-digit/.-() characters except minus/period/comma
    # First detect parentheses for negative amounts
    negative = False
    if s.startswith('(') and s.endswith(')'):
        negative = True
        s = s[1:-1].strip()
    # Remove thousands separator commas
    s = s.replace(',', '')
    # If there's still any stray characters, try to keep digits, dot and minus
    s = re.sub(r'[^0-9\.\-]', '', s)
    if s == '':
        return None
    if negative and not s.startswith('-'):
        s = '-' + s
    return s


class RevolutPLNImporter(importer.ImporterProtocol):
    def __init__(self, account, lastfour):
        self.account = account
        self.lastfour = lastfour
        self.headers = ['Type', 'Product', 'Started Date', 'Completed Date', 'Description', 'Amount', 'Fee', 'Currency', 'State', 'Balance']
        self._identify_re = _make_identify_regex('PLN')

    def identify(self, f):
        """Match Revolut csv export's filename for PLN files"""
        return bool(self._identify_re.match(os.path.basename(f.name)))

    def extract(self, f):
        entries = []

        with open(f.name, encoding='utf-8-sig') as fh:
            reader = csv.DictReader(fh)
            for index, row in enumerate(reader):
                # skip empty rows
                if not any(row.values()):
                    continue

                date_text = row.get('Completed Date') or row.get('Completed date') or row.get('CompletedDate')
                if not date_text:
                    LOG.debug("Skipping row %s: missing Completed Date: %r", index, row)
                    continue
                try:
                    trans_date = parse(date_text).date()
                except (ParserError, ValueError) as e:
                    LOG.warning("Skipping row %s in %s: cannot parse date %r: %s", index, f.name, date_text, e)
                    continue

                trans_desc = (row.get('Description') or '').strip()
                trans_amt_raw = row.get('Amount') or ''
                parsed_amt = _parse_amount(trans_amt_raw)
                if parsed_amt is None:
                    LOG.debug("Skipping row %s: cannot parse amount %r", index, trans_amt_raw)
                    continue

                meta = data.new_metadata(f.name, index)

                txn = data.Transaction(
                    meta=meta,
                    date=trans_date,
                    flag=flags.FLAG_OKAY,
                    payee=trans_desc,
                    narration="",
                    tags=set(),
                    links=set(),
                    postings=[],
                )

                txn.postings.append(
                    data.Posting(self.account, amount.Amount(D(parsed_amt), 'PLN'),
                                 None, None, None, None)
                )

                entries.append(txn)

        return entries


class RevolutEURImporter(importer.ImporterProtocol):
    def __init__(self, account, lastfour):
        self.account = account
        self.lastfour = lastfour
        self._identify_re = _make_identify_regex('EUR')

    def identify(self, f):
        """Match Revolut csv export's filename for EUR files"""
        return bool(self._identify_re.match(os.path.basename(f.name)))

    def extract(self, f):
        entries = []

        with open(f.name, encoding='utf-8-sig') as fh:
            for index, row in enumerate(csv.DictReader(fh)):
                if not any(row.values()):
                    continue

                date_text = row.get('Completed Date') or row.get('Completed date') or row.get('CompletedDate')
                if not date_text:
                    LOG.debug("Skipping row %s: missing Completed Date: %r", index, row)
                    continue
                try:
                    trans_date = parse(date_text).date()
                except (ParserError, ValueError) as e:
                    LOG.warning("Skipping row %s in %s: cannot parse date %r: %s", index, f.name, date_text, e)
                    continue

                trans_desc = (row.get('Description') or '').strip()
                trans_amt_raw = row.get('Amount') or ''
                parsed_amt = _parse_amount(trans_amt_raw)
                if parsed_amt is None:
                    LOG.debug("Skipping row %s: cannot parse amount %r", index, trans_amt_raw)
                    continue

                meta = data.new_metadata(f.name, index)

                txn = data.Transaction(
                    meta=meta,
                    date=trans_date,
                    flag=flags.FLAG_OKAY,
                    payee=trans_desc,
                    narration="",
                    tags=set(),
                    links=set(),
                    postings=[],
                )

                txn.postings.append(
                    data.Posting(self.account, amount.Amount(D(parsed_amt), 'EUR'),
                                 None, None, None, None)
                )

                entries.append(txn)

        return entries


class RevolutUSDImporter(importer.ImporterProtocol):
    def __init__(self, account, lastfour):
        self.account = account
        self.lastfour = lastfour
        self._identify_re = _make_identify_regex('USD')

    def identify(self, f):
        """Match Revolut csv export's filename for USD files"""
        return bool(self._identify_re.match(os.path.basename(f.name)))

    def extract(self, f):
        entries = []

        with open(f.name, encoding='utf-8-sig') as fh:
            for index, row in enumerate(csv.DictReader(fh)):
                if not any(row.values()):
                    continue

                date_text = row.get('Completed Date') or row.get('Completed date') or row.get('CompletedDate')
                if not date_text:
                    LOG.debug("Skipping row %s: missing Completed Date: %r", index, row)
                    continue
                try:
                    trans_date = parse(date_text).date()
                except (ParserError, ValueError) as e:
                    LOG.warning("Skipping row %s in %s: cannot parse date %r: %s", index, f.name, date_text, e)
                    continue

                trans_desc = (row.get('Description') or '').strip()
                trans_amt_raw = row.get('Amount') or ''
                parsed_amt = _parse_amount(trans_amt_raw)
                if parsed_amt is None:
                    LOG.debug("Skipping row %s: cannot parse amount %r", index, trans_amt_raw)
                    continue

                meta = data.new_metadata(f.name, index)

                txn = data.Transaction(
                    meta=meta,
                    date=trans_date,
                    flag=flags.FLAG_OKAY,
                    payee=trans_desc,
                    narration="",
                    tags=set(),
                    links=set(),
                    postings=[],
                )

                txn.postings.append(
                    data.Posting(self.account, amount.Amount(D(parsed_amt), 'USD'),
                                 None, None, None, None)
                )

                entries.append(txn)

        return entries


class RevolutTRYImporter(importer.ImporterProtocol):
    def __init__(self, account, lastfour):
        self.account = account
        self.lastfour = lastfour
        self._identify_re = _make_identify_regex('TRY')

    def identify(self, f):
        """Match Revolut csv export's filename for TRY files"""
        return bool(self._identify_re.match(os.path.basename(f.name)))

    def extract(self, f):
        entries = []

        with open(f.name, encoding='utf-8-sig') as fh:
            for index, row in enumerate(csv.DictReader(fh)):
                if not any(row.values()):
                    continue

                # Fixed typo: use 'Completed Date'
                date_text = row.get('Completed Date') or row.get('Completed date') or row.get('CompletedDate')
                if not date_text:
                    LOG.debug("Skipping row %s: missing Completed Date: %r", index, row)
                    continue
                try:
                    trans_date = parse(date_text).date()
                except (ParserError, ValueError) as e:
                    LOG.warning("Skipping row %s in %s: cannot parse date %r: %s", index, f.name, date_text, e)
                    continue

                trans_desc = (row.get('Description') or '').strip()
                trans_amt_raw = row.get('Amount') or ''
                parsed_amt = _parse_amount(trans_amt_raw)
                if parsed_amt is None:
                    LOG.debug("Skipping row %s: cannot parse amount %r", index, trans_amt_raw)
                    continue

                meta = data.new_metadata(f.name, index)

                txn = data.Transaction(
                    meta=meta,
                    date=trans_date,
                    flag=flags.FLAG_OKAY,
                    payee=trans_desc,
                    narration="",
                    tags=set(),
                    links=set(),
                    postings=[],
                )

                txn.postings.append(
                    data.Posting(self.account, amount.Amount(D(parsed_amt), 'TRY'),
                                 None, None, None, None)
                )

                entries.append(txn)

        return entries