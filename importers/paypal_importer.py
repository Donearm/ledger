#!/usr/bin/env python
# -*- coding: utf-8 -*-
###############################################################################

__author__ = ""
__copyright__ = ""
__credits__ = "https://github.com/ThomasdenH/beangulp-importers"
__license__ = ""
__version__ = ""
__mantainer__ = ""
__date__ = ""
__email__ = ""
__status__ = ""

from enum import Enum
from os import path
from typing import Any, List, Optional
from beancount.core import data, number, position
from beangulp.importers import csvbase
import csv as pycsv
import datetime

english = {
    "date": "Date",
    "time": "Time",
    "timezone": "TimeZone",
    "name": "Name",
    "typ": "Type",
    "currency": "Currency",
    "amount": "Net",
    "balance": "Balance",
    "subject": "Subject",
    "bank_transfer": [
        "Bank Deposit to PP Account",
        "Algemene opname",
    ],  # TODO: < Translate
    "general_currency_conversion": "General Currency Conversion",
    "transaction_id": "Transaction ID",
    "reference_transaction_id": "Reference Txn ID",
}


class MergeType(Enum):
    BANK_TRANSFER = 0
    CURRENCY_CONVERSION = 1


pycsv.register_dialect("paypaldialect", delimiter=",")


class CommaAmount(csvbase.Column):
    def parse(self, value: str):
        return number.D(value.replace(",", "."))


class Importer(csvbase.Importer):
    encoding = "utf-8-sig"
    dialect = "paypaldialect"

    def __init__(
        self,
        base_currency: str,
        account: str,
        bank_account: Optional[str],
        lang=english,
    ) -> None:
        self.lang = lang
        self.columns = {
            "date": csvbase.Date(lang["date"], "%d/%m/%Y"),
            "payee": csvbase.Column(lang["name"]),
            "amount": CommaAmount(lang["amount"]),
            "currency": csvbase.Column(lang["currency"]),
            "balance_unreg": CommaAmount(lang["balance"]),
            "narration": csvbase.Column(lang["subject"]),
            "typ": csvbase.Column(lang["typ"]),
            "time": csvbase.Column(lang["time"]),
            "timezone": csvbase.Column(lang["timezone"]),
            "transaction_id": csvbase.Column(lang["transaction_id"]),
            "reference_transaction_id": csvbase.Column(
                lang["reference_transaction_id"]
            ),
        }
        self.bank_account = bank_account
        super().__init__(account, base_currency)

    def filename(self, filepath: str) -> str:
        return "paypal." + path.basename(filepath)

    def identify(remap, file: str) -> bool:
        f = open(file)
        is_correct = path.basename(f.name) == "Download.CSV"
        f.close()
        return is_correct

    def extract(self, filepath: str, existing: List[Any]) -> List[Any]:
        with open(filepath, encoding=self.encoding) as file:
            contents = file.read()
            if contents == "" or contents.isspace():
                return []

        entries = super().extract(filepath, existing)
        read = self.read(filepath)

        iter = list(zip(entries, read))

        new_entries = []

        i = 0
        while i < len(iter):
            entry, row = iter[i]
            merges = []
            while i + 1 < len(iter):
                next_entry, next_row = iter[i + 1]
                if next_row.reference_transaction_id == row.transaction_id:

                    if next_row.typ in self.lang["bank_transfer"]:
                        merges.append(MergeType.BANK_TRANSFER)
                    elif next_row.typ == self.lang["general_currency_conversion"]:
                        merges.append(MergeType.CURRENCY_CONVERSION)
                    else:
                        print(
                            "unsupported transaction type that references a previous transaction:",
                            next_row.typ,
                        )

                    entry = entry._replace(
                        postings=entry.postings + next_entry.postings
                    )
                    i += 1
                else:
                    break

            # Add an expense posting, derive from the first transaction.
            paypal_account_posting = entry.postings[0]
            payee_account = paypal_account_posting.account
            # Maybe the payee has been set, otherwise use a placeholder
            if payee_account == self.account(filepath):
                payee_account = "Expenses:UnknownAccount"
            first_entry = paypal_account_posting._replace(
                # TODO: For clarity, use Income when money is coming in.
                account=payee_account,
                units=-paypal_account_posting.units,
            )
            entry = entry._replace(postings=[first_entry] + entry.postings[1:])

            # If there was not a bank transfer, the money is coming from the paypal account. Add this posting (use the orinal posting).
            if not MergeType.BANK_TRANSFER in merges:
                paypal_account_posting = paypal_account_posting._replace(
                    account=self.account(filepath)
                )
                entry = entry._replace(
                    postings=entry.postings[:1]
                    + [paypal_account_posting]
                    + entry.postings[1:]
                )

            # The first transaction is the primary transaction. The others should be merged
            while len(merges) > 0:
                if merges[-1] == MergeType.BANK_TRANSFER:
                    # The lowest posting is from a bank transfer. Invert the amount and add add a transfer posting.
                    amount = -entry.postings[-1].units
                    bank_transfer_posting = data.Posting(
                        self.bank_account,
                        amount,
                        None,
                        None,
                        None,
                        None,
                    )
                    entry = entry._replace(
                        postings=entry.postings[:-1] + [bank_transfer_posting]
                    )
                    merges = merges[:-1]
                elif merges[-1] == MergeType.CURRENCY_CONVERSION:
                    # Assume each currency conversion comes in pairs.
                    assert (
                        len(merges) >= 2 and merges[-2] == MergeType.CURRENCY_CONVERSION
                    )

                    # The bottom two postings correspond to the conversion.

                    # One currency gets subtracted, another added. Assume the second-last posting is the native currency.
                    # Other situations are probably possible, but not currently handled.
                    assert entry.postings[-2].units[1] == self.currency

                    # The first entry is the expense. See if the units is identical, in which case we can simply add the
                    # cost spec.
                    assert entry.postings[0].units == entry.postings[-1].units

                    # Add the cost spec
                    entry.postings[0] = entry.postings[0]._replace(
                        cost=position.CostSpec(
                            None,
                            -entry.postings[-2].units[0],
                            self.currency,
                            None,
                            None,
                            None,
                        )
                    )

                    # Remove the currency conversions.
                    entry = entry._replace(postings=entry.postings[:-2])

                    merges = merges[:-2]

            new_entries.append(entry)
            i += 1

        if len(iter) > 0:
            entry, row = iter[-1]
            if row.balance_unreg is not None:
                date = row.date + datetime.timedelta(days=1)
                units = data.Amount(row.balance_unreg, self.currency)
                meta = data.new_metadata(filepath, entry.meta["lineno"])
                new_entries.append(
                    data.Balance(meta, date, self.account(filepath), units, None, None)
                )

        return new_entries
