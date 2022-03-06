# Prices for ledger

## EUR to PLN

Unfortunately PLN is not available in the free tier of the Financial Times api.

An XML file can be downloaded with all the historical exchange rates (from 1999) [here](https://www.ecb.europa.eu/stats/policy_and_exchange_rates/euro_reference_exchange_rates/html/pln.xml). Once cut the header and the footer tags, it can be parsed with:

```sh
awk 'BEGIN {FS = "\""} {print $2, $4}' pln.xml > eur_to_pln.prices
```

# pricehist

Best tool to download prices from a range of sources. The basic syntax for beancount is:

```sh
pricehist fetch alphavantage EUR/MUR -s 2018-01-01 -e 2019-01-01 -o beancount > eur_to_mur.prices
```
