# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.2'
#       jupytext_version: 1.2.4
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %%
import cma_gui as cma
import pandas as pd

from datetime import date
from datetime import datetime
from dateutil.relativedelta import relativedelta
from xbbg import blp

# %% [markdown]
# # As of Date

# %%
# Date range for Bloomberg data pulls
end_date = cma.end_date
end_date_str = end_date.strftime('%m-%d-%Y')

start_date = end_date - relativedelta(years=30)
start_date_str = start_date.strftime('%m-%d-%Y')

# %% [markdown]
# # Equity Data

# %% [markdown]
# ## USD

# %%
# Bloomberg code to pull gross of dividend return values
data_return = ['DAY_TO_DAY_TOT_RETURN_GROSS_DVDS']

# %%
equity_name_list = list(filter(None, list({k:v for (k,v) in cma.val_dict.items() if 'equity_us_name' in k}.values())))
equity_list = list(filter(None, list({k:v for (k,v) in cma.val_dict.items() if 'equity_us_code' in k}.values())))
equity_dictionary = dict(zip(equity_list, equity_name_list))

# %%
equity_returns = blp.bdh(tickers=equity_list, flds=data_return, start_date=start_date_str, end_date=end_date_str, Per='M')

# Rename and reorder columns
equity_returns.columns = equity_returns.columns.droplevel(1)
equity_returns.columns = equity_returns.columns.map(equity_dictionary)

# Convert index to datetime
equity_returns.index = pd.to_datetime(equity_returns.index)

# Adjust dataframe for varying month end dates
equity_returns = equity_returns.resample('M', axis=0).mean()

# %% [markdown]
# ## Non-USD

# %%
# Bloomberg code to pull index values
data_return_nonus = ['PX_LAST']

# %%
# Reference for future renaming of columns
equity_list_nonus = list(filter(None, list({k:v for (k,v) in cma.val_dict.items() if 'equity_nonus_code' in k}.values())))
equity_name_list_nonus = list(filter(None, list({k:v for (k,v) in cma.val_dict.items() if 'equity_nonus_name' in k}.values())))
equity_dictionary_nonus = dict(zip(equity_list_nonus, equity_name_list_nonus))

# %%
equity_returns_nonus = blp.bdh(tickers=equity_list_nonus, flds=data_return_nonus, start_date=start_date_str, end_date=end_date_str, Per='M')

# Rename and reorder columns
equity_returns_nonus.columns = equity_returns_nonus.columns.droplevel(1)
equity_returns_nonus.columns = equity_returns_nonus.columns.map(equity_dictionary_nonus)

# Convert index to datetime
equity_returns_nonus.index = pd.to_datetime(equity_returns_nonus.index)

# Adjust dataframe for varying month end dates
equity_returns_nonus = equity_returns_nonus.resample('M', axis=0).mean()
equity_returns_nonus = equity_returns_nonus.reindex(columns=equity_name_list_nonus)

# %% [markdown]
# # Fixed Income Data

# %% [markdown]
# ## USD - Fixed

# %%
# Reference for future renaming of columns
fixed_list = list(filter(None, list({k:v for (k,v) in cma.val_dict.items() if 'fixed_us_code' in k}.values())))
fixed_name_list = list(filter(None, list({k:v for (k,v) in cma.val_dict.items() if 'fixed_us_name' in k}.values())))
fixed_dictionary = dict(zip(fixed_list, fixed_name_list))

# %% [markdown]
# ### USD Fixed Returns

# %%
fixed_returns = blp.bdh(tickers=fixed_list, flds=data_return, start_date=start_date_str, end_date=end_date_str, Per='M')

# Rename and reorder columns
fixed_returns.columns = fixed_returns.columns.droplevel(1)
fixed_returns.columns = fixed_returns.columns.map(fixed_dictionary)

# Convert index to datetime
fixed_returns.index= pd.to_datetime(fixed_returns.index)

# Adjust dataframe for varying month end dates
fixed_returns = fixed_returns.resample('M', axis=0).mean()

