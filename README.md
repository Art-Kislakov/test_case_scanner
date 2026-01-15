# Test Case Scanner

```
A lightweight Python tool for validating structured QA test cases stored in CSV format.

The scanner applies a set of configurable validation rules to detect common issues in test case files, such as missing fields, incorrect step numbering, empty rows, and inconsistent expected results formatting.
```


## Features
```
- CSV-based test case validation
- Rule-based scanning architecture
- Clear, human-readable console output
- Easy to extend with new validation rules
```


## Project Structure
```
test_case_scanner/
├── app/
│    ├── main.py # Entry point
│    ├── scanner.py # Core scanning logic
│    ├── core_steps.py # Step processing helpers
│    ├── config.py # Configuration flags
│    └── rules/ # Validation rules
├── samples/
│    └── test_case_sample.csv # Example test case file
├── requirements.txt
└── README.md

```
## How It Works
```
1. The scanner reads a CSV file containing test cases.
2. Each row is processed and validated against enabled rules.
3. Validation results are printed to the console as a structured report.
## Usage

```bash
python app/main.py

```
## Requirements
```
Python 3.9+

See requirements.txt for dependencies
Notes

This project is intended as a personal learning and portfolio tool focused on QA automation concepts and Python-based validation logic.
```
