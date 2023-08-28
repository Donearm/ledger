#!/bin/bash
#
# A rough series of premade reports, ready to run. Comment out those 
# that are not desired

LEDGERDIR="${HOME}/.ledger/"
ALL_ACCOUNTS="${LEDGERDIR}all.beancount"

# Returns a table with the total of expenses in each of the given 
# accounts between two dates
bean-query $ALL_ACCOUNTS 'SELECT year, month, account, sum(position) FROM date > 2023-06-30 AND date < 2023-08-01 WHERE account ~ "Expenses:(Animals|Animals:Food|Apparel|Beauty|Drinks|Food-Delivery|Groceries|Health|Household|Other|Restaurants-and-Food-Out|Subscriptions:Play|Subscriptions:Spotify|Subscriptions:Upc|Transportation:Car-Expenses|Transportation:Car-Fuel|Utilities)" GROUP BY year, month, account ORDER BY year, month, account;'

# Returns a single entry table with the grand total, by currency, of all 
# the entries in the given accounts, between two dates
bean-query $ALL_ACCOUNTS 'SELECT year, month, root(account, 1) as r, sum(position) FROM date >= 2023-07-01 AND date < 2023-08-01 WHERE account ~ "Expenses:(Animals|Animals:Food|Apparel|Beauty|Drinks|Food-Delivery|Groceries|Health|Household|Other|Restaurants-and-Food-Out|Subscriptions:Play|Subscriptions:Spotify|Subscriptions:Upc|Transportation:Car-Expenses|Transportation:Car-Fuel|Utilities)" GROUP BY year, month, r ORDER BY year, month, r;'

# Returns a single entry table with the grand total, of all the entries 
# in the given accounts, between two dates, converted to a single 
# currency
bean-query $ALL_ACCOUNTS 'SELECT year, month, root(account, 1) as r, convert(sum(position), "PLN") FROM date >= 2023-07-01 AND date < 2023-08-01 WHERE account ~ "Expenses:(Animals|Animals:Food|Apparel|Beauty|Drinks|Food-Delivery|Groceries|Health|Household|Other|Restaurants-and-Food-Out|Subscriptions:Play|Subscriptions:Spotify|Subscriptions:Upc|Transportation:Car-Expenses|Transportation:Car-Fuel|Utilities)" GROUP BY year, month, r ORDER BY year, month, r;'

exit 0
