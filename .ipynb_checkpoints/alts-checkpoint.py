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
import equity_calcs
import std_dev

import numpy as np
import pandas as pd

# %% [markdown]
# # US

# %% [markdown]
# ## IR Adjustments

# %%
alts_us_name = list(filter(None, list({k:v for (k,v) in cma.val_dict.items() if 'alts_us_name' in k}.values())))
alts_us_beta =list(filter(None, list({k:v for (k,v) in cma.val_dict.items() if 'alts_us_beta' in k}.values())))
alts_us_ir =list(filter(None, list({k:v for (k,v) in cma.val_dict.items() if 'alts_us_ir' in k}.values())))

df_alts_us = pd.DataFrame(list(zip(alts_us_name, alts_us_beta, alts_us_ir)), columns =['Asset Class', 'Beta Relative To', 'Information Ratio']) 
df_alts_us = df_alts_us.set_index('Asset Class')

# %%
# Retrieve finalized standard deviaions for use in calcs
std_dev_us = pd.DataFrame(std_dev.annual_adj_std_dev_us)
std_dev_us = std_dev_us.rename(columns={0: 'Std Dev'})

df_alts_us = df_alts_us.merge(std_dev_us, left_index=True, right_index=True)

# %%
# Standard Deviations to use in calcs
sd_to_use_us = []
for name in df_alts_us.index:
    if df_alts_us.loc[name,'Beta Relative To'] == 'Building Blocks':
        sd_to_use_us.append(0)
    else:
        value = std_dev_us.loc[df_alts_us.loc[name,'Beta Relative To']][0]
        sd_to_use_us.append(value)

df_alts_us['Std Dev to Use'] = sd_to_use_us

# %%
# Determine beta value to use for calculations
beta_to_use_us = []
for name in df_alts_us.index:
    skip_list = ['Building Blocks']
    if df_alts_us.loc[name,'Beta Relative To'] in skip_list:
        beta_to_use_us.append(0)
    else:
        beta_lookup = equity_calcs.df_beta_reference_us.loc[name, df_alts_us.loc[name,'Beta Relative To']]
        beta_to_use_us.append(beta_lookup)
    
df_alts_us['Beta To Use'] = beta_to_use_us


# %%
# Residual Risk
df_alts_us['Residual Risk'] = (df_alts_us['Std Dev']**2 - df_alts_us['Beta To Use']**2 * df_alts_us['Std Dev to Use']**2)**(1/2)

# %%
# Base return to use
base_return_to_use_us = []
for name in df_alts_us.index:
    skip_list = ['Building Blocks', 'Commodities']
    if df_alts_us.loc[name,'Beta Relative To'] in skip_list:
        base_return_to_use_us.append(0)
    else:
        base_lookup = equity_calcs.equity_returns_us[df_alts_us.loc[name,'Beta Relative To']]
        base_return_to_use_us.append(base_lookup)
        
df_alts_us['Base Return'] = base_return_to_use_us
df_alts_us['Base Return'] = df_alts_us['Base Return']/100
df_alts_us.loc['Energy Infrastructure','Base Return'] = cma.val_dict['us_inflation']/100

# %%
# Calculate returns for alts with IR adjustments
df_alts_us_ir = df_alts_us[df_alts_us['Information Ratio']!='N/A'].copy(deep=True)

# %%
# Calc final expected return for alts with IR adjustments
df_alts_us_ir['Expected Return'] = (
    (equity_calcs.cash/100) + (df_alts_us_ir['Base Return'] - (equity_calcs.cash/100)) * df_alts_us_ir['Beta To Use'] +\
    df_alts_us_ir['Information Ratio'] * df_alts_us_ir['Residual Risk'])

alts_returns_us_ir = df_alts_us_ir['Expected Return']*100

# %% [markdown]
# ## Non-IR Adjustments

# %%
df_alts_us_no_ir = df_alts_us[df_alts_us['Information Ratio']=='N/A'].copy(deep=True)
df_alts_us_no_ir

# %%
df_alts_us_no_ir['Expected Return'] = np.nan
df_alts_us_no_ir.loc['Commodities', 'Expected Return'] = cma.val_dict['us_inflation']

