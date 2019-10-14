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
import std_dev

import pandas as pd
# -

# # USD

# ## Building Block Returns

# +
# Calculate building block asset classes
cash = 2.50

us_equity_return = cma.val_dict['us_inflation'] + cma.val_dict['us_reg'] + cma.val_dict['us_equity_income'] +\
    cma.val_dict['us_equity_val'] + cma.val_dict['us_equity_buyback']

intl_equity_return = cma.val_dict['us_inflation'] + cma.val_dict['gl_exus_reg'] + cma.val_dict['gl_exus_equity_income'] +\
    cma.val_dict['gl_exus_equity_val'] + cma.val_dict['gl_exus_equity_buyback']

em_equity_return = cma.val_dict['us_inflation'] + cma.val_dict['em_reg'] + cma.val_dict['em_equity_income'] +\
    cma.val_dict['em_equity_val'] + cma.val_dict['em_equity_buyback']

gl_equity_return = (0.55 * us_equity_return) + (0.335 * intl_equity_return) + (0.11 * em_equity_return)
# -

# ## Beta Calcs

# +
# Import returns
df_returns_us = pd.read_csv('P:\\Advisory\\Research\\Automation\\CMAs\\Data\\combined_returns_us.csv', index_col=0)

# Beta references
df_beta = df_returns_us.iloc[:6, :].copy(deep=True)
df_beta.index = ['Commodities', 'Global Emerging Markets Equity', 'Global Equity',
                    'International Developed Equity', 'U.S. Equity', 'U.S. REIT']

# Set all values to 0 initially
for col in df_beta.columns:
    df_beta[col].values[:] = 0
    
# Set reference asset classes to 1
df_beta.loc['Commodities', 'Commodities'] = 1
df_beta.loc['Global Emerging Markets Equity', 'Global Emerging Markets Equity'] = 1
df_beta.loc['Global Equity', 'Global Equity'] = 1
df_beta.loc['International Developed Equity', 'International Developed Equity'] = 1
df_beta.loc['U.S. Equity', 'U.S. Equity'] = 1
df_beta.loc['U.S. REIT', 'U.S. REIT'] = 1

# +
# Beta Matrix
df_beta_comm = (df_beta.loc['Commodities',:]).dot(std_dev.exp_cov_us).div(std_dev.annual_adj_std_dev_us.loc['Commodities',:].values[0]**2)
df_beta_em = (df_beta.loc['Global Emerging Markets Equity',:]).dot(std_dev.exp_cov_us).div(std_dev.annual_adj_std_dev_us.loc['Global Emerging Markets Equity',:].values[0]**2)
df_beta_global = (df_beta.loc['Global Equity',:]).dot(std_dev.exp_cov_us).div(std_dev.annual_adj_std_dev_us.loc['Global Equity',:].values[0]**2)
df_beta_intl = (df_beta.loc['International Developed Equity',:]).dot(std_dev.exp_cov_us).div(std_dev.annual_adj_std_dev_us.loc['International Developed Equity',:].values[0]**2)
df_beta_us = (df_beta.loc['U.S. Equity',:]).dot(std_dev.exp_cov_us).div(std_dev.annual_adj_std_dev_us.loc['U.S. Equity',:].values[0]**2)
df_beta_us_reit = (df_beta.loc['U.S. REIT',:]).dot(std_dev.exp_cov_us).div(std_dev.annual_adj_std_dev_us.loc['U.S. REIT',:].values[0]**2)

df_beta_reference = pd.concat([df_beta_comm, df_beta_em, df_beta_global, df_beta_intl, df_beta_us, df_beta_us_reit], axis=1)
df_beta_reference
# -

# Create beta dataframe
df_beta_relative_beta = list(filter(None, list({k:v for (k,v) in cma.val_dict.items() if 'equity_us_beta' in k}.values())))
df_beta_relative_name = list(filter(None, list({k:v for (k,v) in cma.val_dict.items() if 'equity_us_name' in k}.values())))
df_beta_relative = pd.DataFrame(zip(df_beta_relative_name, df_beta_relative_beta), columns =['Asset Class', 'Beta Relative To']).set_index('Asset Class')
df_expected_return = df_beta_reference.join(df_beta_relative, how='outer')

# +
# Fill in building block returns
df_expected_return['Expected Return'] = 'NaN'

