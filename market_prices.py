#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Script by https://github.com/barrucadu/hledger-scripts

from html.parser import HTMLParser
import json
import sys
import time
import urllib.request
from datetime import date, timedelta

def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)

def get_coinbase(base, currency):
    req = urllib.request.Request(
        "https://api.coinbase.com/v2/prices/{}-{}/spot/".format(base, currency),
        headers={"CB-VERSION": "2018-05-25"})
    with urllib.request.urlopen(req) as response:
        resp = json.load(response)
        return resp['data']['amount']


def ft_find_price(url, currency):
    class FTPriceFinder(HTMLParser):
        def __init__(self):
            HTMLParser.__init__(self)
            self.found = None
            self.isnext = False

        def handle_data(self, data):
            if data == 'Price ({})'.format(currency):
                self.isnext = True
            elif self.isnext:
                self.found = data
                self.isnext = False

    req = urllib.request.Request(url)
    with urllib.request.urlopen(req) as response:
        html = response.read().decode('utf-8')
        finder = FTPriceFinder()
        finder.feed(html)
        if finder.found is None:
            raise Exception("could not find price")
        else:
            return finder.found


def get_ft_currency(base, currency):
    return ft_find_price(
        "https://markets.ft.com/data/currencies/tearsheet/summary?s={}{}".format(base, currency),
        currency)


def get_ft_fund(isin, currency):
    return ft_find_price(
        "https://markets.ft.com/data/funds/tearsheet/summary?s={}:{}".format(isin, currency),
        currency)


config = json.load(sys.stdin)
symbols = config.get('symbols', {})
for commodity, cconfig in config.get('commodities', {}).items():
    try:
        try:
            provider = cconfig['provider']
        except KeyError:
            raise Exception("missing provider")

        currency = cconfig.get('currency', 'PLN')

        if provider == 'coinbase':
            rate = get_coinbase(
                cconfig.get('base', commodity),
                currency)
        elif provider == 'ft_currency':
            rate = get_ft_currency(
                cconfig.get('base', commodity),
                currency)
        elif provider == 'ft_fund':
            rate = get_ft_fund(
                cconfig.get('isin', commodity),
                currency)
        else:
            raise Exception("unknown provider '{}'".format(provider))

        #if sys.argv[1]:
        #    try:
        #        date = time.strftime(sys.argv[1])
        #    except:
        #date = time.strftime('%Y-%m-%d')
        start_date = date(2013, 1, 1)
        end_date = date(2022, 2, 1)
        for single_date in daterange(start_date, end_date):
            if currency in symbols:
                #print('P {} {} {}{}'.format(date, commodity, symbols[currency], rate))
                print('P {} {} {}{}'.format(single_date, commodity, symbols[currency], rate))
            else:
                #print('P {} {} {} {}'.format(date, commodity, rate, currency))
                print('P {} {} {} {}'.format(single_date, commodity, rate, currency))
    except Exception as e:
        print("; error processing commodity '{}': {}".format(commodity, e))
