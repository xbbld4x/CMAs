# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.4'
#       jupytext_version: 1.2.4
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# +
import cma_gui as cma

import numpy as np
import pandas as pd

from datetime import date
from datetime import datetime
from dateutil.relativedelta import relativedelta
from scipy import stats
# -

# Include 20 years of data dats
last_date = datetime.strptime(cma.val_dict['as_of_date'], '%m-%d-%Y')
first_date = last_date - relativedelta(years=20)

# # USD

# +
# Import index values
df_equity = pd.read_excel(
    "P:\\Advisory\\Research\\Automation\\CMAs\\Data\\bloomberg_data_usd.xlsx", sheet_name='equity_returns', index_col=0)
df_fixed = pd.read_excel(
    "P:\\Advisory\\Research\\Automation\\CMAs\\Data\\bloomberg_data_usd.xlsx", sheet_name='fixed_returns', index_col=0)
df_alts = pd.read_excel(
    "P:\\Advisory\\Research\\Automation\\CMAs\\Data\\bloomberg_data_usd.xlsx", sheet_name='alts_returns', index_col=0)

# Combine all index values into single dataframe
df_returns = df_equity.join(df_fixed, how="outer")
df_returns = df_returns.join(df_alts, how="outer")

# Filter dataframe to only include 20 years of data
mask_us = (df_returns.index > first_date) & (df_returns.index <= last_date)
df_returns = df_returns.loc[mask_us]

# +
# Determine columns with NaN
list_nan_us = df_returns.columns[df_returns.isna().any()].tolist()

equity_us_name = list(filter(None, list({k:v for (k,v) in cma.val_dict.items() if 'equity_us_name' in k}.values())))
equity_us_beta = list(filter(None, list({k:v for (k,v) in cma.val_dict.items() if 'equity_us_beta' in k}.values())))
df_backfill_us_equity = pd.DataFrame(list(zip(equity_us_name, equity_us_beta)), columns =['Asset Class', 'Beta Relative To'])

fixed_us_name = list(filter(None, list({k:v for (k,v) in cma.val_dict.items() if 'fixed_us_name' in k}.values())))
fixed_us_beta = list(filter(None, list({k:v for (k,v) in cma.val_dict.items() if 'fixed_us_beta' in k}.values())))
df_backfill_us_fixed = pd.DataFrame(list(zip(fixed_us_name, fixed_us_beta)), columns =['Asset Class', 'Beta Relative To'])

alts_us_name = list(filter(None, list({k:v for (k,v) in cma.val_dict.items() if 'alts_us_name' in k}.values())))
alts_us_beta = list(filter(None, list({k:v for (k,v) in cma.val_dict.items() if 'alts_us_beta' in k}.values())))
df_backfill_us_alts = pd.DataFrame(list(zip(alts_us_name, alts_us_beta)), columns =['Asset Class', 'Beta Relative To'])

# Combine backfill data into one dataframe
filter_vals = ['Building Blocks', 'N/A']

df_backfill_us = df_backfill_us_equity.copy(deep=True)
df_backfill_us = df_backfill_us.append(df_backfill_us_fixed).append(df_backfill_us_alts)
df_backfill_us = df_backfill_us[~df_backfill_us['Beta Relative To'].str.contains('|'.join(filter_vals))]
df_backfill_us = df_backfill_us.set_index('Asset Class')
# -

# Backfill indexes with beta adjusted returns if history is not available
for i in range(len(list_nan_us)):
    list_nan_us_sub = list_nan_us[i]
    backfill_sub_us = df_backfill_us.loc[list_nan_us[i], 'Beta Relative To']
    
    df_bfill_us = df_returns[[list_nan_us_sub, backfill_sub_us]].dropna()
    
    slope, intercept, r_value, p_value, std_err = stats.linregress(df_bfill_us[backfill_sub_us].values, 
                                                                   df_bfill_us[list_nan_us_sub].values)

    df_returns[list_nan_us_sub].fillna(
        df_returns[backfill_sub_us] * slope + intercept, inplace=True)

df_returns.to_csv(
    r"P:\\Advisory\\Research\\Automation\\CMAs\\Data\\combined_returns_us.csv")

# # Non USD

# Import index values
df_equity_nonus = pd.read_excel(
    "P:\\Advisory\\Research\\Automation\\CMAs\\Data\\bloomberg_data_nonus.xlsx", sheet_name='equity_returns', index_col=0)
df_fixed_nonus = pd.read_excel(
    "P:\\Advisory\\Research\\Automation\\CMAs\\Data\\bloomberg_data_nonus.xlsx", sheet_name='fixed_returns', index_col=0)