# Fill in beta-relative returns
df_alts_us_no_ir.loc[df_alts_us_no_ir['Beta Relative To'] == 'Global Equity', 'Expected Return'] = ((equity_calcs.gl_equity_return - equity_calcs.cash) * df_alts_us_no_ir['Beta To Use'] + equity_calcs.cash)
df_alts_us_no_ir.loc[df_alts_us_no_ir['Beta Relative To'] == 'U.S. Equity', 'Expected Return'] = ((equity_calcs.us_equity_return - equity_calcs.cash) * df_alts_us_no_ir['Beta To Use'] + equity_calcs.cash)
alts_returns_us_no_ir = df_alts_us_no_ir['Expected Return']

# %%
alts_returns_us = df_alts_us_no_ir['Expected Return']

alts_returns_us = alts_returns_us_ir.append(alts_returns_us_no_ir)
alts_returns_us

# %% [markdown]
# # Non USD

# %%
alts_nonus_name = list(filter(None, list({k:v for (k,v) in cma.val_dict.items() if 'alts_nonus_name' in k}.values())))
alts_nonus_beta =list(filter(None, list({k:v for (k,v) in cma.val_dict.items() if 'alts_nonus_beta' in k}.values())))
alts_nonus_ir =list(filter(None, list({k:v for (k,v) in cma.val_dict.items() if 'alts_nonus_ir' in k}.values())))

df_beta_relative_alts = pd.DataFrame(list(zip(alts_nonus_name, alts_nonus_beta, alts_nonus_ir)), columns =['Asset Class', 'Beta Relative To', 'Information Ratio']) 
df_beta_relative_alts = df_beta_relative_alts.set_index('Asset Class')
 
df_expected_return = equity_calcs.df_beta_reference_nonus.join(df_beta_relative_alts, how='outer')

# Fill beta for alts non local adjusted returns
df_expected_return.loc[alts_nonus_name, :'USD_U.S. Equity'] = df_expected_return.loc[['USD_'+s for s in alts_nonus_name], :'USD_U.S. Equity'].values.tolist()

# %% [markdown]
# ## IR Adjusted Returns

# %%
# Calculate returns for alts with IR adjustments
df_alts_returns_nonus_ir = df_expected_return.dropna(subset=['Information Ratio']).copy(deep=True)
df_alts_returns_nonus_ir['Expected Return'] = np.nan

# Retrieve finalized standard deviaions for use in calcs
std_dev = pd.DataFrame(std_dev.annual_adj_std_dev_nonus)
std_dev = std_dev.rename(columns={0: 'Std Dev'})

df_alts_returns_nonus_ir = df_alts_returns_nonus_ir.join(std_dev, how='outer')
df_alts_returns_nonus_ir = df_alts_returns_nonus_ir.dropna(subset=['Information Ratio'])

# %%
df_alts_returns_nonus_ir['Std Dev to Use'] = std_dev.loc['USD_U.S. Equity', 'Std Dev']

# Fill std deviations and beta to use for non local adjusted returns
sd_to_use = std_dev.loc[['USD_'+s for s in alts_nonus_name], 'Std Dev'].values.tolist()
df_alts_returns_nonus_ir.loc[alts_nonus_name, 'Std Dev'] = sd_to_use

beta_to_use = df_expected_return.loc[['USD_'+s for s in alts_nonus_name], 'USD_U.S. Equity'].values.tolist()
df_alts_returns_nonus_ir.loc[alts_nonus_name, 'Beta To Use'] = beta_to_use

# %%
# Residual Risk
df_alts_returns_nonus_ir['Residual Risk'] = (df_alts_returns_nonus_ir['Std Dev']**2 - df_alts_returns_nonus_ir['Beta To Use']**2 * df_alts_returns_nonus_ir['Std Dev to Use']**2)**(1/2)

# %%
# Revert beta back to local for final return calc
df_beta_revert = equity_calcs.df_beta_reference_nonus.join(df_beta_relative_alts, how='outer').dropna(subset=['Information Ratio'])
df_beta_revert = df_beta_revert.loc[:, 'U.S. Equity']

# %%
# Calc final expected return
df_alts_returns_nonus_ir['Expected Return'] = equity_calcs.cash/100 + (equity_calcs.equity_returns_nonus['U.S. Equity']/100 - equity_calcs.cash/100)\
    * df_beta_revert + df_alts_returns_nonus_ir['Information Ratio'] * df_alts_returns_nonus_ir['Residual Risk']

alts_returns_nonus = (df_alts_returns_nonus_ir['Expected Return']*100).round(1)      
alts_returns_nonus

# %%
