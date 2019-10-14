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

from statsmodels.stats.weightstats import DescrStatsW

# +
# Exponential weight
count = [x for x in range(240)]
count.reverse()

percent = [(1-cma.val_dict['lambda_val'])*(cma.val_dict['lambda_val']**x) for x in count]
sum_val = sum(percent)

exponential_weight = pd.Series([x / sum_val for x in percent])
# -
# # Define functions

# ## Standard deviation functions


# +
def monthly_standard_dev(dataframe_returns, exponential_weight):
    # Monthly variance
    df_variance = (dataframe_returns - dataframe_returns.mean())**2 
    func = lambda x: np.asarray(x) * np.asarray(exponential_weight)
    df_variance = df_variance.apply(func)
    monthly_variance = df_variance.sum()

    # Monthly standard deviation
    monthly_std_dev = np.sqrt(monthly_variance)   
    return monthly_std_dev


def exponential_std_dev(monthly_std_dev, exponential_weight, dataframe_returns):
    # Annual adjusted standard deviation
    monthly_std_dev_list = monthly_std_dev.tolist()

    adj_sd_list2 = [x**2 for x in monthly_std_dev_list]
    sum_prod = (1 + pd.Series([dataframe_returns.iloc[:,x].values.dot(exponential_weight.values) 
                               for x in range(len(dataframe_returns.columns))]))**2

    base = [sum(x) for x in zip(sum_prod, adj_sd_list2)]
    equation_p1 = [x**12 for x in base]

    sum_prod2 = (1 + pd.Series([dataframe_returns.iloc[:,x].values.dot(exponential_weight.values) 
                                for x in range(len(dataframe_returns.columns))]))

    base_2 = sum_prod2.tolist()
    equation_p2 = [x ** (2*12) for x in base_2]

    pre_final = [x-y for x,y in zip(equation_p1, equation_p2)]

    annual_adj_std_dev = pd.DataFrame(np.sqrt(pre_final))
    annual_adj_std_dev.index = dataframe_returns.columns
    
    return annual_adj_std_dev


# -

# ## Covariance and Correlation Matrices Functions

# +
def value_minus_mean(dataframe_returns, monthly_std_dev, exponential_weight):
    # Value Minus Mean / Standard Deviation
    average = dataframe_returns.mean()
    value_minus_mean_div_sd = (dataframe_returns.sub(average)).div(monthly_std_dev)
    value_minus_mean_div_sd.index = exponential_weight.index
    return value_minus_mean_div_sd

def exponential_correlation(value_minus_mean, exponential_weight):
    exp_corr_raw = []
    for x in range(len(value_minus_mean.columns)):
        col = [(value_minus_mean.iloc[:,x]*value_minus_mean.iloc[:,i]*exponential_weight).sum() for i in range(len(value_minus_mean.columns))]
        exp_corr_raw.append(col)
    
    exp_corr = pd.DataFrame(exp_corr_raw)
    exp_corr.index = value_minus_mean.columns
    exp_corr.columns = value_minus_mean.columns
    return exp_corr

def stand_dev_matrix(annual_adj_std_dev):
    df_annual_adj_std_dev = pd.DataFrame(annual_adj_std_dev)
    matrix_sd = df_annual_adj_std_dev.dot(df_annual_adj_std_dev.T)
    return matrix_sd


# -

# # USD

# ## Import Data

# +
# Extract Indices
equity_us_code = list(filter(None, list({k:v for (k,v) in cma.val_dict.items() if 'equity_us_code' in k}.values())))
fixed_us_code = list(filter(None, list({k:v for (k,v) in cma.val_dict.items() if 'fixed_us_code' in k}.values())))
alts_us_code = list(filter(None, list({k:v for (k,v) in cma.val_dict.items() if 'alts_us_code' in k}.values())))

# Import returns
df_returns_us = pd.read_csv('P:\\Advisory\\Research\\Automation\\CMAs\\Data\\combined_returns_us.csv', index_col=0)/100
# -
# ## Standard Deviations

# +
# Monthly standard deviation
monthly_std_dev_us = monthly_standard_dev(df_returns_us, exponential_weight)

# Annual adjusted standard deviation
annual_adj_std_dev_us = exponential_std_dev(monthly_std_dev_us, exponential_weight, df_returns_us)
# -

# ## Covariance and Correlation Matrices

# +
value_minus_mean_div_sd_us = value_minus_mean(df_returns_us, monthly_std_dev_us, exponential_weight)

# Exponential correlation
exp_corr_us = exponential_correlation(value_minus_mean_div_sd_us, exponential_weight)

# Exponential covariance
matrix_sd_us = stand_dev_matrix(annual_adj_std_dev_us)
exp_cov_us = exp_corr_us.mul(matrix_sd_us, axis=0)

# Final correlation matrix
corr_matrix_final_us = (exp_cov_us.div(matrix_sd_us))
# -

# # Non-USD

# ## Import Data

# +
# Extract Indices
equity_nonus_code = list(filter(None, list({k:v for (k,v) in cma.val_dict.items() if 'equity_nonus_code' in k}.values())))
fixed_nonus_code = list(filter(None, list({k:v for (k,v) in cma.val_dict.items() if 'fixed_nonus_code' in k}.values())))
alts_nonus_code = list(filter(None, list({k:v for (k,v) in cma.val_dict.items() if 'alts_nonus_code' in k}.values())))

# Import returns
df_returns_nonus = pd.read_csv('P:\\Advisory\\Research\\Automation\\CMAs\\Data\\combined_returns_nonus.csv', index_col=0)
# -

# ## Standard Deviations

# +
# Monthly standard deviation
monthly_std_dev_nonus = monthly_standard_dev(df_returns_nonus, exponential_weight)

# Annual adjusted standard deviation
annual_adj_std_dev_nonus = exponential_std_dev(monthly_std_dev_nonus, exponential_weight, df_returns_nonus)
# -

# ## Covariance and Correlation Matrices

# +
value_minus_mean_div_sd_nonus = value_minus_mean(df_returns_nonus, monthly_std_dev_nonus, exponential_weight)

# Exponential correlation
exp_corr_nonus = exponential_correlation(value_minus_mean_div_sd_nonus, exponential_weight)

# Exponential covariance
matrix_sd_nonus = stand_dev_matrix(annual_adj_std_dev_nonus)
exp_cov_nonus = exp_corr_nonus.mul(matrix_sd_nonus, axis=0)

# Final correlation matrix
corr_matrix_final_nonus = (exp_cov_nonus.div(matrix_sd_nonus))
