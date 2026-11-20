# CSV to MySQL Migration

Python script that cleans a messy customers CSV file and loads it into MySQL. Rows that cannot be fixed are saved in a separate file with the reason, and a summary report is printed.

**All data in this project is fictional sample data.**

## What it does
- Fixes names (extra spaces, wrong capitalization) and lowercases emails.
- Reads dates in three formats and converts them to one standard format.
- Standardizes country names and cleans money values like `$1,250.00`.
- Rejects rows with missing names, invalid emails, bad dates or amounts, and duplicate emails.
- Loads valid rows into MySQL. Running it again updates rows instead of duplicating them.
- Writes `output/rejected_rows.csv` and prints how many rows were read, loaded and rejected.

## Tech
Python 3, pandas, mysql-connector-python, python-dotenv, MySQL.

## How to run
1. Create the database and table: run `schema.sql` in MySQL Workbench.
2. Install dependencies: `pip install -r requirements.txt`
3. Copy `.env.example` to `.env` and fill in your MySQL user and password.
4. Run: `python migrate.py`
5. Check the data: `SELECT * FROM customers;`

## Example output
_Add a screenshot of the terminal report and of the `customers` table here after running the script._

## Assumptions
- Dates written as `dd/mm/yyyy` are read day-first.
- Only the countries listed in `COUNTRY_MAP` are accepted.
- When an email appears twice, the first row is kept.

## Notes
- Next improvements: tests for the cleaning functions, and a config file for the column rules.
