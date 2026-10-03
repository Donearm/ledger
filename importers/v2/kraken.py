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

from dateutil.parser import parse

import csv
import os
import re

class KrakenLedgerImporter(importer.ImporterProtocol):
    def __init__(self, account, lastfour):
        self.account = account
        self.lastfour = lastfour

    def identify(self, f):
        """Regular expression to match Kraken ledger csv export's filename"""

        return re.match('ledgers\.csv', os.path.basename(f.name))

    def extract(self, f):
        entries = []

        with open(f.name) as f:
            for index, row in enumerate(csv.DictReader(f)):
                print(index, row)
                trans_date = parse(row['time']).date()
                #trans_desc = row['type'] + ' ' + row['txid'] or row['refid']

                # In some Kraken's entries, the withdrawals for instance, there's no txid but only a refid column
                # 'type' is always the action performed (trade/deposit/withdrawal)
                if row['txid']:
                    trans_desc = row['type'] + ' ' + row['txid']
                else:
                    trans_desc = row['type'] + ' ' + row['refid']

                trans_amt = row['amount']
                trans_asset = row['asset']
                trans_fees = row['fee']

                meta = data.new_metadata(f.name, index)

                txn = data.Transaction(
                        meta = meta,
                        date = trans_date,
                        flag = flags.FLAG_OKAY,
                        payee = trans_desc,
                        narration = "",
                        tags = set(),
                        links = set(),
                        postings = [],
                        )

                txn.postings.append(
                        data.Posting(self.account, amount.Amount(D(trans_amt), trans_asset),
                            None, None, None, None)
                        )
                
                entries.append(txn)

        return entries

class KrakenTradeImporter(importer.ImporterProtocol):
    def __init__(self, account, lastfour):
        self.account = account
        self.lastfour = lastfour

    def identify(self, f):
        """Regular expression to match Kraken trades csv export's filename"""

        return re.match('trades\.csv', os.path.basename(f.name))

    def extract(self, f):
        entries = []

        with open(f.name) as f:
            for index, row in enumerate(csv.DictReader(f)):
                print(index, row)
                trans_date = parse(row['time']).date()
                trans_desc = row['type'] + ' ' + row['ordertype'] + ' ' + row['txid']
                trans_amt = row['vol']
                trans_asset = row['pair']
                trans_fees = row['fee']

                meta = data.new_metadata(f.name, index)

                txn = data.Transaction(
                        meta = meta,
                        date = trans_date,
                        flag = flags.FLAG_OKAY,
                        payee = trans_desc,
                        narration = "",
                        tags = set(),
                        links = set(),
                        postings = [],
                        )

                txn.postings.append(
                        data.Posting(self.account, amount.Amount(D(trans_amt), trans_asset),
                            None, None, None, None)
                        )
                
                entries.append(txn)

        return entries
