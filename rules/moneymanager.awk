# Extract the necessary fields from a MoneyManager exported csv file
BEGIN {FS = ","}
{print $1,$2,$3,$4,$5,$7,$9,$10}
