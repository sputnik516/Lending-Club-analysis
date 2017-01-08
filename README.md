# Lending Club Loan analysis
Raw data can be found here: https://www.kaggle.com/wendykan/lending-club-loan-data in SQLite format, or can be sourced directly from Lending Club: https://www.lendingclub.com/info/download-data.action

The original database has nearly 1 million lines. LC_data_analysis.py reads this data, cleans it, and exports .csv files that are small enough for a user to be able to easily work with using excel.

* to_csv - Export all data to .csv
* group_grade_csv - Export .csv grouped by loan grade