# %% [markdown]
# ### USD Fixed Yields

# %%
fixed_yields = blp.bdh(tickers=fixed_list, flds='YIELD_TO_WORST', start_date=start_date_str, end_date=end_date_str, Per='M')

# Rename and reorder columns
fixed_yields.columns = fixed_yields.columns.droplevel(1)
fixed_yields.columns = fixed_yields.columns.map(fixed_dictionary)

# Convert index to datetime
fixed_yields.index = pd.to_datetime(fixed_yields.index)

# Adjust dataframe for varying month end dates
fixed_yields = fixed_yields.resample('M', axis=0).mean()

# %%
# Add bank loan yields
bank_loan_yield = blp.bdh(tickers='SPBDLLY Index', flds='PX_LAST', start_date=start_date_str, end_date=end_date_str, Per='M')

# Rename and reorder columns
bank_loan_yield.columns = bank_loan_yield.columns.droplevel(1)

# Adjust dataframes for varying month end dates
bank_loan_yield = bank_loan_yield.resample('M', axis=0).mean()

# %%
# Combine with other yield results
fixed_yields['U.S. Bank Loans'] = bank_loan_yield

# %% [markdown]
# ### USD Fixed Spreads

# %%
fixed_spreads = blp.bdh(tickers=fixed_list, flds='INDEX_OAS_TSY', start_date=start_date_str, end_date=end_date_str, Per='M')

# Rename and reorder columns
fixed_spreads.columns = fixed_spreads.columns.droplevel(1)
fixed_spreads.columns = fixed_spreads.columns.map(fixed_dictionary)

# Fill for indices with no spread
fixed_spreads['U.S. TIPS'] = 0
fixed_spreads['U.S. Intermediate Municipal'] = 0
fixed_spreads['U.S. Short Municipal'] = 0

# Convert index to datetime
fixed_spreads.index = pd.to_datetime(fixed_spreads.index)

# Adjust dataframe for varying month end dates
fixed_spreads = fixed_spreads.resample('M', axis=0).mean()

# Add bank loan spread estimate
fixed_spreads['U.S. Bank Loans'] = fixed_yields['U.S. Bank Loans'] - fixed_yields['U.S. Treasury Bills']

# %% [markdown]
# ### USD Fixed Duration

# %%
fixed_durations = blp.bdh(tickers=fixed_list, flds='INDEX_OAD_TSY', start_date=start_date_str, end_date=end_date_str, Per='M')
tips_duration = blp.bdh(tickers='BCIT1T Index', flds='MODIFIED_DURATION', start_date=start_date_str, end_date=end_date_str, Per='M')

# Rename and reorder columns
fixed_durations.columns = fixed_durations.columns.droplevel(1)
fixed_durations.columns = fixed_durations.columns.map(fixed_dictionary)

# Add constant for bank loan spreads
fixed_durations['U.S. Bank Loans'] = 0.25
fixed_durations['U.S. TIPS'] = tips_duration

# Convert index to datetime
fixed_durations.index = pd.to_datetime(fixed_durations.index)

# Adjust dataframe for varying month end dates
fixed_durations = fixed_durations.resample('M', axis=0).mean()

# %% [markdown]
# ## Non USD - Fixed

# %%
# Reference for future renaming of columns
fixed_list_nonus = list(filter(None, list({k:v for (k,v) in cma.val_dict.items() if 'fixed_nonus_code' in k}.values())))
fixed_name_list_nonus = list(filter(None, list({k:v for (k,v) in cma.val_dict.items() if 'fixed_nonus_name' in k}.values())))
fixed_dictionary_nonus = dict(zip(fixed_list_nonus, fixed_name_list_nonus))

# %% [markdown]
# ### Non-USD Fixed Returns

# %%
fixed_returns_nonus = blp.bdh(tickers=fixed_list_nonus, flds=data_return_nonus, start_date=start_date_str, end_date=end_date_str, Per='M')

# Rename and reorder columns
fixed_returns_nonus.columns = fixed_returns_nonus.columns.droplevel(1)
fixed_returns_nonus.columns = fixed_returns_nonus.columns.map(fixed_dictionary_nonus)

