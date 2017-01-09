# Lending Club Loan analysis
Raw data can be found here: https://www.kaggle.com/wendykan/lending-club-loan-data in SQLite format, or can be sourced directly from Lending Club: https://www.lendingclub.com/info/download-data.action

The original database has nearly 1 million lines. lc_loan_data.py reads this data, cleans it, and exports .csv files that are small enough for a user to be able to easily work with using excel.

This program can be run from the command line. The user inputs the database name, and the type of output required:

* -csv_all - Export all data to .csv
* -csv_by_grade - Export .csv grouped by loan grade
* -h - Help and available commands
* -ppt_grade - create a PowerPoint including a loan summary, and table of loans by grade


Video Demo: https://www.youtube.com/watch?v=F8BXn7gM1DA
