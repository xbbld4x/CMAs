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
import math
import numpy as np
import operator
import pandas as pd

from datetime import date
from datetime import datetime
from dateutil.relativedelta import relativedelta
from nelson_siegel_svensson.calibrate import betas_ns_ols
from scipy import stats
from scipy.stats import mstats
# -

# Date range for dataframes
last_date = datetime.strptime(cma.val_dict['as_of_date'], '%m-%d-%Y')
first_date = last_date - relativedelta(years=20)

# # US Term Structure

# +
# Import Treasury Information
df_treas_yields = pd.read_excel('P:\\Advisory\\Research\\Automation\\CMAs\\Data\\term_structure_data.xlsx', sheet_name='us_treas_yld', index_col=0)
df_treas_durations = pd.read_excel('P:\\Advisory\\Research\\Automation\\CMAs\\data\\term_structure_data.xlsx', sheet_name='us_treas_dur', index_col=0)

# Filter dataframes to only include 20 years of data
df_treas_yields = df_treas_yields.loc[:cma.val_dict['as_of_date'], :]
df_treas_durations = df_treas_durations.loc[:cma.val_dict['as_of_date'], :]

# Get latest values
current_yield_list = (df_treas_yields.iloc[-1,:] / 100).round(4) 
current_yield_list = current_yield_list.to_list()

current_duration_list = (df_treas_durations.iloc[-1,:]).round(4) 
current_duration_list = current_duration_list.to_list()

# +
# Calculate Normalized Rates
term_premium = [cma.val_dict['term_prem_3mo'], cma.val_dict['term_prem_5yr']/100, cma.val_dict['term_prem_10yr']/100, cma.val_dict['term_prem_30yr']/100]

future_yield = (cma.val_dict['us_inflation']/100 + cma.val_dict['us_rcr']/100)
future_yield_list = [future_yield, (future_yield + cma.val_dict['term_prem_5yr']/100), (future_yield + cma.val_dict['term_prem_10yr']/100), 
                     (future_yield + cma.val_dict['term_prem_30yr']/100)]

future_duration_list = current_duration_list

interest_rates = {'Current_Yield':current_yield_list,
                  'Current_Duration':current_duration_list,
                  'Term_Premium': term_premium,
                  'Future_Yield':future_yield_list,
                  'Future_Duration':future_duration_list}

df_interest_rates = pd.DataFrame(interest_rates)
df_interest_rates = df_interest_rates.rename(index = {0: "three_mo",
                                                      1: "five_yr",
                                                      2: "ten_yr",
                                                      3: "thirty_yr"})


df_interest_rates = df_interest_rates.round(4)
df_interest_rates.loc[:,['Current_Duration', 'Future_Duration']] = df_interest_rates.loc[:,['Current_Duration', 'Future_Duration']].round(2)

# +
# Curve parameters
df_yield_10yr = pd.DataFrame(df_interest_rates['Current_Yield'])

for i in range(1,11):
    df_yield_10yr[i] = np.nan

yield_norm = df_interest_rates['Future_Yield']

# Normalized values
for i in range(cma.val_dict['yield_norm_yrs'], 11):
     df_yield_10yr.iloc[:,i] = yield_norm

# Path to reach normalized yield state
for i in range(1, cma.val_dict['yield_norm_yrs']):
     df_yield_10yr.iloc[:, i] = (df_interest_rates['Future_Yield'] - df_interest_rates['Current_Yield']) / cma.val_dict['yield_norm_yrs'] + df_yield_10yr.iloc[:,i-1]

# +
# Determine parameters for each year
df_yield_params = pd.DataFrame(['NaN', 'NaN', 'NaN'], columns=['Current'])

for i in range(1,11):
    df_yield_params[i] = np.nan

tau=1.65

param_list = []
for i in range(0, 11):
    t = np.array(df_interest_rates['Current_Duration'])
    y = np.array(df_yield_10yr.iloc[:,i])
    
    curve, status = betas_ns_ols(tau, t, y)
    curve = str(curve)

    B0 = float((curve.split('=')[1]).split(',')[0])
    B1 = float((curve.split('=')[2]).split(',')[0])
    B2 = float((curve.split('=')[3]).split(',')[0])
    param = [B0, B1, B2]
    df_yield_params.iloc[:,i] = param

