# Ledger

<!-- vim-markdown-toc GFM -->

* [What is this](#what-is-this)
	* [Folder organization](#folder-organization)
* [Beancount](#beancount)
	* [Reports](#reports)
* [Ledger to beancount](#ledger-to-beancount)
* [Importers](#importers)
	* [Kraken](#kraken)

<!-- vim-markdown-toc -->

# What is this

My double entry accounting files. Plus, a collection of commands, queries, and
rules to analyze the transactions with (h)ledger and beancount.

## Folder organization

* `csv` = csv files from various bank and financial institutions
* `exports` = where exported documents for interoperability are. Usually from ledger to gnucash via csv
* `importers` = Beancount importers
* `journals` = original (h)ledger files
* `prices` = the dir where are saved commodities' prices
* `rules` = rules for importing csv/pdf files into (h)ledger

# Beancount

## Reports

A few useful commands for reporting to be used either with `bean-query` or with `fava`

List of expenses for the current month:

```sql
SELECT
    account, sum(cost(position)) as total, month
WHERE
    account ~ "Expenses:*" and year = YEAR(today()) and month = MONTH(today())
GROUP BY month, account
ORDER BY total, account DESC
```

Monthly expenses report:

```sql
SELECT
    year, month, account, sum(position)
FROM
    date > 2015-01-01 AND date < 2016-02-29
WHERE
    account ~ "Expenses"
    GROUP BY year, month, account
    ORDER by year, month, account
    FLATTEN
```

Expenses in a given year in a specific currency:

```sql
SELECT
    year, month, root(account, 1) as account, sum(position) as total
  FROM
    date > 2013-01-01 AND date < 2021-12-31
  WHERE
     account ~ "Expenses" OR
     account ~ "Liabilities:Mortgage" OR
     account ~ "Liabilities:Loan" OR
     account ~ "Income"
  GROUP BY year, month, account
  ORDER BY year, month, account
  FLATTEN
```

Select all transactions in an account matching a specific word:

```sql
SELECT
  date, account, position, balance
WHERE
  account ~ 'Ship';
```

Expenses for each month of a selected year, in a specific currency:

```sql
SELECT
  MONTH(date) AS month,
  SUM(COST(position)) AS balance
WHERE
   account ~ 'Expenses:' AND
   currency = 'EUR' AND
   YEAR(date) = 2021
GROUP BY 1
ORDER BY 1;
```

It is easy from this example to check the earnings by month ("Assets:") or by 
checking the expenses of a specific category using a sub-account of "Expenses".

Show all accounts' balance, converted into a specific currency:

```sql
SELECT
  account, convert(sum(position), 'PLN')
GROUP BY 1
ORDER BY 1;
```

# Ledger to beancount

A Perl [script](https://github.com/beancount/ledger2beancount) is available.

It unfortunately fails at transactions whose amount is registered as:

```
EUR-1000
```

To clean up the ledger file before using the conversion script, a couple of commands in Vimscript can be used:

```vim
:%s/\(EUR\)\([-+]\)\([0-9.]*\)/\2\3 \1/g
```

And

```vim
:%s/+\([0-9.]*\)/\1/g
```

The latter is necessary to remove the `+` sign in front of the amount as the script fails at those. The `-` sign is instead fine to keep.

# Importers

## Kraken

Kraken's history can be downloaded at [https://www.kraken.com/u/history/export](https://www.kraken.com/u/history/export).
It gets requested and after a few minutes of processing can be actually downloaded.

There will be 2 types of files, trades and ledgers. The format for trades is:

```csv
"txid","ordertxid","pair","time","type","ordertype","price","cost","fee","vol","margin","misc","ledgers"
"TFWNEI-DWFNM-DPKYGT","OTVM57-ZCIA2-HXL3O6","XXMRZEUR","2017-11-12 19:04:13.6946","buy","market",103.22000000,10.32200000,0.02683720,0.10000000,0.00000000,"","L3ZB4N-T33RW-ATJMAH,LKFD5C-OY5LR-PWEQW2"
"THXBOQ-UXHAI-HKJOSZ","OGMGAA-LRUV7-HI56WX","XREPZEUR","2017-11-12 19:17:16.4198","buy","limit",15.00000,15.00000,0.02400,1.00000000,0.00000,"","LXEQNM-EZERP-JWXZBJ,L4ER7P-XHIOQ-VSUANG"
"TCA24X-HIIPC-FJFIF5","OA7BMG-MUB5A-M6NM6I","DASHEUR","2017-11-23 20:10:26.1312","buy","market",484.000000,14.520000,0.037752,0.03000000,0.000000,"","L4PCMC-XQP4O-M7YKAT,LYOKCB-SNR2F-4VRKPU"
```

Which can be cleaned up with:

```awk
awk 'BEGIN {FS = ","} {print $3" "$4" "$5" "$6" "$7" "$8" "$9}'
```

The ledgers format is:

```csv
"txid","refid","time","type","subtype","aclass","asset","amount","fee","balance"
"","QCC7MTT-4Q44K5-ULXBU6","2017-11-09 08:50:00","deposit","","currency","ZEUR",100.0000,0.0000,""
"LJUEZM-UA5DG-GOKDCG","QCC7MTT-4Q44K5-ULXBU6","2017-11-09 09:03:01","deposit","","currency","ZEUR",100.0000,0.0000,100.0000
"LKFD5C-OY5LR-PWEQW2","TFWNEI-DWFNM-DPKYGT","2017-11-12 19:04:13","trade","","currency","XXMR",0.1000000000,0.0000000000,0.1000000000
"L3ZB4N-T33RW-ATJMAH","TFWNEI-DWFNM-DPKYGT","2017-11-12 19:04:13","trade","","currency","ZEUR",-10.3220,0.0268,89.6512
"L4ER7P-XHIOQ-VSUANG","THXBOQ-UXHAI-HKJOSZ","2017-11-12 19:17:16","trade","","currency","XREP",1.0000000000,0.0000000000,1.0000000000
```

Which can be cleaned up with:

```awk
awk 'BEGIN {FS = ","} {print $3" "$4" "$6" "$7" "$8" "$9}'
```