df_expected_return.loc[['U.S. Equity', 'Global Equity', 'International Developed Equity', 'Global Emerging Markets Equity'], 'Expected Return'] = (
    us_equity_return, gl_equity_return, intl_equity_return, em_equity_return)
# -

# Fill in beta-relative returns
df_expected_return.loc[df_expected_return['Beta Relative To'] == 'Global Emerging Markets Equity', 'Expected Return'] = ((em_equity_return - cash) * df_expected_return['Global Emerging Markets Equity'] + cash)
df_expected_return.loc[df_expected_return['Beta Relative To'] == 'Global Equity', 'Expected Return'] = ((gl_equity_return - cash) * df_expected_return['Global Equity'] + cash)
df_expected_return.loc[df_expected_return['Beta Relative To'] == 'International Developed Equity', 'Expected Return'] = ((intl_equity_return - cash) * df_expected_return['International Developed Equity'] + cash)
df_expected_return.loc[df_expected_return['Beta Relative To'] == 'U.S. Equity', 'Expected Return'] = ((us_equity_return - cash) * df_expected_return['U.S. Equity'] + cash)

# +
# Finalize expected returns
equity_returns_us = df_expected_return.dropna(subset=['Beta Relative To'])
equity_returns_us = equity_returns_us.loc[:,'Expected Return']

equity_returns_us
# -

# # NON-USD

# ## Building Block Returns

# +
# Calculate building block asset classes
cash_nonus = 2.60

us_equity_return = cma.val_dict['us_inflation'] + cma.val_dict['us_equity_income'] + cma.val_dict['us_equity_buyback'] +\
                    cma.val_dict['us_real_gdp'] + cma.val_dict['us_equity_val']

europe_ex_uk_equity_return = cma.val_dict['us_inflation'] + cma.val_dict['europe_ex_uk_equity_income'] + cma.val_dict['europe_ex_uk_equity_buyback'] +\
                               cma.val_dict['europe_ex_uk_real_gdp'] + cma.val_dict['europe_ex_uk_equity_val']

uk_equity_return = cma.val_dict['us_inflation'] + cma.val_dict['uk_equity_income'] + cma.val_dict['uk_equity_buyback'] +\
                               cma.val_dict['uk_real_gdp'] + cma.val_dict['uk_equity_val']

japan_equity_return = cma.val_dict['us_inflation'] + cma.val_dict['japan_equity_income'] + cma.val_dict['japan_equity_buyback'] +\
                               cma.val_dict['japan_real_gdp'] + cma.val_dict['japan_equity_val']

apac_ex_japan_equity_return = cma.val_dict['us_inflation'] + cma.val_dict['apac_ex_japan_equity_income'] + cma.val_dict['apac_ex_japan_equity_buyback'] +\
                               cma.val_dict['apac_ex_japan_real_gdp'] + cma.val_dict['apac_ex_japan_equity_val']

emerging_equity_return = cma.val_dict['us_inflation'] + cma.val_dict['em_equity_income'] + cma.val_dict['em_equity_buyback'] +\
                               cma.val_dict['em_real_gdp'] + cma.val_dict['em_equity_val']
# -

# ## Beta Calcs

# +
# Import returns
df_returns_nonus = pd.read_csv('P:\\Advisory\\Research\\Automation\\CMAs\\Data\\combined_returns_nonus.csv', index_col=0)

# Beta references
df_beta_nonus = df_returns_nonus.iloc[:4, :].copy(deep=True)
df_beta_nonus.index = ['U.S. Equity', 'Europe Ex-UK Equity', 'Japan Equity', 'USD_U.S. Equity']

# Set all values to 0 initially
for col in df_beta_nonus.columns:
    df_beta_nonus[col].values[:] = 0
    
# Set reference asset classes to 1
df_beta_nonus.loc['U.S. Equity', 'U.S. Equity'] = 1
df_beta_nonus.loc['Europe Ex-UK Equity', 'Europe Ex-UK Equity'] = 1
df_beta_nonus.loc['Japan Equity', 'Japan Equity'] = 1
df_beta_nonus.loc['USD_U.S. Equity', 'USD_U.S. Equity'] = 1