# +
# US Yield Curve Over Next 10 Years
term_structure = (np.arange(0.5, 100.5, 0.5))

curve_list = []
for i in range(0, 11):
    curve_item = [df_yield_params.iloc[0,i] + df_yield_params.iloc[1,i] * (tau / x) * (1 - math.exp(-x / tau)) + df_yield_params.iloc[2,i] * (tau / x) * (1 - (1 + x / tau) * math.exp(-x / tau)) for x in term_structure]
    curve_list.append(curve_item)
    
df_us_yield_curves = pd.DataFrame(curve_list).T
df_us_yield_curves['Term Structure'] = term_structure
# -

# # Global Term Structure

# +
# Normalized Rates
df_gl_treas_yields = pd.read_excel('P:\\Advisory\\Research\\Automation\\CMAs\\Data\\term_structure_data.xlsx', sheet_name='gl_treas_yld', index_col=0)
df_gl_treas_durations = pd.read_excel('P:\\Advisory\\Research\\Automation\\CMAs\\Data\\term_structure_data.xlsx', sheet_name='gl_treas_dur', index_col=0)

# Filter dataframes to only include 20 years of data
df_gl_treas_yields = df_gl_treas_yields.loc[:cma.val_dict['as_of_date'], :]
df_gl_treas_durations = df_gl_treas_durations.loc[:cma.val_dict['as_of_date'], :]

# +
gl_current_yield_list = (df_gl_treas_yields.iloc[-1,:] / 100).round(4) 
gl_current_yield_list = gl_current_yield_list.to_list()
gl_current_yield_list.insert(0, 0.010)

gl_current_duration_list = (df_gl_treas_durations.iloc[-1,:]).round(2) 
gl_current_duration_list = gl_current_duration_list.to_list()
gl_current_duration_list.insert(0, 0.25)

# GL term premium
iteration_list_gl_tp = [abs(df_us_yield_curves['Term Structure'] - x).idxmin() for x in gl_current_duration_list]

for i in range(6):
      gl_term_premium = [df_us_yield_curves.iloc[x, i] - future_yield for x in iteration_list_gl_tp]
gl_term_premium[:] = [x - cma.val_dict['gl_theme_tp_adjust'] for x in gl_term_premium]
gl_term_premium[0] = 0

# +
gl_future_yield = (cma.val_dict['global_inflation']/100 + cma.val_dict['global_rcr']/100)

gl_future_yield_list = [gl_future_yield, (gl_future_yield + gl_term_premium[1]), (gl_future_yield + gl_term_premium[2]),
                        (gl_future_yield + gl_term_premium[3]), (gl_future_yield + gl_term_premium[4]), (gl_future_yield + gl_term_premium[5])]
gl_future_duration_list = gl_current_duration_list

gl_interest_rates = {'Current_Yield':gl_current_yield_list,
                     'Current_Duration':gl_current_duration_list,
                     'Term_Premium': gl_term_premium,
                     'Future_Yield':gl_future_yield_list,
                     'Future_Duration':gl_future_duration_list}

df_gl_interest_rates = pd.DataFrame(gl_interest_rates)
df_gl_interest_rates = df_gl_interest_rates.rename(index = {0: "3 Mo LIBOR",
                                                            1: "1-3 Yr",
                                                            2: "3-5 Yr",
                                                            3: "5-7 Yr",
                                                            4: "7-10 Yr",
                                                            5: "10+ Yr"})

# +
# Current Curve Parameters
t = np.array(df_gl_interest_rates['Current_Duration'])
y = np.array(df_gl_interest_rates['Current_Yield'])

curve, status = betas_ns_ols(tau, t, y)
curve = str(curve)

# Extract paramaters from results
B0_gl_curr = float((curve.split('=')[1]).split(',')[0])
B1_gl_curr = float((curve.split('=')[2]).split(',')[0])
B2_gl_curr = float((curve.split('=')[3]).split(',')[0])
param_gl_curr = [B0_gl_curr, B1_gl_curr, B2_gl_curr]

