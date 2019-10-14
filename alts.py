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
from std_dev import annual_adj_std_dev_nonus

import numpy as np
import pandas as pd

# %% [markdown]
# # US

# %%

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
std_dev = pd.DataFrame(annual_adj_std_dev_nonus)
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
df_alts_returns_nonus_ir['Expected Return'] = equity_calcs.cash/100 + (equity_calcs.expected_return_equity_nonus['U.S. Equity']/100 - equity_calcs.cash/100)\
    * df_beta_revert + df_alts_returns_nonus_ir['Information Ratio'] * df_alts_returns_nonus_ir['Residual Risk']

expected_return_alts_nonus_ir = (df_alts_returns_nonus_ir['Expected Return']*100).round(1)      
expected_return_alts_nonus_ir
