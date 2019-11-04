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

from datetime import datetime
from dateutil.relativedelta import relativedelta
from scipy import stats
# -

# 20 years of data dates
last_date = datetime.strptime(cma.val_dict['as_of_date'], '%m-%d-%Y')
first_date = last_date - relativedelta(years=20) + relativedelta(months=1)


# # Functions

def returns_dataframe(file_suffix):
    """ Combine all return streams and combine into one dataframe for beta backfill calculations """
    
    file = r"P:\\Advisory\\Research\\Automation\\CMAs\\Data\\bloomberg_data_" + file_suffix + ".xlsx"
    
    df_equity = pd.read_excel(file, sheet_name='equity_returns', index_col=0)
    df_fixed = pd.read_excel(file, sheet_name='fixed_returns', index_col=0)
    df_alts = pd.read_excel(file, sheet_name='alts_returns', index_col=0)

    # Combine all index values into single dataframe
    df_returns = df_equity.join(df_fixed, how="outer").join(df_alts, how="outer")
    
    # Reorder
    order_name = list(filter(None, list({k:v for (k,v) in cma.val_dict.items() if '_' + file_suffix + '_name' in k}.values())))
    df_returns = df_returns.reindex(columns=order_name)

    # Filter dataframe to only include last 20 years
    df_returns = df_returns.loc[first_date:last_date, :]
    
    return df_returns


def backfill_determination(df_returns, file_suffix):
    """ Determine what index to use for beta calculations """
    
    asset_name = list(filter(None, list({k:v for (k,v) in cma.val_dict.items() if '_' + file_suffix + '_name' in k}.values())))
    asset_beta = list(filter(None, list({k:v for (k,v) in cma.val_dict.items() if '_' + file_suffix + '_beta' in k}.values())))
    df_backfill = pd.DataFrame(list(zip(asset_name, asset_beta)), columns =['Asset Class', 'Beta Relative To']).set_index('Asset Class') 
    
    # Strip out values that don't need backfilled
    filter_vals = ['Building Blocks', 'N/A']
    df_backfill = df_backfill[~df_backfill['Beta Relative To'].str.contains('|'.join(filter_vals))]
    
    return df_backfill


def backfill_calc(df_returns, df_backfill):
    """ Fill in missing data with beta calculated proxy value """
    
    # Determine columns with NaN
    list_nan = df_returns.columns[df_returns.isna().any()].tolist()
    
    # Backfill indexes with beta adjusted returns if history is not available
    for i in range(len(list_nan)):
        list_nan_sub = list_nan[i]
        backfill_sub = df_backfill.loc[list_nan[i], 'Beta Relative To']
        df_bfill = df_returns[[list_nan_sub, backfill_sub]].dropna()
        
        slope, intercept, r_value, p_value, std_err = stats.linregress(df_bfill[backfill_sub].values, df_bfill[list_nan_sub].values)

        df_returns[list_nan_sub].fillna(df_returns[backfill_sub] * slope + intercept, inplace=True)


# # USD

# +
df_returns_us = returns_dataframe('us')
df_backfill_us = backfill_determination(df_returns_us, 'us')
backfill_calc(df_returns_us, df_backfill_us)

df_returns_us.to_csv(
    r"P:\\Advisory\\Research\\Automation\\CMAs\\Data\\combined_returns_us.csv")
# -

# # Non-USD

# +
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
df_index_nonus = df_equity_nonus.join(df_fixed_nonus, how="outer").join(df_alts_nonus, how="outer")

# +
# Adjust indices for currency
df_index_local= df_index_nonus.mul(df_currency[cma.val_dict['currency']], axis=0)

# Add back in alts and us equity with non local results
df_equity_nonus_usequity = df_equity_nonus['U.S. Equity']
df_alts_nonus_nolocal = df_alts_nonus.merge(df_equity_nonus_usequity, left_index=True, right_index=True)
df_alts_nonus_nolocal = df_alts_nonus_nolocal.add_prefix('USD_')

df_index_local = df_index_local.join(df_alts_nonus_nolocal, how="outer")

# Calculate monthly returns in local currency
df_returns_nonus = df_index_local.pct_change()

# Filter dataframe to only include last 20 years
df_returns_nonus = df_returns_nonus.loc[first_date:last_date, :]
# -

df_backfill_nonus = backfill_determination(df_returns_nonus, 'nonus')
backfill_calc(df_returns_nonus, df_backfill_nonus)
df_returns_nonus

df_returns_nonus.to_csv(
    r"P:\\Advisory\\Research\\Automation\\CMAs\\Data\\combined_returns_nonus.csv")