# +
# Future Curve Parameters
t = np.array(df_gl_interest_rates['Future_Duration'])
y = np.array(df_gl_interest_rates['Future_Yield'])

curve, status = betas_ns_ols(tau, t, y)
curve = str(curve)

# Extract paramaters from results
B0_gl_future = float((curve.split('=')[1]).split(',')[0])
B1_gl_future = float((curve.split('=')[2]).split(',')[0])
B2_gl_future = float((curve.split('=')[3]).split(',')[0])
param_gl_future = [B0_gl_future, B1_gl_future, B2_gl_future]
# -

# Yield Curves Next 10 Yrs
gl_term_structure = (np.arange(0.5, 100.5, 0.5))

# +
gl_curr_yield = [B0_gl_curr + B1_gl_curr * (tau / x) * (1 - math.exp(-x / tau)) + B2_gl_curr * (tau / x) * (1 - (1 + x / tau) * math.exp(-x / tau)) for x in gl_term_structure]

df_gl_yield_curves = pd.DataFrame(df_us_yield_curves.iloc[:,0])

for i in range(1,11):
    df_gl_yield_curves[i] = np.nan
df_gl_yield_curves.iloc[:,0] = gl_curr_yield

# Normalized Values
for i in range(cma.val_dict['gl_yield_norm_yrs'], 11):
     df_gl_yield_curves.iloc[:,i] = [B0_gl_future + B1_gl_future * (tau / x) * (1 - math.exp(-x / tau)) + B2_gl_future * (tau / x) * (1 - (1 + x / tau) * math.exp(-x / tau)) for x in gl_term_structure]

# Path to reach normalized yield state
for i in range(1, cma.val_dict['gl_yield_norm_yrs']):
     df_gl_yield_curves.iloc[:, i] = (df_gl_yield_curves.iloc[:,cma.val_dict['gl_yield_norm_yrs']] - 
                                      df_gl_yield_curves.iloc[:,0]) / cma.val_dict['gl_yield_norm_yrs'] + df_gl_yield_curves.iloc[:,i-1]

df_gl_yield_curves['Term Structure'] = gl_term_structure
# -

# # EM Term Structure

# +
# Normalized Rates
df_em_treas_yields = pd.read_excel('P:\\Advisory\\Research\\Automation\\CMAs\\Data\\term_structure_data.xlsx', sheet_name='em_treas_yld', index_col=0)
df_em_treas_durations = pd.read_excel('P:\\Advisory\\Research\\Automation\\CMAs\\Data\\term_structure_data.xlsx', sheet_name='em_treas_dur', index_col=0)

# Filter dataframes to only include 20 years of data
df_em_treas_yields = df_em_treas_yields.loc[:cma.val_dict['as_of_date'], :]
df_em_treas_durations = df_em_treas_durations.loc[:cma.val_dict['as_of_date'], :]

# +
em_current_yield_list = (df_em_treas_yields.iloc[-1,:] / 100)
em_current_yield_list = em_current_yield_list.to_list()
em_current_yield_list.insert(0, 0.045)

em_current_duration_list = (df_em_treas_durations.iloc[-1,:])
em_current_duration_list = em_current_duration_list.to_list()
em_current_duration_list.insert(0, 0.25)

# EM term premium
iteration_list_em_tp = [abs(df_us_yield_curves['Term Structure'] - x).idxmin() for x in em_current_duration_list]

for i in range(6):
      em_term_premium = [df_us_yield_curves.iloc[x, i] - future_yield for x in iteration_list_em_tp]
em_term_premium[:] = [x - cma.val_dict['em_theme_tp_adjust'] for x in em_term_premium]
em_term_premium[0] = 0

# +
# Import Treasury Information
em_future_yield = (cma.val_dict['em_inflation']/100 + cma.val_dict['em_rcr']/100)

em_future_yield_list = [em_future_yield, (em_future_yield + em_term_premium[1]), (em_future_yield + em_term_premium[2]),
                       (em_future_yield + em_term_premium[3]), (em_future_yield + em_term_premium[4]), (em_future_yield + em_term_premium[5])]
