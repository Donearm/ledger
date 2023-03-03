package main

////////////////////////////////////////////////////////////////////////////////
// Copyright (c) 2022, Gianluca Fiore
//
//    This program is free software: you can redistribute it and/or modify
//    it under the terms of the GNU General Public License as published by
//    the Free Software Foundation, either version 3 of the License, or
//    (at your option) any later version.
//
////////////////////////////////////////////////////////////////////////////////

// A quick program to extrapolate all the debts from a csv statement and output 
// their sum

import (
	"encoding/csv"
	"strconv"
	"fmt"
	"os"
	"io"
	"regexp"
)

// Regexp to match the statement filenames of Bank Millennium and Bank Santander 
// Polska
var millenniumCsv = regexp.MustCompile(`^Account_activity_*`)
var santanderCsv = regexp.MustCompile(`^historia_*`)

func csvReader() {
	csvFile, err := os.Open(os.Args[1])
	if err != nil {
		fmt.Println("An error encountered while opening file", err)
		return
	}

	reader := csv.NewReader(csvFile)
	reader.LazyQuotes = true // Bank Millennium csv needs this

	total_debit := 0.00
	debit := 0.00
	for i := 2 ;; i = i + 1 {
		record, err := reader.Read()
		if err == io.EOF {
			break // reached end of file
		} else if err != nil {
			fmt.Println("An error occurred while reading the file", err)
			return
		}

		if millenniumCsv.MatchString(os.Args[1]) {
			debit, _ := strconv.ParseFloat(record[7], 8)
			total_debit += debit
		} else if santanderCsv.MatchString(os.Args[1]) {
			debit, _ := strconv.ParseFloat(record[8], 8)
			total_debit += debit
		} else {
			debit, _ := strconv.ParseFloat(record[7], 8)
			total_debit += debit
		}

		//debit, _ := strconv.ParseFloat(record[7], 8)
		//total_debit += debit

		fmt.Printf("Row %d : %v %f \n", i, record, debit)
	}
	fmt.Println("Total debit is ", total_debit)

	err = csvFile.Close()
	if err != nil {
		fmt.Println("An error encountered while closing file", err)
		return
	}

}

func main() {
	csvReader()
}
