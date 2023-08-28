#!/bin/bash
#
# This script runs through the ledger from 2015 onward, looping over 
# each month and printing the total expenses for it, only from selected 
# accounts, all converted to a predefined currency
#
# Quite in alpha state, use at your own risk

LEDGERDIR="${HOME}/.ledger/"
ALL_ACCOUNTS="${LEDGERDIR}all.beancount"
CURRENCY='PLN'
EXPENSES_ACCOUNTS='Expenses:(Animals|Animals:Food|Apparel|Beauty|Drinks|Food-Delivery|Groceries|Health|Household|Other|Restaurants-and-Food-Out|Subscriptions:Play|Subscriptions:Spotify|Subscriptions:Upc|Transportation:Car-Expenses|Transportation:Car-Fuel|Utilities)'

for y in {2015..2023}; do
	for m in {1..12}; do
		if [[ ${m} -eq 12 ]]; then
			# if we reached the December, the upper date limit should be 
			# January of next year, not any "thirteenth" month
			BQL="SELECT year, month, root(account, 1) as r, convert(sum(position), '${CURRENCY}') FROM date >= ${y}-$(printf "%02d" ${m})-01 AND date < $((${y} + 1))-${m}-01 WHERE account ~ '${EXPENSES_ACCOUNTS}' GROUP BY year, month, r ORDER BY year, month, r;"
			bean-query -f csv -q $ALL_ACCOUNTS "${BQL}";
		else
			BQL="SELECT year, month, root(account, 1) as r, convert(sum(position), '${CURRENCY}') FROM date >= ${y}-$(printf "%02d" ${m})-01 AND date < ${y}-$(printf "%02d" $((${m} + 1)))-01 WHERE account ~ '${EXPENSES_ACCOUNTS}'  GROUP BY year, month, r ORDER BY year, month, r;"
			bean-query -f csv -q $ALL_ACCOUNTS "${BQL}";
		fi
	done
done

exit 0