em_future_duration_list = em_current_duration_list

em_interest_rates = {'Current_Yield':em_current_yield_list,
                     'Current_Duration':em_current_duration_list,
                     'Term_Premium': em_term_premium,
                     'Future_Yield':em_future_yield_list,
                     'Future_Duration':em_future_duration_list}

df_em_interest_rates = pd.DataFrame(em_interest_rates)
df_em_interest_rates = df_em_interest_rates.rename(index = {0: "3 Mo LIBOR",
                                                            1: "1-3 Yr",
                                                            2: "3-5 Yr",
                                                            3: "5-7 Yr",
                                                            4: "7-10 Yr",
                                                            5: "10+ Yr"})

# +
# Current Curve Parameters
t = np.array(df_em_interest_rates['Current_Duration'])
y = np.array(df_em_interest_rates['Current_Yield'])

curve, status = betas_ns_ols(tau, t, y)
curve = str(curve)

# Extract paramaters from results
B0_em_curr = float((curve.split('=')[1]).split(',')[0])
B1_em_curr = float((curve.split('=')[2]).split(',')[0])
B2_em_curr = float((curve.split('=')[3]).split(',')[0])
param_em_curr = [B0_em_curr, B1_em_curr, B2_em_curr]

# +
# Future Curve Parameters
t = np.array(df_em_interest_rates['Future_Duration'])
y = np.array(df_em_interest_rates['Future_Yield'])

curve, status = betas_ns_ols(tau, t, y)
curve = str(curve)

# Extract paramaters from results
B0_em_future = float((curve.split('=')[1]).split(',')[0])
B1_em_future = float((curve.split('=')[2]).split(',')[0])
B2_em_future = float((curve.split('=')[3]).split(',')[0])
param_em_future = [B0_em_future, B1_em_future, B2_em_future]
# -

# Yield Curves Next 10 Yrs
em_term_structure = (np.arange(0.5, 100.5, 0.5))

# +
em_curr_yield = [B0_em_curr + B1_em_curr * (tau / x) * (1 - math.exp(-x / tau)) + B2_em_curr * (tau / x) * (1 - (1 + x / tau) * math.exp(-x / tau)) for x in em_term_structure]

# Create shell dataframe
df_em_yield_curves = pd.DataFrame(df_us_yield_curves.iloc[:,0])
for i in range(1,11):
    df_em_yield_curves[i] = np.nan
df_em_yield_curves.iloc[:,0] = em_curr_yield

# Normalized Values
for i in range(cma.val_dict['em_yield_norm_yrs'], 11):
     df_em_yield_curves.iloc[:,i] = [B0_em_future + B1_em_future * (tau / x) * (1 - math.exp(-x / tau)) + B2_em_future * (tau / x) * (1 - (1 + x / tau) * math.exp(-x / tau)) for x in em_term_structure]

# Path to reach normalized yield state
for i in range(1, cma.val_dict['em_yield_norm_yrs']):
     df_em_yield_curves.iloc[:, i] = (df_em_yield_curves.iloc[:,cma.val_dict['em_yield_norm_yrs']] - 
                                      df_em_yield_curves.iloc[:,0]) / cma.val_dict['em_yield_norm_yrs'] + df_em_yield_curves.iloc[:,i-1]

df_em_yield_curves['Term Structure'] = em_term_structure
# -

# # USD Returns

# ## Import Data

# +
df_yield = pd.read_excel('P:\\Advisory\\Research\\Automation\\CMAs\\Data\\bloomberg_data_usd.xlsx', sheet_name='fixed_yields', index_col=0) / 100
df_duration = pd.read_excel('P:\\Advisory\\Research\\Automation\\CMAs\\Data\\bloomberg_data_usd.xlsx', sheet_name='fixed_durations', index_col=0)
df_spread = pd.read_excel('P:\\Advisory\\Research\\Automation\\CMAs\\Data\\bloomberg_data_usd.xlsx', sheet_name='fixed_spreads', index_col=0) /100

