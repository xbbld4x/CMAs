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

# %% [markdown]
# # Run All Calcs

# %%
# Check if new data needs to be pulled
date_check = pd.read_excel('P:\\Advisory\\Research\\Automation\\CMAs\\Data\\bloomberg_data_us.xlsx', index_col=0)

if (cma.val_dict['as_of_date'] in date_check.index):
    import backfill_calc
    import std_dev
    import fixed_income_calcs
    import equity_calcs
    import alts
    print('No new data needed')
else:
    import data_pull
    import backfill_calc
    import std_dev
    import fixed_income_calcs
    import equity_calcs
    import alts
    print('New data pulled')

# %% [markdown]
# # Final Data

# %% [markdown]
# ## US

# %%
df_final_us = pd.concat([equity_calcs.equity_returns_us, fixed_income_calcs.fixed_returns_us*100, alts.alts_returns_us])
df_final_us = pd.DataFrame(df_final_us)
df_final_us = df_final_us.rename(columns={0: "Expected Return"})

# Combine Expected Returns with Standard Deviation
df_final_us = df_final_us.merge(std_dev.annual_adj_std_dev_us*100, left_index=True, right_index=True)
df_final_us = df_final_us.rename(columns={0: "Standard Deviation"})

# Convert to ints and round
df_final_us['Expected Return'] = pd.to_numeric(df_final_us['Expected Return']).round(1)
df_final_us['Standard Deviation'] = pd.to_numeric(df_final_us['Standard Deviation']).round(1)

# Reorder
equity_us_name = list(filter(None, list({k:v for (k,v) in cma.val_dict.items() if 'equity_us_name' in k}.values())))
fixed_us_name = list(filter(None, list({k:v for (k,v) in cma.val_dict.items() if 'fixed_us_name' in k}.values())))
alts_us_name = list(filter(None, list({k:v for (k,v) in cma.val_dict.items() if 'alts_us_name' in k}.values())))

order_name_us = equity_us_name + fixed_us_name + alts_us_name
df_final_us = df_final_us.reindex(index=order_name_us)

df_final_us

# %% [markdown]
# ## NonUS

# %%
df_final_nonus = pd.concat([equity_calcs.equity_returns_nonus, fixed_income_calcs.fixed_returns_nonus*100, alts.alts_returns_nonus])
df_final_nonus = pd.DataFrame(df_final_nonus)

df_final_nonus = df_final_nonus.rename(columns={0: "Expected Return"})
    
# Combine Expected Returns with Standard Deviation
df_final_nonus = df_final_nonus.merge(std_dev.annual_adj_std_dev_nonus*100, left_index=True, right_index=True)
df_final_nonus = df_final_nonus.rename(columns={0: "Standard Deviation"})

# Add Income Return

df_final_nonus = df_final_nonus.join(pd.DataFrame(fixed_income_calcs.income_return_nonus*100)).rename(columns={0: "Income Return"})

df_final_nonus.loc[['U.S. Equity', 'U.S. Small Cap Equity'], 'Income Return'] = cma.val_dict['us_equity_income']
df_final_nonus.loc[['Europe Ex-UK Equity', 'Europe Small Cap Equity'], 'Income Return'] = cma.val_dict['europe_ex_uk_equity_income']
df_final_nonus.loc['UK Equity', 'Income Return'] = cma.val_dict['uk_equity_income']
df_final_nonus.loc[['Japan Equity', 'Japan Small Cap Equity'], 'Income Return'] = cma.val_dict['japan_equity_income']
df_final_nonus.loc['Developed Market Pacific Ex-Japan Equity', 'Income Return'] = cma.val_dict['apac_ex_japan_equity_income']
df_final_nonus.loc['Global Emerging Markets Equity', 'Income Return'] = cma.val_dict['em_equity_income']

df_final_nonus.loc[list(filter(None, list({k:v for (k,v) in cma.val_dict.items() if 'alts_nonus_name' in k}.values()))),'Income Return'] = 0


# Convert to ints and round
df_final_nonus['Expected Return'] = pd.to_numeric(df_final_nonus['Expected Return']).round(1)
df_final_nonus['Standard Deviation'] = pd.to_numeric(df_final_nonus['Standard Deviation']).round(1)
df_final_nonus['Income Return'] = pd.to_numeric(df_final_nonus['Income Return']).round(1)

# Reorder
equity_nonus_name = list(filter(None, list({k:v for (k,v) in cma.val_dict.items() if 'equity_nonus_name' in k}.values())))
fixed_nonus_name = list(filter(None, list({k:v for (k,v) in cma.val_dict.items() if 'fixed_nonus_name' in k}.values())))
alts_nonus_name = list(filter(None, list({k:v for (k,v) in cma.val_dict.items() if 'alts_nonus_name' in k}.values())))

order_name_nonus = equity_nonus_name + fixed_nonus_name + alts_nonus_name
df_final_nonus = df_final_nonus.reindex(index=order_name_nonus)

df_final_nonus


# %%
std_dev.corr_matrix_final_nonus

# %%
