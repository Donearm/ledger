#!/usr/bin/env python
# -*- coding: utf-8 -*-
###############################################################################
#
# Copyright (c) 2022, Gianluca Fiore
#
###############################################################################
#
# Follow the example at https://github.com/fxtlabs/beansoup/blob/master/beansoup/importers/csv.py

__author__ = "Gianluca Fiore"
__copyright__ = ""
__credits__ = ""
__license__ = ""
__version__ = ""
__mantainer__ = ""
__date__ = ""
__email__ = ""
__status__ = ""

import sys
import csv
import io
import logging
import re

from beancount.ingest import importer
from beancount.core import data, amount
from beancount.core import account_types as atypes
#import beangulp

#class Importer(beangulp.Importer):
class Importer(importer.ImporterProtocol):

    def __init__(self, account, currency='PLN', basename=None,
            first_day=None, filename_regexp='', account_types=None):
        """Create a new importer for the given account

        Args:
            account: an account string
            account_types: an AccountTypes object or None to use the default ones
            basename: Optional, the name of the new files
            currency: the currency for all extracted transactions
            filename_regexp: a regular expression string used to match the basename (no path) of the target file
            first_day: an int in [1,28] as the first day of the statement/billing period or None. If None, the file date will be the date of the last extracted entry, otherwise the date of the end of the monthly period containing the last extracted entry
            """
        self.filename_re = re.compile(filename_regexp)
        self.account = account
        self.currency = currency.upper()
        self.basename = basename
        self.first_day = first_day
        self.account_sign = atypes.get_account_sign(account, account_types)

    def name(self) -> str:
        """This method provides an unique id for each importer instance"""
        return '{}: "{}"'.format(super().name(), 'Bank Millennium')

    def identify(self, file) -> bool: # Compulsory to implement
        """This method returns true if this importer can handle the given file"""

    def extract(self, file):
        """This method is called to attempt to extract Beancount directives from the file content.
        It must create the directives by instantiating the objects defined in beancount.core.data and
        return them"""
        rows = self.parse(file)
        rows, error_lineno = sort_rows(rows)
        new_entries = []
        if len(rows) == 0:
            return new_entries

        for index, row in enumerate(rows):
            posting = data.Posting(
                    self.account,
                    amount.Amount(row.amount, self.currency),
                    None, None, None, None)
            # Use the final positional index rather than the lineno of the row because
            # bean-extract will sort the entries returned by its importers; doing that
            # using the original line number of the parsed CSV row would undo all the
            # effort we did to find their correct chronological order.
            meta = data.new_metadata(file.name, index)
            payee = None
            narration = row.description
            entry = data.Transaction(
                    meta,
                    row.date,
                    self.FLAG,
                    payee,
                    narration,
                    data.EMPTY_SET,
                    data.EMPTY_SET,
                    [posting])
            new_entries.append(entry)
            print(new_entries)

    def parse(self, file):
        """The parse method opens a csv file and return its rows"""
        with open(file, 'r') as csv_file:
            reader = csv.reader(csv_file)
            try:
                rows = [parse_row(row, reader.line_num) for row in reader if row]
            except (csv.Error, ValueError) as exc:
                logging.error('{}:{}: {}'.format(csv_file.name, reader.line_num, exc))
                rows = []
        print(rows)
        return rows

    def file_account(self):
        """This method returns the root account associated with this importer"""

    def date(self) -> str:
        """If a date can be extracted from the statement's contents it can be returned here"""

    def file_name(self) -> str:
        """This method is used for the importer to provide a nicer name to file the download under,
        renaming the original file as named by the bank"""


def sort_rows(rows):
    """Sort the rows of a CSV file.
    This function can sort the rows of a CSV file in ascending chronological order
    such that the balance values of each row match the sequence of transactions.
    Args:
      rows: A list of objects with a lineno, date, amount, and balance attributes.
    Returns
      A pair with a sorted list of rows and an error. The error is None if the function
      could find an ordering agreeing with the balance values of its rows; otherwise,
      it is the line number in the CSV file corresponding to the first row not agreeing
      with its balance value.
    """
    if len(rows) <= 1:
        return rows, None

    # If there is more than one row sharing the earliest date of the statement, we do not
    # know for sure which one came first, so we have a number of opening balances and we
    # have to find out which one is the right one.
    first_date = rows[0].date
    opening_balances = [row.balance - row.amount for row in itertools.takewhile(
        lambda r: r.date == first_date, rows)]

    error_lineno = 0
    for opening_balance in opening_balances:
        # Given one choice of opening balance, we try to find an ordering of the rows
        # that agrees with the balance amount they show
        stack = list(reversed(rows))
        prev_balance = opening_balance
        unbalanced_rows = []
        balanced_rows = []
        while stack:
            row = stack.pop()
            # Check if the current row balances with the previous one
            if prev_balance + row.amount == row.balance:
                # The current row is in the correct chronological order
                balanced_rows.append(row)
                prev_balance = row.balance
                if unbalanced_rows:
                    # Put unbalanced rows back on the stack so they get another chance
                    stack.extend(unbalanced_rows)
                    unbalanced_rows.clear()
            else:
                # The current row is out of chronological order
                if unbalanced_rows and unbalanced_rows[0].date != row.date:
                    # No ordering can be found that agrees with the
                    # balance values of the rows
                    break
                # Skip the current row for the time being
                unbalanced_rows.append(row)
        if len(balanced_rows) == len(rows):
            return balanced_rows, None
        error_lineno = unbalanced_rows[0].lineno

    # The rows could not be ordered in any way that would agree with the balance values
    return rows, error_lineno


def main():
    i = Importer('Bank-Millennium')
    i.extract('/home/gianluca/Downloads/Account_activity_20220209_113629.csv')

if __name__ == '__main__':
    status = main()
    sys.exit(status)
