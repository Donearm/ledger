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
	"fmt"
	"io"
	"os"
	"path/filepath"
	"regexp"
	"strconv"
	"strings"
)

// Regexp to match the statement filenames of Bank Millennium and Bank Santander 
// Polska
var millenniumCsv = regexp.MustCompile(`^(Downloads/)?Account_activity_*`)
var santanderCsv = regexp.MustCompile(`^(Downloads/)?historia_*`)
var santanderSelectCsv = regexp.MustCompile(`^(Downloads/)?history_*`)
var wiseCsv = regexp.MustCompile(`^(Downloads/)?statement_*`)

func csvReader(path string) {
	fmt.Println("Reading:", path)

	csvFile, err := os.Open(path)
	if err != nil {
		fmt.Println("Error opening file:", err)
		return
	}
	defer func() {
		if err := csvFile.Close(); err != nil {
			fmt.Println("Error closing file:", err)
		}
	}()

	reader := csv.NewReader(csvFile)
	reader.LazyQuotes = true
	reader.FieldsPerRecord = -1 // allow variable number of fields

	var totalDebit float64
	var parsedValue float64

	// choose column index based on filename (use base name for matching)
	base := filepath.Base(path)
	colIdx := 7 // default
	switch {
	case millenniumCsv.MatchString(base):
		colIdx = 7
	case santanderCsv.MatchString(base):
		colIdx = 5
	case santanderSelectCsv.MatchString(base):
		colIdx = 5
	case wiseCsv.MatchString(base):
		colIdx = 2
	default:
		colIdx = 7
	}

	row := 0
	for {
		record, err := reader.Read()
		if err == io.EOF {
			break
		}
		if err != nil {
			fmt.Println("Error reading CSV:", err)
			return
		}
		row++

		// Skip first row (header) to match previous behavior (the original started i := 2)
		if row == 1 {
			continue
		}

		if colIdx >= len(record) {
			fmt.Printf("Row %d: not enough columns (need index %d, got %d) -> skipping\n", row, colIdx, len(record))
			continue
		}

		field := strings.TrimSpace(record[colIdx])
		if field == "" {
			// empty cell -> skip
			continue
		}

		// Detect if the original field was negative (leading '-') before normalization
		originalWasNegative := strings.HasPrefix(field, "-")
		// Normalize number: change comma to dot
		field = strings.ReplaceAll(field, ",", ".")
		// Remove thousands separators (if any) - example: "1 234.56" or "1'234.56"
		field = strings.ReplaceAll(field, " ", "")
		field = strings.ReplaceAll(field, "'", "")

		// if the field had a leading '-', remove it so we can parse the 
		// magnitude
		if strings.HasPrefix(field, "-") {
			field = strings.TrimPrefix(field, "-")
		}

		// Parse float
		parsed, perr := strconv.ParseFloat(field, 64)
		if perr != nil {
			fmt.Printf("Row %d: cannot parse value %q: %v -> skipping\n", row, record[colIdx], perr)
			continue
		}
		parsedValue = parsed

		// Only add values that were negative in the original CSV (true debts)
		if originalWasNegative {
			totalDebit += parsedValue
		}

		fmt.Printf("Row %d: parsed=%f (raw %q) added=%t total=%f\n", row, parsedValue, record[colIdx], originalWasNegative, totalDebit)
	}

	fmt.Printf("Total debit is %f\n", totalDebit)
}

func main() {
	if len(os.Args) < 2 {
		fmt.Printf("Usage: %s <csv-file-path>\n", filepath.Base(os.Args[0]))
		os.Exit(2)
	}
	csvReader(os.Args[1])
}