# Convert index to datetime
fixed_returns_nonus.index= pd.to_datetime(fixed_returns_nonus.index)

# Adjust dataframe for varying month end dates
fixed_returns_nonus = fixed_returns_nonus.resample('M', axis=0).mean()
fixed_returns_nonus = fixed_returns_nonus.reindex(columns=fixed_name_list_nonus)

# %% [markdown]
# ### Non-USD Fixed Yields

# %%
fixed_yields_nonus = blp.bdh(tickers=fixed_list_nonus, flds='YIELD_TO_WORST', start_date=start_date_str, end_date=end_date_str, Per='M')

# Rename and reorder columns
fixed_yields_nonus.columns = fixed_yields_nonus.columns.droplevel(1)
fixed_yields_nonus.columns = fixed_yields_nonus.columns.map(fixed_dictionary_nonus)

# Convert index to datetime
fixed_yields_nonus.index = pd.to_datetime(fixed_yields_nonus.index)

# Adjust dataframe for varying month end dates
fixed_yields_nonus = fixed_yields_nonus.resample('M', axis=0).mean()

# %% [markdown]
# ### Non-USD Fixed Spreads

# %%
fixed_spreads_nonus = blp.bdh(tickers=fixed_list_nonus, flds='INDEX_OAS_TSY', start_date=start_date_str, end_date=end_date_str, Per='M')

# Rename and reorder columns
fixed_spreads_nonus.columns = fixed_spreads_nonus.columns.droplevel(1)
fixed_spreads_nonus.columns = fixed_spreads_nonus.columns.map(fixed_dictionary_nonus)

# Convert index to datetime
fixed_spreads_nonus.index = pd.to_datetime(fixed_spreads_nonus.index)

# Adjust dataframe for varying month end dates
fixed_spreads_nonus = fixed_spreads_nonus.resample('M', axis=0).mean()

# %% [markdown]
# ### Non-USD Fixed Duration

# %%
fixed_durations_nonus = blp.bdh(tickers=fixed_list_nonus, flds='INDEX_OAD_TSY', start_date=start_date_str, end_date=end_date_str, Per='M')

# Rename and reorder columns
fixed_durations_nonus.columns = fixed_durations_nonus.columns.droplevel(1)
fixed_durations_nonus.columns = fixed_durations_nonus.columns.map(fixed_dictionary_nonus)

# Convert index to datetime
fixed_durations_nonus.index = pd.to_datetime(fixed_durations_nonus.index)

# Adjust dataframe for varying month end dates
fixed_durations_nonus = fixed_durations_nonus.resample('M', axis=0).mean()

# %% [markdown]
# # Treasury Data

# %% [markdown]
# ## US Treasury Data

# %%
treasury_list = ['I00087 Index', 'BTB5STAT Index', 'BW10STAT Index', 'BW30STAT Index']
treasury_dictionary = {'I00087 Index': '3 Mo', 'BTB5STAT Index': '5 Yr', 'BW10STAT Index': '10 Yr', 'BW30STAT Index': '30 Yr'}

# %%
# Treasury Yields
fixed_treasury_yld = blp.bdh(tickers=treasury_list, flds='INDEX_YIELD_TO_MATURITY', start_date=start_date_str, end_date=end_date_str, Per='M')

# Rename and reorder columns
fixed_treasury_yld.columns = fixed_treasury_yld.columns.droplevel(1)
fixed_treasury_yld.columns = fixed_treasury_yld.columns.map(treasury_dictionary)

# %%
# Treasury Duration
fixed_treasury_dur = blp.bdh(tickers=treasury_list, flds='INDEX_OAD_TSY', start_date=start_date_str, end_date=end_date_str, Per='M')

# Rename and reorder columns
fixed_treasury_dur.columns = fixed_treasury_dur.columns.droplevel(1)
fixed_treasury_dur.columns = fixed_treasury_dur.columns.map(treasury_dictionary)

