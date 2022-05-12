# Importers for Beancount ledger

There are mainly one large importer, that is my principal bank account on which 
I rarely have investments or open positions. That account holds 3 currencies 
(PLN, EUR and USD).

Secondary importers are for PayPal (I rarely use it), Wise (very useful for 
travelling and holding multiple currencies), and Revolut (occasional purchases 
and crypto/currency/stock investments).

`config.py` is used to call one by one the importers. Each importer file has a 
specific function to import its own currency. They had to be separated 
otherwise it would have been way hard with some csv exports to understand in 
what currency the transactions were. It is far from optimal but for the number 
of entries that need to be processed, it is fast enough.

Roughly every two months all the importers are ran.
