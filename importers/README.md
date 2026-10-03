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

## V2 vs V3

Beancount overhauled the importing system from v2 to v3. I moved the v2 
importer as they were into a subdirectory and the one in the main directory are 
for v3

# How to run the importers

## 1. Check file matching
```python
python3 config.py identify /path/to/statements/
```

## 2. Extract to inspect output
```python
python3 config.py extract /path/to/statements/ -o test.beancount
```

## 3. Validate against ledger
```shell
bean-check main.beancount test.beancount 2>&1 | grep -i "error\|warning" || 
echo "No errors!"
```

During normal operations, only step 2 is actually necessary.
