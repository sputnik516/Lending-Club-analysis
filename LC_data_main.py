import pandas as pd
import numpy as np
import sqlite3 as sql


class LoanData(object):

    def __init__(self, fname):
        self.fname = fname
        self.data = pd.DataFrame()

    # Connect to database and pull in raw data
    def data_from_db(self):
        db_con = sql.connect(self.fname)
        self.data = pd.read_sql_query('SELECT funded_amnt_inv, total_pymnt, out_prncp, recoveries, grade, loan_status FROM loan',
                                 db_con)
        print('Read {} records frm DB'.format(len(self.data)))

    # Characterizes loans by adding a clean 'status' value
    def clean_status(self, raw_status):

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
            # using this label:
            status = 'uncategorized'

        return status


    # Add a 'clean_status' column
    def add_clean_status(self):
        self.data['clean_status'] = self.data.apply(lambda row: self.clean_status(row["loan_status"]), axis=1)

        print('{} records are Uncategorized'.format(len(self.data[self.data['clean_status'] == 'uncategorized'])))

    def add_p_l(self):
        # Set remaining amount of 'default' loans to 0
        self.data.ix[self.data.clean_status == 'default', 'out_prncp'] = 0


        # Add profit/loss columns:
        self.data['profit_loss'] = (self.data['funded_amnt_inv'] - self.data['total_pymnt'] -
                                    self.data['recoveries'] - self.data['out_prncp']) * -1
        self.data['profit_loss_pct'] = self.data['profit_loss'] / self.data['funded_amnt_inv']

    # Checks if all loans have a 'status', removes rows with no 'loan_status'
    def check_status(self):
        # To ensure that a 'loan_status' value is available for each row,
        # we get the totals of rows with/ without the status value:
        print('Out of {} records, {} have a status, and {} do not'.format(len(self.data['loan_status']),
                                                                          self.data['loan_status'].notnull().sum(),
                                                                          self.data['loan_status'].isnull().sum()))

        # Remove rows with no 'loan_status'
        self.data = self.data[self.data.loan_status.notnull()]

    # Group by Grade, save to .csv
    def group_grade_csv(self, csv_name):

        grouped_data = self.data.groupby(['grade']).sum()[['funded_amnt_inv', 'total_pymnt', 'out_prncp',
                                                           'recoveries', 'profit_loss']]
        grouped_data.to_csv(csv_name, index_label='grade', index='grade')


    # Save all loan data to .csv
    def to_csv(self, csv_name):

        self.data.to_csv(csv_name, index_label=False, index=False)


if __name__ == '__main__':

    # Database file:
    fname = 'database.sqlite'

    data = LoanData(fname)
    data.data_from_db()
    data.check_status()
    data.add_clean_status()
    data.add_p_l()
    data.group_grade_csv('LC_loans_by_grade.csv')
    data.to_csv('LC_loans_all.csv')