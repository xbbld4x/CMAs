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
import backfill_calc
import cma_gui as cma
import math
import numpy as np
import operator
import pandas as pd

from nelson_siegel_svensson.calibrate import betas_ns_ols
from scipy.stats import mstats


# -

# # Functions

# ## Term Structure Functions

def rate_norm(current_yield, norm_years, future_yield):
    """Determine future normalized rates"""
    df_yield_10yr = pd.DataFrame(current_yield)
    
    for i in range(1,11):
        df_yield_10yr[i] = np.nan

    # Normalized values
    for i in range(norm_years, 11):
         df_yield_10yr.iloc[:,i] = future_yield
    
    # Path to reach normalized yield state
    for i in range(1, norm_years):
        df_yield_10yr.iloc[:, i] = [(x - y) /norm_years for x, y in zip(future_yield, current_yield)] + df_yield_10yr.iloc[:,i-1]
    
    return df_yield_10yr


def curve_params(current_duration, yield_path):
    
    """Calculate parameters for all 10 years"""
    df_yield_params = pd.DataFrame(['NaN', 'NaN', 'NaN'], columns=['Current'])

    for i in range(1,11):
        df_yield_params[i] = np.nan

    tau=1.65

    param_list = []
    for i in range(0, 11):
        t = np.array(current_duration)
        y = np.array(yield_path.iloc[:,i])

        curve, status = betas_ns_ols(tau, t, y)
        curve = str(curve)

        B0 = float((curve.split('=')[1]).split(',')[0])
        B1 = float((curve.split('=')[2]).split(',')[0])
        B2 = float((curve.split('=')[3]).split(',')[0])
        param = [B0, B1, B2]
        df_yield_params.iloc[:,i] = param
        
    return df_yield_params


def curve_final(yield_params):
    
    """Calculate final 10 year curves"""
    tau=1.65
    
    # Yield Curve Over Next 10 Years
    term_structure = (np.arange(0.5, 100.5, 0.5))

    curve_list = []
    for i in range(0, 11):
        curve_item = [yield_params.iloc[0,i] + yield_params.iloc[1,i] * (tau / x) * (1 - math.exp(-x / tau)) + yield_params.iloc[2,i] * (tau / x) * (1 - (1 + x / tau) * math.exp(-x / tau)) for x in term_structure]
        curve_list.append(curve_item)

    df_yield_curves = pd.DataFrame(curve_list).T
    df_yield_curves['Term Structure'] = term_structure
    return df_yield_curves


# ## Fixed Income Return Functions

def term_assignment(suffix):
    
    asset_name = {k:v for (k,v) in cma.val_dict.items() if 'fixed_' + suffix + '_name' in k}
    asset_name = [i for i in asset_name.values()]
    
    asset_term = {k:v for (k,v) in cma.val_dict.items() if 'fixed_' + suffix + '_term' in k}
    asset_term = [i for i in asset_term.values()]
    
    asset_dict = dict(zip(asset_name, asset_term))
    
    return asset_dict


def future_tsy_ylds(term_struc, term_dict, term_suffix, duration_suffix):
    
    term = {k:v for (k,v) in term_dict.items() if v==term_struc}
    durations = eval('duration_' + duration_suffix).filter(items = term).tolist()
    
    iteration_list = [abs(eval('df_yield_curves_' + term_suffix)['Term Structure'] - x).idxmin() for x in durations]
    future_tsy_yld = pd.DataFrame(index=range(0,10), columns=term.keys())
    
    for i in range(1, 11):
        future_tsy_yld.loc[i-1,:] = [eval('df_yield_curves_' + term_suffix).iloc[x, i] for x in iteration_list]
    
    return future_tsy_yld


def future_spreads(spread_current, spread_history):
    
    norm_reference = cma.val_dict['spread_norm_yrs']
    
    future_spreads = pd.DataFrame(spread_current).T
    future_spreads = future_spreads.reset_index(drop=True)
    
    # Winsorize spread norm
    spread_norm = []
    for i in range(len(spread_history.columns)):
        list = mstats.winsorize(spread_history.iloc[:,i].dropna(), limits=[0.05, 0.05], inclusive=[True, True])

        def Average(lst): 
            return sum(lst) / len(lst) 
        spread_norm.append(Average(list))
    
    # Create shell dataframe
    for i in range(1,11):
        future_spreads.loc[i] = np.nan
    
    # Calculate normalized spread path
    for i in range(norm_reference, 11):
        future_spreads.iloc[i,:] = spread_norm
    
    # Populate data for years leading up to normalization
    for i in range(1, norm_reference):
        future_spreads.iloc[i,:] = (future_spreads.iloc[norm_reference,:] - future_spreads.iloc[0,:]) / norm_reference + future_spreads.iloc[i-1,:]
    
    return future_spreads


