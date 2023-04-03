#!/bin/bash

# Monthly update of prices for Beancount, using pricehist
# (https://gitlab.com/chrisberkhout/pricehist)

CURRENT_YEAR=$(date +%Y)
PRICEHIST=/home/gianluca/.local/bin/pricehist
PRICES_DIR=/home/gianluca/.ledger/prices/

# Save current month in decimal format (no leading 0)
CURRENT_MONTH=$((10#$(date +%m)))

# declare an associative array of currencies' pairs and output filenames
declare -A PRICEPAIRS
PRICEPAIRS['EUR/CHF']='eur_to_chf.prices'
PRICEPAIRS['EUR/GBP']='eur_to_gbp.prices'
PRICEPAIRS['EUR/MUR']='eur_to_mur.prices'
PRICEPAIRS['EUR/MXN']='eur_to_mxn.prices'
PRICEPAIRS['EUR/PLN']='eur_to_pln.prices'
PRICEPAIRS['EUR/TRY']='eur_to_try.prices'
PRICEPAIRS['EUR/USD']='eur_to_usd.prices'
PRICEPAIRS['GBP/EUR']='gbp_to_eur.prices'
PRICEPAIRS['GBP/PLN']='gbp_to_pln.prices'
PRICEPAIRS['MUR/EUR']='mur_to_eur.prices'
PRICEPAIRS['MUR/PLN']='mur_to_pln.prices'
PRICEPAIRS['MUR/USD']='mur_to_usd.prices'
PRICEPAIRS['PLN/CHF']='pln_to_chf.prices'
PRICEPAIRS['PLN/EUR']='pln_to_eur.prices'
PRICEPAIRS['PLN/GBP']='pln_to_gbp.prices'
PRICEPAIRS['PLN/MUR']='pln_to_mur.prices'
PRICEPAIRS['PLN/MXN']='pln_to_mxn.prices'
PRICEPAIRS['PLN/USD']='pln_to_usd.prices'
PRICEPAIRS['TRY/EUR']='try_to_eur.prices'
PRICEPAIRS['USD/EUR']='usd_to_eur.prices'
PRICEPAIRS['USD/MUR']='usd_to_mur.prices'
PRICEPAIRS['USD/MXN']='usd_to_mxn.prices'
PRICEPAIRS['USD/PLN']='usd_to_pln.prices'

# if January, save December prices. Otherwise, subtract 1 to get the 
# previous month
if [ $CURRENT_MONTH -eq 1 ]; then
	$UPDATE_MONTH=12
else
	let UPDATE_MONTH=$CURRENT_MONTH-1
fi

for i in "${!PRICEPAIRS[@]}"; do
	echo "Updating $i prices..."
	$PRICEHIST fetch alphavantage $i -s ${CURRENT_YEAR}-0${UPDATE_MONTH}-01 -e ${CURRENT_YEAR}-0${CURRENT_MONTH}-01 -o beancount >> ${PRICES_DIR}${PRICEPAIRS[$i]}
	# We have to sleep for a minute after every call because 
	# alphavantage has a 5 calls/minute API rate limit
	sleep 60
	# meanwhile, we can sort and "uniq" the file to remove duplicate 
	# entries and have all nicely ordered
	sort -u "${PRICES_DIR}${PRICEPAIRS[$i]}" -o "${PRICES_DIR}${PRICEPAIRS[$i]}" 
done

exit 0
