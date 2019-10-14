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

# # Functions

def beta_matrix(covariance_matrix, standard_deviations, beta_reference, name_reference):
    df_beta =  pd.DataFrame(0, index=covariance_matrix.columns, columns=covariance_matrix.columns)
    
    # Set reference asset classes to 1
    for i in range(len(df_beta.columns)):
        df_beta.iloc[i, i] = 1
    
    # Calculate all betas
    beta_calc = []
    for i in range(len(covariance_matrix.columns)):
        sub = df_beta.iloc[i,:].dot(covariance_matrix).div(standard_deviations.iloc[i,:].values[0]**2)
        beta_calc.append(sub)
    df_beta_calc = pd.DataFrame(beta_calc).T
    
    # Create dataframe with beta results
    df_beta_relative_beta = list(filter(None, list({k:v for (k,v) in cma.val_dict.items() if beta_reference in k}.values())))
    df_beta_relative_name = list(filter(None, list({k:v for (k,v) in cma.val_dict.items() if name_reference in k}.values())))
    df_beta_relative = pd.DataFrame(zip(df_beta_relative_name, df_beta_relative_beta), columns =['Asset Class', 'Beta Relative To']).set_index('Asset Class')
    df_expected_return = df_beta_calc.join(df_beta_relative, how='outer')
    
    return df_expected_return, df_beta_calc


# # USD

# ## Building Block Returns

# +
# Calculate building block asset classes
cash = 2.60

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

df_expected_return_us, df_beta_reference_us = beta_matrix(std_dev.exp_cov_us, std_dev.annual_adj_std_dev_us, 'equity_us_beta', 'equity_us_name')    

# +
# Fill in building block returns
df_expected_return_us['Expected Return'] = 'NaN'

df_expected_return_us.loc[['U.S. Equity', 'Global Equity', 'International Developed Equity', 'Global Emerging Markets Equity'], 'Expected Return'] = (
    us_equity_return, gl_equity_return, intl_equity_return, em_equity_return)
# -

# Fill in beta-relative returns
df_expected_return_us.loc[df_expected_return_us['Beta Relative To'] == 'Global Emerging Markets Equity', 'Expected Return'] = ((em_equity_return - cash) * df_expected_return_us['Global Emerging Markets Equity'] + cash)
df_expected_return_us.loc[df_expected_return_us['Beta Relative To'] == 'Global Equity', 'Expected Return'] = ((gl_equity_return - cash) * df_expected_return_us['Global Equity'] + cash)
df_expected_return_us.loc[df_expected_return_us['Beta Relative To'] == 'International Developed Equity', 'Expected Return'] = ((intl_equity_return - cash) * df_expected_return_us['International Developed Equity'] + cash)
df_expected_return_us.loc[df_expected_return_us['Beta Relative To'] == 'U.S. Equity', 'Expected Return'] = ((us_equity_return - cash) * df_expected_return_us['U.S. Equity'] + cash)

# Finalize expected returns
equity_returns_us = df_expected_return_us.dropna(subset=['Beta Relative To'])
equity_returns_us = equity_returns_us.loc[:,'Expected Return']

# # NON-USD

# ## Building Block Returns

# +
# Calculate building block asset classes
cash_nonus = 2.50

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

df_expected_return_nonus, df_beta_reference_nonus = beta_matrix(std_dev.exp_cov_nonus, std_dev.annual_adj_std_dev_nonus, 'equity_nonus_beta', 'equity_nonus_name')   
# -

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
    ((df_expected_return_nonus.loc['U.S. Equity','Expected Return'] - cash_nonus) * df_expected_return_nonus['U.S. Equity'] + cash_nonus)

df_expected_return_nonus.loc[df_expected_return_nonus['Beta Relative To'] == 'Europe Ex-UK Equity', 'Expected Return'] = \
    ((df_expected_return_nonus.loc['Europe Ex-UK Equity','Expected Return'] - cash_nonus) * df_expected_return_nonus['Europe Ex-UK Equity'] + cash_nonus)

df_expected_return_nonus.loc[df_expected_return_nonus['Beta Relative To'] == 'Japan Equity', 'Expected Return'] = \
    ((df_expected_return_nonus.loc['Japan Equity','Expected Return'] - cash_nonus) * df_expected_return_nonus['Japan Equity'] + cash_nonus)


# +
# Finalize expected returns
equity_returns_nonus = df_expected_return_nonus.dropna(subset=['Beta Relative To'])
equity_returns_nonus = equity_returns_nonus.loc[:,'Expected Return']

# Reorder
df_equity_nonus = pd.read_excel(
    "P:\\Advisory\\Research\\Automation\\CMAs\\Data\\bloomberg_data_nonus.xlsx", sheet_name='equity_returns', index_col=0)
expected_return_equity_nonus_order = df_equity_nonus.columns.tolist()

equity_returns_nonus = equity_returns_nonus.reindex(index=expected_return_equity_nonus_order)
# -