def future_ylds(current_yields, suffix):
    
    future_ylds = pd.DataFrame(current_yields).T
    future_ylds = future_ylds.reset_index(drop=True)
    
    for i in range(1, 11):
        future_ylds.loc[i,:] = eval('future_tsy_ylds_' + suffix).loc[i-1,:] + eval('future_spreads_' + suffix).loc[i,:]
    
    return future_ylds


def future_duration(current_duration, suffix):
    future_duration = pd.DataFrame(current_duration).T
    future_duration = future_duration.reset_index(drop=True)

    for i in range(0, 10):
        future_duration.loc[i,:] = current_duration
    
    return future_duration


def default_recovery(suffix):
    default_name = {k:v for (k,v) in cma.val_dict.items() if 'fixed_' + suffix + '_name' in k}
    default_name = [i for i in default_name.values() if i != '']
    
    default_rate = {k:v for (k,v) in cma.val_dict.items() if 'fixed_' + suffix + '_default' in k}
    default_rate = [0 if i=='N/A' else i for i in default_rate.values()]
    default_rate = [i/100 for i in default_rate if i != '']
    
    recovery_rate = {k:v for (k,v) in cma.val_dict.items() if 'fixed_' + suffix + '_recover' in k}
    recovery_rate = [0 if i=='N/A' else i for i in recovery_rate.values()]
    recovery_rate = [i/100 for i in recovery_rate if i != '']
    
    impact_rate = [a*(1-b) for a,b in zip(default_rate, recovery_rate)]
    
    return impact_rate


def annual_returns(current_yields, future_yields, future_durations, default_impact):
    annual_returns = pd.DataFrame(current_yields).T
    annual_returns = annual_returns.reset_index(drop=True).iloc[1:,:]
    
    for i in range(0, 10):
        annual_returns.loc[i,:] = future_yields.iloc[i,:] - (future_yields.iloc[i+1,:] - future_yields.iloc[i,:]) * future_durations.iloc[i,:]\
            +100 *(future_yields.iloc[i+1,:] - future_yields.iloc[i,:]) **2
        
    # Adjust for default and recovery rates
    for i in range(len(annual_returns.columns)):
        annual_returns.iloc[:,i] = annual_returns.iloc[:,i] - default_impact[i]
    
    return annual_returns


# # MAIN VARIABLES

# +
first_date = backfill_calc.first_date
last_date = backfill_calc.last_date

term_file = r'P:\\Advisory\\Research\\Automation\\CMAs\\Data\\term_structure_data.xlsx'
# -

# # TERM STRUCTURES

# ## US TERM STRUCTURE

# +
# Read in data as of last date and convert to list, 
current_yield_us = (pd.read_excel(term_file, sheet_name='us_treas_yld', index_col=0).loc[last_date,:] / 100).to_list()
current_duration_us = (pd.read_excel(term_file, sheet_name='us_treas_dur', index_col=0).loc[last_date,:]).to_list()

# Term premium
term_premium_us = [cma.val_dict['term_prem_3mo'], cma.val_dict['term_prem_5yr']/100, cma.val_dict['term_prem_10yr']/100, cma.val_dict['term_prem_30yr']/100]

# Establish future yields and duration
future_yield_base_us = (cma.val_dict['us_inflation']/100 + cma.val_dict['us_rcr']/100)
future_yield_us = [future_yield_base_us, (future_yield_base_us + cma.val_dict['term_prem_5yr']/100), (future_yield_base_us + cma.val_dict['term_prem_10yr']/100), 
                   (future_yield_base_us + cma.val_dict['term_prem_30yr']/100)]

future_duration_us = current_duration_us
# -

df_yield_10yr_us = rate_norm(current_yield_us, cma.val_dict['yield_norm_yrs'], future_yield_us)
df_yield_params_us = curve_params(current_duration_us, df_yield_10yr_us)
df_yield_curves_us = curve_final(df_yield_params_us)

# ## GLOBAL TERM STRUCTURE

# +
# Read in data as of last date and convert to list, 
current_yield_gl = (pd.read_excel(term_file, sheet_name='gl_treas_yld', index_col=0).loc[last_date,:] / 100).to_list()
current_yield_gl.insert(0, 0.010)

current_duration_gl = (pd.read_excel(term_file, sheet_name='gl_treas_dur', index_col=0).loc[last_date,:]).to_list()
current_duration_gl.insert(0, 0.25)

