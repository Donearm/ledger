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

import sys

import beangulp

class Importer(beangulp.Importer):

    def name(self) -> str:
        """This method provides an unique id for each importer instance"""

    def identify():
        # Compulsory to implement
        """This method returns true if this importer can handle the given file"""

    def extract():
        """This method is called to attempt to extract Beancount directives from the file content.
        It must create the directives by instantiating the objects defined in beancount.core.data and
        return them"""

    def file_account():
        """This method returns the root account associated with this importer"""

    def date():
        """If a date can be extracted from the statement's contents it can be returned here"""

    def file_name():
        """This method is used for the importer to provide a nicer name to file the download under,
        renaming the original file as named by the bank"""


if __name__ == '__main__':
    status = main()
    sys.exit(status)