# Filter dataframes to only include 20 years of data
df_yields = df_yield.loc[:cma.val_dict['as_of_date'], :]
df_duration = df_duration.loc[:cma.val_dict['as_of_date'], :]
df_spread = df_spread.loc[:cma.val_dict['as_of_date'], :]
# -















# # Non USD Returns

# ## Import Data

# +
df_yield_nonus = pd.read_excel('P:\\Advisory\\Research\\Automation\\CMAs\\Data\\bloomberg_data_nonus.xlsx', sheet_name='fixed_yields', index_col=0) / 100
df_duration_nonus = pd.read_excel('P:\\Advisory\\Research\\Automation\\CMAs\\Data\\bloomberg_data_nonus.xlsx', sheet_name='fixed_durations', index_col=0)
df_spread_nonus = pd.read_excel('P:\\Advisory\\Research\\Automation\\CMAs\\Data\\bloomberg_data_nonus.xlsx', sheet_name='fixed_spreads', index_col=0) /100

# Filter dataframes to only include 20 years of data
df_yield_nonus = df_yield_nonus.loc[:cma.val_dict['as_of_date'], :]
df_duration_nonus = df_duration_nonus.loc[:cma.val_dict['as_of_date'], :]
df_spread_nonus = df_spread_nonus.loc[:cma.val_dict['as_of_date'], :]

# +
# Add TBills to synopsis for calculation purposes
df_yield_nonus['U.S. Treasury Bills'] = df_yield['U.S. Treasury Bills']
df_duration_nonus['U.S. Treasury Bills'] = df_duration['U.S. Treasury Bills']
df_spread_nonus['U.S. Treasury Bills'] = df_spread['U.S. Treasury Bills']

# Synopsis of current yield, spreads, and duration for all asset classes
df_yield_last_nonus = pd.DataFrame(df_yield_nonus.iloc[-1,:]).T
df_yield_last_nonus = df_yield_last_nonus.rename({240: 'Current Yield'})

df_spread_last_nonus = pd.DataFrame(df_spread_nonus.iloc[-1,:]).T
df_spread_last_nonus = df_spread_last_nonus.rename({240: 'Current Spread'})

df_duration_last_nonus = pd.DataFrame(df_duration_nonus.iloc[-1,:]).T
df_duration_last_nonus = df_duration_last_nonus.rename({240: 'Current Duration'})

df_synopsis_nonus = pd.concat([df_yield_last_nonus, df_spread_last_nonus, df_duration_last_nonus], sort=False)
df_synopsis_nonus = df_synopsis_nonus.astype(float)
df_synopsis_nonus.index = ['Current Yield', 'Current Spread', 'Current Duration']
df_synopsis_nonus.loc['Current Duration', 'U.S. Treasury Bills'] = 0.25
df_synopsis_nonus = df_synopsis_nonus.round(4)
# -

# ## Future Treasury Yields

# +
duration_list_nonus = df_synopsis_nonus.loc['Current Duration',:]

df_name_nonus = {k:v for (k,v) in cma.val_dict.items() if 'fixed_nonus_name' in k}
df_name_nonus = [i for i in df_name_nonus.values()]

df_term_nonus = {k:v for (k,v) in cma.val_dict.items() if 'fixed_nonus_term' in k}
df_term_nonus = [i for i in df_term_nonus.values()]

# Create dataframe to determine what asset classes to what term structure
df_term_combined_nonus = pd.DataFrame(zip(df_name_nonus, df_term_nonus), columns =['Asset Class', 'Term Structure']).set_index('Asset Class')
df_term_combined_nonus = df_term_combined_nonus.merge(duration_list_nonus, left_index=True, right_index=True)

# Split dataframes based on term structure
df_term_us_nonus = df_term_combined_nonus[df_term_combined_nonus['Term Structure'] == 'US']
df_term_gl_nonus = df_term_combined_nonus[df_term_combined_nonus['Term Structure'] == 'NonUS']
df_term_em_nonus = df_term_combined_nonus[df_term_combined_nonus['Term Structure'] == 'EM']

# +
# US Term structure yield determination
duration_list_us_nonus = df_term_us_nonus.loc[:,'Current Duration']
iteration_list_us_nonus = [abs(df_us_yield_curves['Term Structure'] - x).idxmin() for x in duration_list_us_nonus]