# %% [markdown]
# ## Global Treasury Data

# %%
gl_treasury_list = ['LGY3TRUU Index', 'I04790 Index', 'LG7YSTAT Index', 'LGY7TRUU Index','LGY1TRUU Index']
gl_treasury_dictionary = {'LGY3TRUU Index': '1-3 Yr', 'I04790 Index': '3-5 Yr', 'LG7YSTAT Index': '5-7 Yr', 
                          'LGY7TRUU Index': '7-10 Yr','LGY1TRUU Index': '10+ Yr'}  

# %%
# Gl Treasury Yields
gl_fixed_treasury_yld = blp.bdh(tickers=gl_treasury_list, flds='INDEX_YIELD_TO_MATURITY', start_date=start_date_str, end_date=end_date_str, Per='M')

# Rename and reorder columns
gl_fixed_treasury_yld.columns = gl_fixed_treasury_yld.columns.droplevel(1)
gl_fixed_treasury_yld.columns = gl_fixed_treasury_yld.columns.map(gl_treasury_dictionary)

# %%
# Gl Treasury Durations
gl_fixed_treasury_dur = blp.bdh(tickers=gl_treasury_list, flds='INDEX_OAD_TSY', start_date=start_date_str, end_date=end_date_str, Per='M')

# Rename and reorder columns
gl_fixed_treasury_dur.columns = gl_fixed_treasury_dur.columns.droplevel(1)
gl_fixed_treasury_dur.columns = gl_fixed_treasury_dur.columns.map(gl_treasury_dictionary)

# %% [markdown]
# ## Global Agg Data

# %%
gl_agg_list = ['H16607US Index', 'H16608US Index', 'H16609US Index', 'H16610US Index','H16611US Index']
gl_agg_dictionary = {'H16607US Index': '1-3 Yr', 'H16608US Index': '3-5 Yr', 'H16609US Index': '5-7 Yr', 
                          'H16610US Index': '7-10 Yr','H16611US Index': '10+ Yr'}     

# %%
# Gl Treasury Yields
gl_fixed_agg_yld = blp.bdh(tickers=gl_agg_list, flds='INDEX_YIELD_TO_MATURITY', start_date=start_date_str, end_date=end_date_str, Per='M')

# Rename and reorder columns
gl_fixed_agg_yld.columns = gl_fixed_agg_yld.columns.droplevel(1)
gl_fixed_agg_yld.columns = gl_fixed_agg_yld.columns.map(gl_agg_dictionary)

# %%
# Gl Treasury Durations
gl_fixed_agg_dur = blp.bdh(tickers=gl_agg_list, flds='INDEX_OAD_TSY', start_date=start_date_str, end_date=end_date_str, Per='M')

# Rename and reorder columns
gl_fixed_agg_dur.columns = gl_fixed_agg_dur.columns.droplevel(1)
gl_fixed_agg_dur.columns = gl_fixed_agg_dur.columns.map(gl_agg_dictionary)

# %%
# Gl Treasury Spreads
gl_fixed_agg_spread = blp.bdh(tickers=gl_agg_list, flds='INDEX_OAS_TSY', start_date=start_date_str, end_date=end_date_str, Per='M')

# Rename and reorder columns
gl_fixed_agg_spread.columns = gl_fixed_agg_spread.columns.droplevel(1)
gl_fixed_agg_spread.columns = gl_fixed_agg_spread.columns.map(gl_agg_dictionary)

# %% [markdown]
# ## EM Treasury Data

# %%
em_treasury_list = ['I22843US Index', 'I22844US Index', 'I22845US Index', 'I22846US Index', 'I22847US Index']
em_treasury_dictionary = {'I22843US Index': '1-3 Yr', 'I22844US Index': '3-5 Yr', 'I22845US Index': '5-7 Yr', 'I22846US Index': '7-10 Yr','I22847US Index': '10+ Yr'}    

# %%
# Treasury Yields
em_fixed_treasury_yld = blp.bdh(tickers=em_treasury_list, flds='INDEX_YIELD_TO_MATURITY', start_date=start_date_str, end_date=end_date_str, Per='M')