df_alts_nonus = pd.read_excel(
    "P:\\Advisory\\Research\\Automation\\CMAs\\Data\\bloomberg_data_nonus.xlsx", sheet_name='alts_returns', index_col=0)
df_currency = pd.read_excel(
    "P:\\Advisory\\Research\\Automation\\CMAs\\Data\\bloomberg_data_nonus.xlsx", sheet_name='currencies', index_col=0)

# Combine all index values into single dataframe
df_index_nonus = df_equity_nonus.join(df_fixed_nonus, how="outer")
df_index_nonus = df_index_nonus.join(df_alts_nonus, how="outer")

# +
# Adjust indices for currency
df_index_local= df_index_nonus.mul(df_currency[cma.val_dict['currency']], axis=0)

# Add back in alts and us equity with non local results
df_equity_nonus_usequity = df_equity_nonus['U.S. Equity']
df_alts_nonus_nolocal = df_alts_nonus.merge(df_equity_nonus_usequity, left_index=True, right_index=True)
df_alts_nonus_nolocal = df_alts_nonus_nolocal.add_prefix('USD_')

df_index_local = df_index_local.join(df_alts_nonus_nolocal, how="outer")

# Calculate monthly returns in local currency
df_returns_local = df_index_local.pct_change()

# Filter dataframe to only include 20 years of data
last_date = datetime.strptime(cma.val_dict['as_of_date'], '%m-%d-%Y')
first_date = last_date - relativedelta(years=20)

mask = (df_returns_local.index > first_date) & (df_returns_local.index <= last_date)
df_returns_local = df_returns_local.loc[mask]

# +
# Determine columns with NaN
list_nan_nonus = df_returns_local.columns[df_returns_local.isna().any()].tolist()

equity_nonus_name = list(filter(None, list({k:v for (k,v) in cma.val_dict.items() if 'equity_nonus_name' in k}.values())))
equity_nonus_beta = list(filter(None, list({k:v for (k,v) in cma.val_dict.items() if 'equity_nonus_beta' in k}.values())))
df_backfill_equity_nonus = pd.DataFrame(list(zip(equity_nonus_name, equity_nonus_beta)), columns =['Asset Class', 'Beta Relative To'])

fixed_nonus_name = list(filter(None, list({k:v for (k,v) in cma.val_dict.items() if 'fixed_nonus_name' in k}.values())))
fixed_nonus_beta = list(filter(None, list({k:v for (k,v) in cma.val_dict.items() if 'fixed_nonus_beta' in k}.values())))
df_backfill_fixed_nonus = pd.DataFrame(list(zip(fixed_nonus_name, fixed_nonus_beta)), columns =['Asset Class', 'Beta Relative To'])

alts_nonus_name = list(filter(None, list({k:v for (k,v) in cma.val_dict.items() if 'alts_nonus_name' in k}.values())))
alts_nonus_beta = list(filter(None, list({k:v for (k,v) in cma.val_dict.items() if 'alts_nonus_beta' in k}.values())))
df_backfill_alts_nonus = pd.DataFrame(list(zip(alts_nonus_name, alts_nonus_beta)), columns =['Asset Class', 'Beta Relative To'])

# Combine backfill data into one dataframe
filter_vals = ['Building Blocks', 'N/A']

df_backfill_nonus = df_backfill_equity_nonus.copy(deep=True)
df_backfill_nonus = df_backfill_nonus.append(df_backfill_fixed_nonus).append(df_backfill_alts_nonus)
df_backfill_nonus = df_backfill_nonus[~df_backfill_nonus['Beta Relative To'].str.contains('|'.join(filter_vals))]
df_backfill_nonus = df_backfill_nonus.set_index('Asset Class')

# +
# # Loop through every column with NaN, determine backfill index, calculate beta,
# # Fill NaN values of column with beta-adjusted returns

for i in range(len(list_nan_nonus)):
    list_nan_nonus_sub = list_nan_nonus[i]
    backfill_sub_nonus = df_backfill_nonus.loc[list_nan_nonus[i], 'Beta Relative To']
    
    df_bfill_nonus = df_returns_local[[list_nan_nonus_sub, backfill_sub_nonus]].dropna()
    
    slope, intercept, r_value, p_value, std_err = stats.linregress(df_bfill_nonus[backfill_sub_nonus].values, 
                                                                    df_bfill_nonus[list_nan_nonus_sub].values)

    df_returns_local[list_nan_nonus_sub].fillna(
        df_returns_local[backfill_sub_nonus] * slope + intercept, inplace=True)

# Drop beta returns
df_returns_local = df_returns_local.drop(['Emerging Debt Agg USD'], axis=1)

# -

df_returns_local.to_csv(
    r"P:\\Advisory\\Research\\Automation\\CMAs\\Data\\combined_returns_nonus.csv")