tsy_yield_us_nonus = pd.DataFrame(index=range(1,11), columns=df_term_us_nonus.index)

for i in range(1, 11):
     tsy_yield_us_nonus.loc[i,:] = [df_us_yield_curves.iloc[x, i] for x in iteration_list_us_nonus]

# +
# Non-US Term structure yield determination
duration_list_gl_nonus = df_term_gl_nonus.loc[:,'Current Duration']
iteration_list_gl_nonus = [abs(df_gl_yield_curves['Term Structure'] - x).idxmin() for x in duration_list_gl_nonus]

tsy_yield_gl_nonus = pd.DataFrame(index=range(1,11), columns=df_term_gl_nonus.index)

for i in range(1, 11):
     tsy_yield_gl_nonus.loc[i,:] = [df_gl_yield_curves.iloc[x, i] for x in iteration_list_gl_nonus]

# +
# EM Term structure yield determination
duration_list_em_nonus = df_term_em_nonus.loc[:,'Current Duration']
iteration_list_em_nonus = [abs(df_em_yield_curves['Term Structure'] - x).idxmin() for x in duration_list_em_nonus]

tsy_yield_em_nonus = pd.DataFrame(index=range(1,11), columns=df_term_em_nonus.index)

for i in range(1, 11):
     tsy_yield_em_nonus.loc[i,:] = [df_em_yield_curves.iloc[x, i] for x in iteration_list_em_nonus]

# +
# Combine 3 structure dataframes
df_fixed_order_nonus = df_synopsis_nonus.columns.tolist()

future_treasury_yields_nonus = pd.concat([tsy_yield_us_nonus, tsy_yield_gl_nonus, tsy_yield_em_nonus], axis=1)
future_treasury_yields_nonus = future_treasury_yields_nonus.reindex(columns=df_fixed_order_nonus)
# -

# ## Future Spreads

# +
# create base dataframe with current spreads
future_spreads_nonus = pd.DataFrame(df_synopsis_nonus.loc['Current Spread',:])
future_spreads_nonus = future_spreads_nonus.T

for i in range(1,11):
    future_spreads_nonus[i] = np.nan
    
future_spreads_nonus = future_spreads_nonus.reindex(columns=df_fixed_order_nonus)

# +
# Winsorize spread norm
spread_norm_nonus = []
for i in range(len(df_spread_nonus.columns)):
    list = mstats.winsorize(df_spread_nonus.iloc[:,i].dropna(), limits=[0.05, 0.05], inclusive=[False, False])

    def Average(lst): 
        return sum(lst) / len(lst) 
    spread_norm_nonus.append(Average(list))
    
spread_norm_nonus = pd.Series(spread_norm_nonus)
spread_norm_nonus.index = df_spread_nonus.columns

# +
# Create shell dataframe
for i in range(1, 11):
    future_spreads_nonus.loc[i] = np.nan

# Calculate normalized spread path
for i in range(cma.val_dict['spread_norm_yrs'], 11):
    future_spreads_nonus.iloc[i,:] = spread_norm_nonus

# Populate data for years leading up to normalization
for i in range(1, cma.val_dict['spread_norm_yrs']):
    future_spreads_nonus.iloc[i,:] = (future_spreads_nonus.iloc[cma.val_dict['spread_norm_yrs'],:] - future_spreads_nonus.iloc[0,:]) / cma.val_dict['spread_norm_yrs'] + future_spreads_nonus.iloc[i-1,:]

# -

# ## Yield Forecast

# +
future_yields_nonus = pd.DataFrame(df_synopsis_nonus.loc['Current Yield',:])

future_yields_nonus = future_yields_nonus.T
#future_yields_nonus = future_yields.reindex(columns=df_fixed_order)

for i in range(1, 11):
    future_yields_nonus.loc[i,:] = future_treasury_yields_nonus.loc[i,:] + future_spreads_nonus.loc[i,:]
# -

# ## Duration Forecast