# Rename and reorder columns
em_fixed_treasury_yld.columns = em_fixed_treasury_yld.columns.droplevel(1)
em_fixed_treasury_yld.columns = em_fixed_treasury_yld.columns.map(em_treasury_dictionary)

# %%
# Treasury Duration
em_fixed_treasury_dur = blp.bdh(tickers=em_treasury_list, flds='INDEX_OAD_TSY', start_date=start_date_str, end_date=end_date_str, Per='M')

# Rename and reorder columns
em_fixed_treasury_dur.columns = em_fixed_treasury_dur.columns.droplevel(1)
em_fixed_treasury_dur.columns = em_fixed_treasury_dur.columns.map(em_treasury_dictionary)

# %% [markdown]
# ## AA Corp Data (for Muni Calcs)

# %%
aa_corp_list = ['I08219 Index']
aa_corp_dictionary = {'I08219 Index': 'AA Corp'}

# %%
# AA Corp Spreads
aa_corp_spread = blp.bdh(tickers=aa_corp_list, flds='INDEX_OAS_TSY', start_date=start_date_str, end_date=end_date_str, Per='M')

# Rename and reorder columns
aa_corp_spread.columns = aa_corp_spread.columns.droplevel(1)
aa_corp_spread.columns = aa_corp_spread.columns.map(aa_corp_dictionary)

# %% [markdown]
# # Alts Data

# %% [markdown]
# ## USD - Alts

# %%
# Reference for future renaming of columns
alts_list = list(filter(None, list({k:v for (k,v) in cma.val_dict.items() if 'alts_us_code' in k}.values())))
alts_name_list = list(filter(None, list({k:v for (k,v) in cma.val_dict.items() if 'alts_us_name' in k}.values())))
alts_dictionary = dict(zip(alts_list, alts_name_list))

# %%
alts_returns = blp.bdh(tickers=alts_list, flds=data_return, start_date=start_date_str, end_date=end_date_str, Per='M')

# Rename and reorder columns
alts_returns.columns = alts_returns.columns.droplevel(1)
alts_returns.columns = alts_returns.columns.map(alts_dictionary)

# Convert index to datetime
alts_returns.index = pd.to_datetime(alts_returns.index)

# Adjust dataframe for varying month end dates
alts_returns = alts_returns.resample('M', axis=0).mean()

# %% [markdown]
# ## Non USD - Alts

# %%
# Reference for future renaming of columns
alts_list_nonus = list(filter(None, list({k:v for (k,v) in cma.val_dict.items() if 'alts_nonus_code' in k}.values())))
alts_name_list_nonus = list(filter(None, list({k:v for (k,v) in cma.val_dict.items() if 'alts_nonus_name' in k}.values())))
alts_dictionary_nonus = dict(zip(alts_list_nonus, alts_name_list_nonus))

# %%
alts_returns_nonus = blp.bdh(tickers=alts_list_nonus, flds=data_return_nonus, start_date=start_date_str, end_date=end_date_str, Per='M')

# Rename and reorder columns
alts_returns_nonus.columns = alts_returns_nonus.columns.droplevel(1)
alts_returns_nonus.columns = alts_returns_nonus.columns.map(alts_dictionary_nonus)

# Convert index to datetime
alts_returns_nonus.index = pd.to_datetime(alts_returns_nonus.index)

# Adjust dataframe for varying month end dates
alts_returns_nonus = alts_returns_nonus.resample('M', axis=0).mean()

# %% [markdown]
# # Currency

# %%
currencies = ['AUD', 'CAD', 'CHF','DKK', 'EUR', 'GBP', 'JPY', 'NOK', 'NZD', 'SEK']
cross_currencies = ['USD' + x +' Curncy' for x in currencies]

# Change naming
cross_currencies_dictionary = {}
for key in cross_currencies: 
    for value in currencies: 
        cross_currencies_dictionary[key] = value 
        currencies.remove(value) 
        break 