# +
# Beta Matrix
df_beta_us_nonus = (df_beta_nonus.loc['U.S. Equity',:]).dot(std_dev.exp_cov_nonus).div(std_dev.annual_adj_std_dev_nonus.loc['U.S. Equity',:].values[0]**2)
df_beta_europe_ex_uk_nonus = (df_beta_nonus.loc['Europe Ex-UK Equity',:]).dot(std_dev.exp_cov_nonus).div(std_dev.annual_adj_std_dev_nonus.loc['Europe Ex-UK Equity'].values[0]**2)
df_beta_japan_nonus = (df_beta_nonus.loc['Japan Equity',:]).dot(std_dev.exp_cov_nonus).div(std_dev.annual_adj_std_dev_nonus.loc['Japan Equity'].values[0]**2)
df_beta_us_usd_nonus = (df_beta_nonus.loc['USD_U.S. Equity',:]).dot(std_dev.exp_cov_nonus).div(std_dev.annual_adj_std_dev_nonus.loc['USD_U.S. Equity'].values[0]**2)

df_beta_reference_nonus = pd.concat([df_beta_us_nonus, df_beta_europe_ex_uk_nonus, df_beta_japan_nonus, df_beta_us_usd_nonus], axis=1)
# -

# Create beta dataframe
df_beta_relative_beta_nonus = list(filter(None, list({k:v for (k,v) in cma.val_dict.items() if 'equity_nonus_beta' in k}.values())))
df_beta_relative_name_nonus = list(filter(None, list({k:v for (k,v) in cma.val_dict.items() if 'equity_nonus_name' in k}.values())))
df_beta_relative_nonus = pd.DataFrame(zip(df_beta_relative_name_nonus, df_beta_relative_beta_nonus), columns =['Asset Class', 'Beta Relative To']).set_index('Asset Class')
df_expected_return_nonus = df_beta_reference_nonus.join(df_beta_relative_nonus, how='outer')

# ## Equity Returns

# +
# Fill in building block returns
df_expected_return_nonus['Expected Return'] = 'NaN'

df_expected_return_nonus.loc[['U.S. Equity', 'Europe Ex-UK Equity', 'UK Equity','Japan Equity', 'Developed Market Pacific Ex-Japan Equity', 
                              'Global Emerging Markets Equity'], 'Expected Return'] = (
                              us_equity_return - cma.val_dict['us_inflation'] + cma.val_dict['country_inflation'],
                              europe_ex_uk_equity_return - cma.val_dict['us_inflation'] + cma.val_dict['country_inflation'],
                              uk_equity_return - cma.val_dict['us_inflation'] + cma.val_dict['country_inflation'],
                              japan_equity_return - cma.val_dict['us_inflation'] + cma.val_dict['country_inflation'],
                              apac_ex_japan_equity_return - cma.val_dict['us_inflation'] + cma.val_dict['country_inflation'],
                              emerging_equity_return - cma.val_dict['us_inflation'] + cma.val_dict['country_inflation'])

# +
#Fill in beta-relative returns
df_expected_return_nonus.loc[df_expected_return_nonus['Beta Relative To'] == 'U.S. Equity', 'Expected Return'] = \
    ((df_expected_return_nonus.loc['U.S. Equity','Expected Return'] - cash) * df_expected_return_nonus['U.S. Equity'] + cash)

df_expected_return_nonus.loc[df_expected_return_nonus['Beta Relative To'] == 'Europe Ex-UK Equity', 'Expected Return'] = \
    ((df_expected_return_nonus.loc['Europe Ex-UK Equity','Expected Return'] - cash) * df_expected_return_nonus['Europe Ex-UK Equity'] + cash)

df_expected_return_nonus.loc[df_expected_return_nonus['Beta Relative To'] == 'Japan Equity', 'Expected Return'] = \
    ((df_expected_return_nonus.loc['Japan Equity','Expected Return'] - cash) * df_expected_return_nonus['Japan Equity'] + cash)


# +
# Finalize expected returns
equity_returns_nonus = df_expected_return_nonus.dropna(subset=['Beta Relative To'])
equity_returns_nonus = equity_returns_nonus.loc[:,'Expected Return']

# Reorder
df_equity_nonus = pd.read_excel(
    "P:\\Advisory\\Research\\Automation\\CMAs\\Data\\bloomberg_data_nonus.xlsx", sheet_name='equity_returns', index_col=0)
expected_return_equity_nonus_order = df_equity_nonus.columns.tolist()

equity_returns_nonus = equity_returns_nonus.reindex(index=expected_return_equity_nonus_order)
equity_returns_nonus
# -