# Term premium
iteration_list_gl_tp = [abs(df_yield_curves_us['Term Structure'] - x).idxmin() for x in current_duration_gl]

for i in range(6):
      gl_term_premium = [df_yield_curves_us.iloc[x, i] - future_yield_base_us for x in iteration_list_gl_tp]
gl_term_premium[:] = [x - cma.val_dict['gl_theme_tp_adjust'] for x in gl_term_premium]
gl_term_premium[0] = 0

# Establish future yields and duration
future_yield_base_gl = (cma.val_dict['gl_inflation']/100 + cma.val_dict['gl_rcr']/100)
future_yield_gl = [future_yield_base_gl, (future_yield_base_gl + gl_term_premium[1]), (future_yield_base_gl + gl_term_premium[2]),
                       (future_yield_base_gl + gl_term_premium[3]), (future_yield_base_gl + gl_term_premium[4]), (future_yield_base_gl + gl_term_premium[5])]

future_duration_gl = current_duration_gl
# -

df_yield_10yr_gl = rate_norm(current_yield_gl, cma.val_dict['gl_yield_norm_yrs'], future_yield_gl)
df_yield_params_gl = curve_params(current_duration_gl, df_yield_10yr_gl)
df_yield_curves_gl = curve_final(df_yield_params_gl)

# ## GLOBAL EX-US TERM STRUCTURE

# +
# Read in data as of last date and convert to list, 
current_yield_gl_agg = (pd.read_excel(term_file, sheet_name='gl_agg_yld', index_col=0).loc[last_date,:] / 100).to_list()
current_yield_gl_agg.insert(0, 0)

current_spread_gl_agg = (pd.read_excel(term_file, sheet_name='gl_agg_spreads', index_col=0).loc[last_date,:] / 100).to_list()
current_spread_gl_agg.insert(0, 0)

# Current yield calculated as agg yield minus spread
current_yield_gl_exus = list(map(operator.sub, current_yield_gl_agg, current_spread_gl_agg))

current_duration_gl_exus = (pd.read_excel(term_file, sheet_name='gl_agg_dur', index_col=0).loc[last_date,:]).to_list()
current_duration_gl_exus.insert(0, 0.25)

# Term premium
iteration_list_gl_exus_tp = [abs(df_yield_curves_us['Term Structure'] - x).idxmin() for x in current_duration_gl_exus]

for i in range(6):
    gl_exus_term_premium = [df_yield_curves_us.iloc[x, i] - future_yield_base_us for x in iteration_list_gl_exus_tp]
    gl_exus_term_premium[:] = [x - cma.val_dict['gl_exus_theme_tp_adjust']/100 for x in gl_exus_term_premium]
    gl_exus_term_premium[0] = 0
    
# Establish future yields and duration
future_yield_base_gl_exus = (cma.val_dict['gl_exus_inflation']/100 + cma.val_dict['gl_exus_rcr']/100)
future_yield_gl_exus = [future_yield_base_gl_exus, (future_yield_base_gl_exus + gl_exus_term_premium[1]), (future_yield_base_gl_exus + gl_exus_term_premium[2]),
                       (future_yield_base_gl_exus + gl_exus_term_premium[3]), (future_yield_base_gl_exus + gl_exus_term_premium[4]), (future_yield_base_gl_exus + gl_exus_term_premium[5])]

future_duration_gl_exus = current_duration_gl_exus
# -

df_yield_10yr_gl_exus = rate_norm(current_yield_gl_exus, cma.val_dict['gl_yield_norm_yrs'], future_yield_gl_exus)
df_yield_params_gl_exus = curve_params(current_duration_gl_exus, df_yield_10yr_gl_exus)
df_yield_curves_gl_exus = curve_final(df_yield_params_gl_exus)

# ## EM TERM STRUCTURE

# +
# Read in data as of last date and convert to list, 
current_yield_em = (pd.read_excel(term_file, sheet_name='em_treas_yld', index_col=0).loc[last_date,:] / 100).to_list()
current_yield_em.insert(0, 0.045)

current_duration_em = (pd.read_excel(term_file, sheet_name='em_treas_dur', index_col=0).loc[last_date,:]).to_list()
current_duration_em.insert(0, 0.25)

# Term premium
iteration_list_em_tp = [abs(df_yield_curves_us['Term Structure'] - x).idxmin() for x in current_duration_em]

for i in range(6):
      em_term_premium = [df_yield_curves_us.iloc[x, i] - future_yield_base_us for x in iteration_list_em_tp]