# %%
historical_cross_currencies = blp.bdh(tickers=cross_currencies, flds='PX_LAST', start_date=start_date_str, end_date=end_date_str, Per='M')

# Rename and reorder columns
historical_cross_currencies.columns = historical_cross_currencies.columns.droplevel(1)
historical_cross_currencies.columns = historical_cross_currencies.columns.map(cross_currencies_dictionary)

# Convert index to datetime
historical_cross_currencies.index = pd.to_datetime(historical_cross_currencies.index)

# Adjust dataframe for varying month end dates
historical_cross_currencies = historical_cross_currencies.resample('M', axis=0).mean()
historical_cross_currencies['USD'] = 1

# %% [markdown]
# # Beta Index Data

# %%
beta_list = 'EMUSTRUU Index'
beta_dictionary = {'EMUSTRUU Index': 'Emerging Debt Agg USD'}

# %%
beta_returns = blp.bdh(tickers=beta_list, flds=data_return_nonus, start_date=start_date_str, end_date=end_date_str, Per='M')

# Rename and reorder columns
beta_returns.columns = beta_returns.columns.droplevel(1)
beta_returns.columns = beta_returns.columns.map(beta_dictionary)

# Convert index to datetime
beta_returns.index = pd.to_datetime(beta_returns.index)

# Adjust dataframe for varying month end dates
beta_returns = beta_returns.resample('M', axis=0).mean()

# %%
# Add beta return needed to fixed non-us data
fixed_returns_nonus = fixed_returns_nonus.join(beta_returns)

# %% [markdown]
# # Save Data to Excel

# %%
with pd.ExcelWriter(r'P:\\Advisory\\Research\\Automation\\CMA_New\\Data\\bloomberg_data_usd.xlsx') as writer:
    equity_returns.to_excel(writer, sheet_name='equity_returns')
    fixed_returns.to_excel(writer, sheet_name='fixed_returns')
    fixed_yields.to_excel(writer, sheet_name='fixed_yields')
    fixed_spreads.to_excel(writer, sheet_name='fixed_spreads')
    fixed_durations.to_excel(writer, sheet_name='fixed_durations')
    alts_returns.to_excel(writer, sheet_name='alts_returns')

# %%
with pd.ExcelWriter(r'P:\\Advisory\\Research\\Automation\\CMA_New\\Data\\bloomberg_data_nonus.xlsx') as writer:
    equity_returns_nonus.to_excel(writer, sheet_name='equity_returns')
    fixed_returns_nonus.to_excel(writer, sheet_name='fixed_returns')
    fixed_yields_nonus.to_excel(writer, sheet_name='fixed_yields')
    fixed_spreads_nonus.to_excel(writer, sheet_name='fixed_spreads')
    fixed_durations_nonus.to_excel(writer, sheet_name='fixed_durations')
    alts_returns_nonus.to_excel(writer, sheet_name='alts_returns')
    historical_cross_currencies.to_excel(writer, sheet_name='currencies')

# %%
with pd.ExcelWriter(r'P:\\Advisory\\Research\\Automation\\CMA_New\\Data\\term_structure_data.xlsx') as writer:
    aa_corp_spread.to_excel(writer, sheet_name='aa_corp_spread')
    fixed_treasury_yld.to_excel(writer, sheet_name='us_treas_yld')
    fixed_treasury_dur.to_excel(writer, sheet_name='us_treas_dur')
    gl_fixed_treasury_yld.to_excel(writer, sheet_name='gl_treas_yld')
    gl_fixed_treasury_dur.to_excel(writer, sheet_name='gl_treas_dur') 
    gl_fixed_agg_yld.to_excel(writer, sheet_name='gl_agg_yld')
    gl_fixed_agg_dur.to_excel(writer, sheet_name='gl_agg_dur')
    gl_fixed_agg_spread.to_excel(writer, sheet_name='gl_agg_spreads')
    em_fixed_treasury_yld.to_excel(writer, sheet_name='em_treas_yld')
    em_fixed_treasury_dur.to_excel(writer, sheet_name='em_treas_dur')

# %%
