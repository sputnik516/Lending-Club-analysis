import pandas as pd
import numpy as np
import sqlite3 as sql


# Connect to database and pull in raw data
def data_from_db(fname):
    db_con = sql.connect(fname)
    data = pd.read_sql_query('SELECT funded_amnt_inv, total_pymnt, out_prncp, recoveries, grade, loan_status FROM loan',
                             db_con)

    return data


# Characterizes loans by adding a clean 'status' value
def clean_status(raw_status):

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
def add_clean_status(data):
    data['clean_status'] = data.apply(lambda row: clean_status(row["loan_status"]), axis=1)

    print('{} records are Uncategorized'.format(len(data[data['clean_status'] == 'uncategorized'])))

    return data

def add_p_l(data):
    # Set remaining amount of 'default' loans to 0
    data.ix[data.clean_status == 'default', 'out_prncp'] = 0


    # Add profit/loss columns:
    data['profit_loss'] = data['total_pymnt'] + data['recoveries'] - data['funded_amnt_inv'] - data['out_prncp']
    data['profit_loss_pct'] = data['profit_loss'] / data['funded_amnt_inv']

    return data


# Checks if all loans have a 'status', removes rows with no 'loan_status'
def check_status(data):
    # To ensure that a 'loan_status' value is available for each row,
    # we get the totals of rows with/ without the status value:
    print('Out of {} records, {} have a status, and {} do not'.format(len(data['loan_status']),
                                                                      data['loan_status'].notnull().sum(),
                                                                      data['loan_status'].isnull().sum()))

    # Remove rows with no 'loan_status'
    data = data[data.loan_status.notnull()]

    return data

def to_csv(data, csv_name):

    data.to_csv(csv_name, index_label=False, index=False)



if __name__ == '__main__':

    # Database file:
    fname = 'database.sqlite'

    data = data_from_db(fname)
    data = check_status(data)
    data = add_clean_status(data)
    data = add_p_l(data)
    to_csv(data, 'LC_loans_by_grade.csv')

    print('Done, data exported to .csv')