em_term_premium[:] = [x - cma.val_dict['em_theme_tp_adjust'] for x in em_term_premium]
em_term_premium[0] = 0

# Establish future yields and duration
future_yield_base_em = (cma.val_dict['em_inflation']/100 + cma.val_dict['em_rcr']/100)
future_yield_em = [future_yield_base_em, (future_yield_base_em + em_term_premium[1]), (future_yield_base_em + em_term_premium[2]),
                       (future_yield_base_em + em_term_premium[3]), (future_yield_base_em + em_term_premium[4]), (future_yield_base_em + em_term_premium[5])]

future_duration_em = current_duration_em
# -

df_yield_10yr_em = rate_norm(current_yield_em, cma.val_dict['em_yield_norm_yrs'], future_yield_em)
df_yield_params_em = curve_params(current_duration_em, df_yield_10yr_em)
df_yield_curves_em = curve_final(df_yield_params_em)

# # CMA RETURNS

# ## US CMAs

# +
# Import Current Data
us_fixed_file = r'P:\\Advisory\\Research\\Automation\\CMAs\\Data\\bloomberg_data_us.xlsx'

# Establish name orders
asset_order = {k:v for (k,v) in cma.val_dict.items() if 'fixed_us_name' in k}
asset_order = [i for i in asset_order.values()if i !='']

yield_us = (pd.read_excel(us_fixed_file, sheet_name='fixed_yields', index_col=0).loc[last_date,:] / 100).reindex(index=asset_order)
duration_us = (pd.read_excel(us_fixed_file, sheet_name='fixed_durations', index_col=0).loc[last_date,:]).reindex(index=asset_order)

spread_us = (pd.read_excel(us_fixed_file, sheet_name='fixed_spreads', index_col=0).loc[last_date,:] / 100).reindex(index=asset_order)
spread_us['U.S. TIPS'] = -0.0205
spread_us['U.S. Short Municipal'] = -0.0020
spread_us_history = (pd.read_excel(us_fixed_file, sheet_name='fixed_spreads', index_col=0).loc[first_date:last_date,:] / 100).reindex(columns=asset_order)
# -

term_assign_us = term_assignment('us')

# +
# Future Treasury Yields
fixed_us_usterm = future_tsy_ylds('US', term_assign_us, 'us', 'us')
fixed_us_nonusterm = future_tsy_ylds('NonUS', term_assign_us, 'gl_exus', 'us')
fixed_us_emterm = future_tsy_ylds('EM', term_assign_us, 'em', 'us')

future_tsy_ylds_us = pd.concat([fixed_us_usterm, fixed_us_nonusterm, fixed_us_emterm], axis=1)
future_tsy_ylds_us = future_tsy_ylds_us.reindex(columns=asset_order)

# +
# Future Spreads
norm_reference = cma.val_dict['spread_norm_yrs']
 
future_spreads_us = pd.DataFrame(future_tsy_ylds_us)
future_spreads_us = future_spreads_us.reset_index(drop=True)
future_spreads_us.iloc[0,:] = spread_us

# Winsorize spread norm
spread_norm = []
for i in range(len(future_tsy_ylds_us.columns)):
    list = mstats.winsorize(spread_us_history.iloc[:,i].dropna(), limits=[0.05, 0.05], inclusive=[True, True])

    def Average(lst): 
        return sum(lst) / len(lst) 
    spread_norm.append(Average(list))
    
spread_norm = pd.DataFrame(zip(future_tsy_ylds_us.columns, spread_norm), columns=['Asset Class', 'Spread']).set_index('Asset Class')

# Modifications for specific asset classes
spread_norm_tips = -cma.val_dict['us_inflation']/100

spread_norm_int_muni = (0.9 * future_tsy_ylds_us.loc[9, 'U.S. Intermediate Municipal'] \
                          - future_tsy_ylds_us.loc[9, 'U.S. Intermediate Municipal']) + 0.005
spread_norm_short_muni = (0.9 * future_tsy_ylds_us.loc[9, 'U.S. Short Municipal'] \
                           - future_tsy_ylds_us.loc[9, 'U.S. Short Municipal']) + 0.003

spread_norm.loc['U.S. Intermediate Municipal',:] = spread_norm_int_muni
spread_norm.loc['U.S. Short Municipal',:] = spread_norm_short_muni
spread_norm.loc['U.S. TIPS',:] = spread_norm_tips
spread_norm = spread_norm['Spread'].tolist()

# Create shell dataframe
for i in range(1,11):
    future_spreads_us.loc[i] = np.nan

