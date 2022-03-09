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

from beancount.ingest import importer
#import beangulp

#class Importer(beangulp.Importer):
class Importer(importer.ImporterProtocol):

    def name(self) -> str:
        """This method provides an unique id for each importer instance"""
        return '{}: "{}"'.format(super().name(), 'Bank Millennium')

    def identify(self, file) -> bool:
        # Compulsory to implement
        """This method returns true if this importer can handle the given file"""

    def extract(self):
        """This method is called to attempt to extract Beancount directives from the file content.
        It must create the directives by instantiating the objects defined in beancount.core.data and
        return them"""
        with open('/home/gianluca/Downloads/Account_activity_20220209_113629.csv', 'r') as csv_file:
            reader = csv.reader(csv_file)

            for row in reader:
                print(row)

            csv_file.close()


    def file_account(self):
        """This method returns the root account associated with this importer"""

    def date(self) -> str:
        """If a date can be extracted from the statement's contents it can be returned here"""

    def file_name(self) -> str:
        """This method is used for the importer to provide a nicer name to file the download under,
        renaming the original file as named by the bank"""

def parse(file, dialect, parse_row):
    with io.StringIO(file.contents()) as stream:
        reader = csv.reader(stream, dialect)
        try:
            rows = [parse_row(row, reader.line_num) for row in reader if row]
        except (csv.Error, ValueError) as exc:
            logging.error('{}:{}: {}'.format(file.name, reader.line_num, exc))
            rows = []
        return rows

def main():
    i = Importer()
    parse('/home/gianluca/Downloads/Account_activity_20220209_113629.csv', '', '')

if __name__ == '__main__':
    status = main()
    sys.exit(status)
