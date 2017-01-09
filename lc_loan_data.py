import pandas as pd
import sqlite3 as sql
import argparse
import sys
import datetime as dt
import to_pptx as ppt


class LoanData(object):

    def __init__(self, database_file):
        self.database_file = database_file
        self.data_from_db()
        self.check_status()
        self.add_clean_status()
        self.add_profit_loss_col()

    def data_from_db(self):
        """Connect to database and pull in raw data"""
        db_con = sql.connect(self.database_file)

        # Make sure database contains correct table and columns.
        try:
            pd.read_sql_query('SELECT funded_amnt_inv, total_pymnt, out_prncp, recoveries, grade, '
                                  'loan_status FROM loan LIMIT 1', db_con)

        except pd.io.sql.DatabaseError:
            print('The database is missing table \'loans\', or one or more required columns: '
                  '\'funded_amnt_inv, total_pymnt, out_prncp, recoveries, grade, loan_status\'')
            sys.exit()

        # Read data from the Database, tell user number of records.
        try:
            self.data = pd.read_sql_query('SELECT * FROM loan', db_con)
            print('Read {} records from database "{}"'.format(len(self.data), self.database_file))

        except pd.io.sql.DatabaseError:
            print('Can\'t connect to Database "{}". Make sure name and location are correct.'
                  .format(self.database_file))
            sys.exit()



    def clean_status(self, raw_status):
        """Characterizes loans by adding a clean 'status' value"""
        status = ""
        raw_status = str(raw_status).lower().strip()

        if 'charged' in raw_status:
            status = 'charged_off'
        elif 'default' in raw_status:
            status = 'default'
        elif 'paid' in raw_status:
            status = 'paid'
        elif ('grace' and 'period') in raw_status:
            status = 'grace_per'
        elif 'current' in raw_status:
            status = 'current'
        elif 'issued' in raw_status:
            status = 'current'
        elif ('late' and '16-30') in raw_status:
            status = 'late16_30'
        elif ('late' and '31-120') in raw_status:
            status = 'late31_120'
        else:
            # There shouldn't be any 'uncategorized' loans, but we'll be able to find them if there are any
            # using this label.

            status = 'uncategorized'

        return status

    def add_clean_status(self):
        """Add a 'clean_status' column, tell user if any rows are 'uncategorized'"""
        self.data['clean_status'] = self.data.apply(lambda row: self.clean_status(row["loan_status"]), axis=1)

        print('{} records are Uncategorized'.format(len(self.data[self.data['clean_status'] == 'uncategorized'])))

    def add_profit_loss_col(self):
        """
        Add columns for: profit/loss in dollars, profit/loss in percent to each row.
        Set remaining amount of 'default' loans to 0.
        """
        self.data.ix[self.data.clean_status == 'default', 'out_prncp'] = 0

        # Add profit/loss columns:
        self.data['profit_loss'] = (self.data['funded_amnt_inv'] - self.data['total_pymnt'] -
                                    self.data['recoveries'] - self.data['out_prncp']) * -1
        self.data['profit_loss_pct'] = self.data['profit_loss'] / self.data['funded_amnt_inv']

    def check_status(self):
        """
        Checks if all loans have a 'status', removes rows with no 'loan_status'.
        To ensure that a 'loan_status' value is available for each row,
        we get the totals of rows with/ without the status value.
        """
        print('Out of {} records, {} have a status, and {} do not'.format(len(self.data['loan_status']),
                                                                          self.data['loan_status'].notnull().sum(),
                                                                          self.data['loan_status'].isnull().sum()))

        # Remove rows with no 'loan_status'
        self.data = self.data[self.data.loan_status.notnull()]

    def group_grade_ppt(self, pptx_name):
        """Group by Grade, save to PowerPoint presentation"""

        grouped_data = self.data.groupby(['grade']).sum()[['funded_amnt_inv', 'total_pymnt', 'out_prncp',
                                                           'recoveries', 'profit_loss']]

        ppt.new_pptx(pptx_name, grouped_data)

        print('Exported data to "{}"'.format(pptx_name))

    def group_grade_csv(self, csv_name):
        """Group by Grade, save to .csv"""

        grouped_data = self.data.groupby(['grade']).sum()[['funded_amnt_inv', 'total_pymnt', 'out_prncp',
                                                           'recoveries', 'profit_loss']]
        grouped_data.to_csv(csv_name, index_label='grade', index='grade')
        print('Exported data to "{}"'.format(csv_name))

    def to_csv(self, csv_name):
        """Save all loan data to .csv"""

        self.data.to_csv(csv_name, index_label=False, index=False)
        print('Exported data to "{}"'.format(csv_name))


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('loan_database_name', help='The file name of the database where loan data is stored',
                                                   type=str)
    parser.add_argument('-csv_all', '--all_data_to_csv', help='Output all data to .csv file', action='store_true')
    parser.add_argument('-csv_by_grade', '--group_by_grade_to_csv', help='Output all data to .csv file, '
                                                                         'grouped by loan grade', action='store_true')
    parser.add_argument('-ppt_grade', '--group_by_grade_to_ppt', help='Output all data to PowerPoint Presentation, '
                                                                         'grouped by loan grade', action='store_true')
    args = parser.parse_args()

    date_time_now = dt.datetime.now()

    if args.all_data_to_csv:
        LoanData(args.loan_database_name).to_csv('loans_all_{}.csv'.format(date_time_now))

    if args.group_by_grade_to_csv:
        LoanData(args.loan_database_name).group_grade_csv('loans_by_grade_{}.csv'.format(date_time_now))

    if args.group_by_grade_to_ppt:
        LoanData(args.loan_database_name).group_grade_ppt('Loan_Performance_{}.ppt'.format(date_time_now))