# Calculate normalized spread path
for i in range(norm_reference, 11):
    future_spreads_us.iloc[i,:] = spread_norm

# Populate data for years leading up to normalization
for i in range(1, norm_reference):
    future_spreads_us.iloc[i,:] = (future_spreads_us.iloc[norm_reference,:] - future_spreads_us.iloc[0,:]) / norm_reference + future_spreads_us.iloc[i-1,:]
    
future_spreads_us = future_spreads_us.reindex(columns=asset_order)
# -


# Yield Forecast
future_ylds_us = future_ylds(yield_us, 'us')

# Duration Forecast
future_duration_us = future_duration(duration_us, 'us')

# Defaults/Recovery
impact_us = default_recovery('us')

# +
# Annual Return Forecast
annual_returns_us = annual_returns(yield_us, future_ylds_us, future_duration_us, impact_us)

annual_returns_us['U.S. TIPS'] += cma.val_dict['us_inflation']/100 
# -

# Expected Return
expected_return_fixed_us = ((annual_returns_us + 1).product(axis=0)**(1/10)-1)


# ## NON-US CMAs

# +
# Import Current Data
nonus_fixed_file = r'P:\\Advisory\\Research\\Automation\\CMAs\\Data\\bloomberg_data_nonus.xlsx'

yield_nonus = pd.read_excel(nonus_fixed_file, sheet_name='fixed_yields', index_col=0).loc[last_date,:] / 100
duration_nonus = pd.read_excel(nonus_fixed_file, sheet_name='fixed_durations', index_col=0).loc[last_date,:]
spread_nonus = pd.read_excel(nonus_fixed_file, sheet_name='fixed_spreads', index_col=0).loc[last_date,:] / 100

spread_nonus_history = pd.read_excel(nonus_fixed_file, sheet_name='fixed_spreads', index_col=0).loc[first_date:last_date,:] / 100

# +
term_assign_nonus = term_assignment('nonus')

# Future Treasury Yields
fixed_nonus_usterm = future_tsy_ylds('US', term_assign_nonus, 'us', 'nonus')
fixed_nonus_nonusterm = future_tsy_ylds('NonUS', term_assign_nonus, 'gl', 'nonus')
fixed_nonus_emterm = future_tsy_ylds('EM', term_assign_nonus, 'em', 'nonus')

# Combine 3 term structure dataframes
fixed_order_nonus = spread_nonus_history.columns.tolist()
future_tsy_ylds_nonus = pd.concat([fixed_nonus_usterm, fixed_nonus_nonusterm, fixed_nonus_emterm], axis=1)
future_tsy_ylds_nonus = future_tsy_ylds_nonus.reindex(columns=fixed_order_nonus)
# -
# Future Spreads
future_spreads_nonus = future_spreads(spread_nonus, spread_nonus_history)

# Yield Forecast
future_ylds_nonus = future_ylds(yield_nonus, 'nonus')

# Duration Forecast
future_duration_nonus = future_duration(duration_nonus, 'nonus')

# Defaults/Recovery
impact_nonus = default_recovery('nonus')

# Annual Return Forecast
annual_returns_nonus = annual_returns(yield_nonus, future_ylds_nonus, future_duration_nonus, impact_nonus)

# +
# Expected Return
expected_return_fixed_nonus = ((annual_returns_nonus + 1).product(axis=0)**(1/10)-1)

# Income Return
income_return_nonus = future_ylds_nonus.mean() - impact_nonus

# Final Return (Inflation_Adjusting)
us_term = {k:v for (k,v) in term_assign_nonus.items() if v=='US'}
us_term = [i for i in us_term.keys()]

gl_term = {k:v for (k,v) in term_assign_nonus.items() if v=='NonUS'}
gl_term = [i for i in gl_term.keys()]

em_term = {k:v for (k,v) in term_assign_nonus.items() if v=='EM'}
em_term = [i for i in em_term.keys()]

expected_return_fixed_nonus.loc[us_term] = expected_return_fixed_nonus.loc[us_term] + cma.val_dict['country_inflation']/100 - cma.val_dict['us_inflation']/100
expected_return_fixed_nonus.loc[gl_term] = expected_return_fixed_nonus.loc[gl_term] + cma.val_dict['country_inflation']/100 - cma.val_dict['gl_inflation']/100
expected_return_fixed_nonus.loc[em_term] = expected_return_fixed_nonus.loc[em_term] + cma.val_dict['country_inflation']/100 - cma.val_dict['em_inflation']/100
# -
expected_return_fixed_nonus