# +
future_duration_nonus = pd.DataFrame(df_synopsis_nonus.loc['Current Duration',:])
future_duration_nonus = future_duration_nonus.T
future_duration_nonus = future_duration_nonus.reindex(columns=df_fixed_order_nonus)

for i in range(1, 11):
     future_duration_nonus.loc[i,:] = df_synopsis_nonus.loc['Current Duration',:]
# -

# ## Annual Return

# +
# Default Rates
df_default_nonus = []
for key, item in cma.val_dict.items():
    if 'fixed_nonus_default' in key:
        df_default_nonus.append(item)
df_default_nonus = [item for item in df_default_nonus if item != '']
df_default_nonus = [x / 100 for x in df_default_nonus]

# Recovery Rates
df_recovery_nonus = []
for key, item in cma.val_dict.items():
    if 'fixed_nonus_recover' in key:
        df_recovery_nonus.append(item)
df_recovery_nonus = [item for item in df_recovery_nonus if item != '']
df_recovery_nonus = [x / 100 for x in df_recovery_nonus]
df_recovery_nonus = [1 - x for x in df_recovery_nonus]

default_impact_nonus = [a*b for a,b in zip(df_default_nonus, df_recovery_nonus)]

# +
annual_returns_nonus = pd.DataFrame(df_synopsis_nonus.loc['Current Yield',:])
annual_returns_nonus = annual_returns_nonus.T

for i in range(1, 11):
      annual_returns_nonus.loc[i,:] = future_yields_nonus.iloc[i-1,:] - (future_yields_nonus.iloc[i,:] - future_yields_nonus.iloc[i-1,:]) * future_duration_nonus.iloc[i-1,:]\
        +100 *(future_yields_nonus.iloc[i,:] - future_yields_nonus.iloc[i-1,:]) **2 

annual_returns_nonus = annual_returns_nonus.iloc[1:,:-1]

# Adjust for default and recovery rates
for i in range(len(annual_returns_nonus.columns)):
    annual_returns_nonus.iloc[:,i] = annual_returns_nonus.iloc[:,i] - default_impact_nonus[i]
# -

# Expected return 
expected_returns_fixed_nonus = ((annual_returns_nonus + 1).product(axis=0)**(1/10)-1)

# ## Income Return

# +
avg_yield_nonus = future_yields_nonus.mean()

diff = [first * second for first, second in zip(df_default_nonus, df_recovery_nonus)]
income_return_nonus = [first - second for first, second in zip(avg_yield_nonus, diff)]
df_income_return_nonus = pd.DataFrame(income_return_nonus)

# Create dataframe of info

df_income_return_nonus.index =  annual_returns_nonus.columns
df_income_return_nonus = df_income_return_nonus.rename(columns={0: "Avg Yield"})

df_income_return_nonus['Term Structure'] = df_term_combined_nonus['Term Structure']
df_income_return_nonus['Expected Return'] = expected_returns_fixed_nonus
# -
# ## Final Return


# +
# Split dataframes based on term structure
df_return_us_nonus = df_income_return_nonus[df_income_return_nonus['Term Structure'] == 'US'].loc[:,'Expected Return']
df_return_gl_nonus = df_income_return_nonus[df_income_return_nonus['Term Structure'] == 'NonUS'].loc[:,'Expected Return']
df_return_em_nonus = df_income_return_nonus[df_income_return_nonus['Term Structure'] == 'EM'].loc[:,'Expected Return']

# US based inflation
final_return_us_nonus = df_return_us_nonus + cma.val_dict['country_inflation']/100 - cma.val_dict['us_inflation']/100

# Global based inflation
final_return_gl_nonus = df_return_gl_nonus + cma.val_dict['country_inflation']/100 - cma.val_dict['global_inflation']/100

# EM based inflation
final_return_em_nonus = df_return_em_nonus + cma.val_dict['country_inflation']/100 - cma.val_dict['em_inflation']/100

# Combine all values
final_return_fixed_income_nonus = final_return_gl_nonus.append(final_return_us_nonus).append(final_return_em_nonus).rename('Adjusted Final Return') 
# -

df_fixed_income_nonus_final = df_income_return_nonus.merge(final_return_fixed_income_nonus, left_index=True, right_index=True)


