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
from datetime import datetime
from datetime import date
from dateutil.relativedelta import relativedelta
from dateutil.rrule import rrule, MONTHLY
import numpy as np
import pandas as pd
import PySimpleGUI as sg

# %% [markdown]
# # Variables

# %%
currencies = ['AUD', 'CAD', 'CHF','DKK', 'EUR', 'GBP', 'JPY', 'NOK', 'NZD', 'SEK', 'USD']

value_range = [float(f'{i:.2f}') for i in list(np.arange(-5.0, 5.1, 0.05))]
value_range.insert(0, 0.0)

default_val = ['', 'N/A'] + [float(f'{i:.2f}') for i in list(np.arange(0.01, 5.0, 0.01))]

recovery_val = ['', 'N/A'] + [float(f'{i:.1f}') for i in list(np.arange(0, 105, 5))]

ir_val = ['', 'N/A'] + [float(f'{i:.2f}') for i in list(np.arange(0, 1.01, 0.01))]

# %%
end_date = date(date.today().year, date.today().month, 1) - relativedelta(days=1)
start_date = end_date - relativedelta(years=1)

as_of_date = pd.date_range(start_date, end_date, freq='M').strftime('%m-%d-%Y').tolist()

# %% [markdown]
# # Equity Data

# %%
beta_equity = ['', 'Building Blocks', 'Europe Ex-UK Equity', 'International Developed Equity', 'Japan Equity', 'U.S. Equity']

equity_us_base = {
    'Asset Class': 
        ['Bloomberg Code', 'Beta Relative To'],
    'U.S. Equity': 
         ['RU30INTR Index', 'Building Blocks'],
    'U.S. Large Cap Equity': 
         ['RU10INTR Index', 'U.S. Equity'],
    'U.S. Mid Cap Equity': 
         ['RUMCINTR Index', 'U.S. Equity'],
    'U.S. Small Cap Equity': 
         ['RU20INTR Index', 'U.S. Equity'],
    'U.S. Micro Cap Equity': 
         ['DWMIT Index', 'U.S. Equity'],
    'Global Equity': 
         ['GDUEACWF Index', 'Building Blocks'],
    'International Developed Equity': 
         ['GDUEACWZ Index', 'Building Blocks'],
    'International Small Cap Equity': 
         ['GCUDWXUS Index', 'International Developed Equity'],
    'Global Emerging Markets Equity': 
         ['GDUEEGF Index', 'Building Blocks'],
    }

equity_nonus_base = {
    'Asset Class': 
        ['Bloomberg Code', 'Beta Relative To'],
    'U.S. Equity': 
        ['GDDUUS Index', 'Building Blocks'],
    'U.S. Small Cap Equity': 
        ['GCUDUS Index', 'U.S. Equity'],
    'Europe Ex-UK Equity': 
        ['GDDUE15X Index', 'Building Blocks'],
    'Europe Small Cap Equity': 
        ['GCUDE15 Index', 'Europe Ex-UK Equity'],
    'UK Equity': 
        ['GDDUUK Index', 'Building Blocks'],
    'Japan Equity': 
        ['GDDUJN Index', 'Building Blocks'],
    'Japan Small Cap Equity': 
        ['GCUAJN Index', 'Japan Equity'],
    'Developed Market Pacific Ex-Japan Equity': 
        ['GDDUPXJ Index', 'Building Blocks'],
    'Global Emerging Markets Equity': 
        ['GDUEEGF Index', 'Building Blocks'],
    }

# %% [markdown]
# # Fixed Income Data

# %%
beta_fixed = ['', 'N/A', 'Emerging Debt Agg USD', 'Global Aggregate Ex-US', 'Global Developed Market Aggregate Fixed Income']
term_struc = ['', 'N/A', 'EM', 'NonUS', 'US']

# USD
fixed_us_base = {
     'Asset Class': 
        ['Bloomberg Code', 'Beta Relative To', 'Term Structure (%)', 'Default Rate(%)', 'Recovery Rate (%)'],
     'U.S. Aggregate': 
        ['LBUSTRUU Index', 'N/A', 'US', 0.15, 50.0],
     'U.S. Treasury': 
        ['LUATTRUU Index', 'N/A', 'US', 'N/A', 'N/A'],
     'U.S. Treasury Bills': 
        ['LD21TRUU Index', 'N/A', 'US', 'N/A', 'N/A'],
     'U.S. Intermediate Treasury': 
        ['LT08TRUU Index', 'N/A', 'US', 'N/A', 'N/A'],
     'U.S. Long Treasury': 
        ['LUTLTRUU Index', 'N/A', 'US', 'N/A', 'N/A'],
     'U.S. Investment Grade Credit': 
        ['LUCRTRUU Index', 'N/A', 'US', 0.29, 50.0],
     'U.S. Intermediate Investment Grade Credit': 
        ['LUICTRUU Index', 'N/A', 'US', 0.29, 50.0],
     'U.S. Long Investment Grade Credit': 
        ['LULCTRUU Index', 'N/A', 'US', 0.29, 50.0],
     'U.S. TIPS': 
        ['BCIT1T Index', 'N/A', 'US', 'N/A', 'N/A'],
     'U.S. Agencies': 
        ['BUAGTRUU Index', 'N/A', 'US', 'N/A', 'N/A'],
     'U.S. MBS': 
        ['LUMSTRUU Index', 'N/A', 'US', 0.10, 50.0],
     'U.S. Investment Grade CMBS': 
        ['LC09TRUU Index', 'N/A', 'US', 0.50, 50.0],
     'U.S. Intermediate Municipal': 
        ['I00777US Index', 'N/A', 'US', 0.10, 50.0],
     'U.S. Short Municipal': 
        ['I00779US Index', 'N/A', 'US', 0.10, 50.0],
     'U.S. High Yield': 
        ['LF98TRUU Index', 'N/A', 'US', 3.50, 40.0],
     'U.S. Bank Loans': 
        ['SPBDAL Index', 'N/A', 'US', 3.50, 60.0],
     'Global Aggregate Ex-US': 
        ['LG38TRUU Index', 'N/A', 'NonUS', 0.20, 50.0],
     'Global Treasury Ex-US': 
        ['LGT1TRUU Index', 'Global Aggregate Ex-US', 'NonUS', 0.15, 50.0],
     'Global Corporate Ex-US':
        ['I16598 Index', 'Global Aggregate Ex-US', 'NonUS', 0.30, 50.0],
     'Emerging Markets Sovereign USD': 
        ['BSSUTRUU Index', 'Global Aggregate Ex-US', 'EM', 0.85, 50.0],
     'Emerging Markets Corporate USD': 
        ['BSEKTRUU Index', 'Global Aggregate Ex-US', 'EM', 1.40, 50.0],
     'Emerging Markets Sovereign Local Currency': ['EMLCTRUU Index', 'Global Aggregate Ex-US', 'EM', 0.85, 50.0],
    }

# Non USD
fixed_nonus_base = {
    'Asset Class': 
        ['Bloomberg Code', 'Beta Relative To', 'Term Structure (%)', 'Default Rate(%)', 'Recovery Rate (%)'],
     'Global Developed Market Sovereign Fixed Income': 
        ['LGTRTRUU Index', 'Global Developed Market Aggregate Fixed Income', 'NonUS', 0.15, 50.0],
     'Global Developed Market Aggregate Fixed Income': 
        ['LEGATRUU Index', 'N/A', 'NonUS', 0.20, 50.0],
     'Global High Yield Fixed Income': 
        ['LG30TRUU Index', 'N/A', 'NonUS', 3.50, 40.0],
     'Emerging Markets Local Currency Fixed Income': 
        ['EMLCTRUU Index', 'Emerging Debt Agg USD', 'EM', 0.85, 50.0],
     'Emerging Markets Hard Currency Fixed Income': 
        ['BEHRTRUU Index', 'Emerging Debt Agg USD', 'US', 0.85, 50.0],
     'Emerging Markets Corporate Fixed Income': 
        ['BSEKTRUU Index', 'Emerging Debt Agg USD', 'US', 1.40, 50.0],
    }

# %% [markdown]
# ## Alts Data

# %%
beta_alts = ['', 'N/A', 'Building Blocks', 'Commodities', 'Global Equity', 'U.S. Equity']

alts_us_base = {
    'Asset Class': 
        ['Bloomberg Code', 'Beta Relative To', 'Information Ratio'],
    'Absolute Return': 
        ['HFRXGL Index', 'Global Equity', 0.30],
    'Hedge Funds': 
        ['HFRIFWI Index', 'Global Equity', 0.30],
    'Hedge Funds - Equity Hedge': 
        ['HFRIEHI Index', 'Global Equity', 0.30],
    'Hedge Funds - Event Driven':
        ['HFRIEDI Index', 'Global Equity', 0.30],
    'Hedge Funds - Macro': 
        ['HFRIMI Index', 'Global Equity', 0.30],
    'Hedge Funds - Relative Value':
        ['HFRIRVA Index', 'Global Equity', 0.30],
    'Hedge Funds - Managed Futures':
        ['CSLABMF Index', 'Global Equity', 0.30],
    'Commodities':
        ['BCOMTR Index', 'Building Blocks', 'N/A'],
    'Global Natural Resources Equity': 
        ['SPGNRUT Index', 'U.S. Equity', 'N/A'],
    'U.S. REIT': 
        ['FNERTR Index', 'U.S. Equity', 'N/A'],
    'Global REIT': 
        ['RUGL Index', 'Global Equity', 'N/A'],
    'Energy Infrastructure': 
        ['AMZX Index', 'Commodities', 0.25],
    }

alts_nonus_base = {
    'Asset Class': 
        ['Bloomberg Code', 'Beta Relative To', 'Information Ratio'],
    'Long-Short Equity': 
        ['HFRIEHI Index', 'U.S. Equity', 0.30],
    'Global Macro': 
        ['HFRIMI Index', 'U.S. Equity', 0.30],
    }

# %%
sg.SetOptions(element_padding=(1, 1))
bw = {'size': (20,1)}

# %%
# Building Blocks Tab
build_layout = [[sg.T('', **bw)],
              [sg.T('As of Date', **bw), 
               sg.Combo(values=as_of_date, **bw, key='as_of_date'),
               sg.T('Currency', **bw), 
               sg.Combo(values=currencies, default_value='USD', **bw, key='currency'),
               sg.T('Lambda', **bw),
               sg.Combo(values=[float(f'{i:.2f}') for i in list(np.arange(0, 1.01, 0.01))], default_value=0.99, **bw, key='lambda_val')],
              [sg.T('_'*190)],

              [sg.T('', **bw), 
               sg.T('US', **bw), 
               sg.T('Global', **bw),
               sg.T('Global Ex-US', **bw),
               sg.T('Emerging', **bw),
               sg.T('Country-Specific', **bw)],          
              [sg.T('Inflation (%)', **bw), 
               sg.Combo(values=value_range, default_value=2.2, **bw, key='us_inflation'),
               sg.Combo(values=value_range, default_value=1.8, **bw, key='gl_inflation'),
               sg.Combo(values=value_range, default_value=1.6, **bw, key='gl_exus_inflation'),
               sg.Combo(values=value_range, default_value=3.0, **bw, key='em_inflation'),
               sg.Combo(values=value_range, default_value=2.1, **bw, key='country_inflation'),],

              [sg.T('', **bw), 
               sg.T('US', **bw),
               sg.T('Global', **bw), 
               sg.T('Global Ex-US', **bw), 
               sg.T('Emerging', **bw),
               sg.T('', **bw),],          
              [sg.T('Real Cash Rate (%)', **bw), 
               sg.Combo(values=value_range, default_value=0.5, **bw, key='us_rcr'),
               sg.Combo(values=value_range, default_value=0.5, **bw, key='gl_rcr'),
               sg.Combo(values=value_range, default_value=0.5, **bw, key='gl_exus_rcr'),
               sg.Combo(values=value_range, default_value=2.0, **bw, key='em_rcr'),
               sg.T('', **bw),],
                
              [sg.T('', **bw), 
               sg.T('US', **bw), 
               sg.T('Global Ex-US', **bw), 
               sg.T('Emerging', **bw),
               sg.T('', **bw),],          
              [sg.T('Real Earnings Growth (%)', **bw), 
               sg.Combo(values=value_range, default_value=2.0, **bw, key='us_reg'),
               sg.Combo(values=value_range, default_value=1.5, **bw, key='gl_exus_reg'),
               sg.Combo(values=value_range, default_value=3.8, **bw, key='em_reg'),
               sg.T('', **bw),],

              [sg.T('', **bw), 
               sg.T('US', **bw), 
               sg.T('Europe Ex-UK', **bw), 
               sg.T('UK', **bw),
               sg.T('Japan', **bw),
               sg.T('APAC Ex Japan', **bw),
               sg.T('Emerging', **bw)],         
              [sg.T('Real GDP Growth (%)', **bw), 
               sg.Combo(values=value_range, default_value=2.0, **bw, key='us_real_gdp'),
               sg.Combo(values=value_range, default_value=1.5, **bw, key='europe_ex_uk_real_gdp'),
               sg.Combo(values=value_range, default_value=1.7, **bw, key='uk_real_gdp'),
               sg.Combo(values=value_range, default_value=0.8, **bw, key='japan_real_gdp'),
               sg.Combo(values=value_range, default_value=2.6, **bw, key='apac_ex_japan_real_gdp'),
               sg.Combo(values=value_range, default_value=3.8, **bw, key='em_real_gdp')],
               [sg.T('_'*190)],

               [sg.T('', **bw), 
               sg.T('US', **bw),
               sg.T('Global Ex-US', **bw), 
               sg.T('Europe Ex-UK', **bw), 
               sg.T('UK', **bw),
               sg.T('Japan', **bw),
               sg.T('APAC Ex Japan', **bw),
               sg.T('Emerging', **bw)],         
              [sg.T('Valuation Adjustment (%)', **bw), 
               sg.Combo(values=value_range, default_value=-0.5, **bw, key='us_equity_val'),
               sg.Combo(values=value_range, default_value=-0.30, **bw, key='gl_exus_equity_val'),
               sg.Combo(values=value_range, default_value=-0.25, **bw, key='europe_ex_uk_equity_val'),
               sg.Combo(values=value_range, default_value=-0.25, **bw, key='uk_equity_val'),
               sg.Combo(values=value_range, default_value=-0.25, **bw, key='japan_equity_val'),
               sg.Combo(values=value_range, default_value=-0.25, **bw, key='apac_ex_japan_equity_val'),
               sg.Combo(values=value_range, default_value=0.00, **bw, key='em_equity_val')],

              [sg.T('', **bw), 
               sg.T('US', **bw), 
               sg.T('Global Ex-US', **bw),
               sg.T('Europe Ex-UK', **bw), 
               sg.T('UK', **bw),
               sg.T('Japan', **bw),
               sg.T('APAC Ex Japan', **bw),
               sg.T('Emerging', **bw)],         
              [sg.T('Equity Income (%)', **bw), 
               sg.Combo(values=value_range, default_value=1.9, **bw, key='us_equity_income'),
               sg.Combo(values=value_range, default_value=2.8, **bw, key='gl_exus_equity_income'),
               sg.Combo(values=value_range, default_value=3.1, **bw, key='europe_ex_uk_equity_income'),
               sg.Combo(values=value_range, default_value=3.5, **bw, key='uk_equity_income'),
               sg.Combo(values=value_range, default_value=1.7, **bw, key='japan_equity_income'),
               sg.Combo(values=value_range, default_value=3.8, **bw, key='apac_ex_japan_equity_income'),
               sg.Combo(values=value_range, default_value=2.5, **bw, key='em_equity_income')],
                
              [sg.T('', **bw), 
               sg.T('US', **bw),
               sg.T('Global Ex-US', **bw), 
               sg.T('Europe Ex-UK', **bw), 
               sg.T('UK', **bw),
               sg.T('Japan', **bw),
               sg.T('APAC Ex Japan', **bw),
               sg.T('Emerging', **bw)],         
              [sg.T('Equity Buybacks (%)', **bw), 
               sg.Combo(values=value_range, default_value=0.7, **bw, key='us_equity_buyback'),
               sg.Combo(values=value_range, default_value=0.0, **bw, key='gl_exus_equity_buyback'),
               sg.Combo(values=value_range, default_value=0.0, **bw, key='europe_ex_uk_equity_buyback'),
               sg.Combo(values=value_range, default_value=-0.0, **bw, key='uk_equity_buyback'),
               sg.Combo(values=value_range, default_value=-0.0, **bw, key='japan_equity_buyback'),
               sg.Combo(values=value_range, default_value=-0.0, **bw, key='apac_ex_japan_equity_buyback'),
               sg.Combo(values=value_range, default_value=-0.0, **bw, key='em_equity_buyback')],
               [sg.T('_'*190)],

              [sg.T('', **bw), 
               sg.T('3 Mo', **bw), 
               sg.T('5 Yr', **bw), 
               sg.T('10 Yr', **bw),
               sg.T('30 Yr', **bw)],       
              [sg.T('Term Premiums (%)', **bw), 
               sg.Combo(values=value_range, default_value=0.00, **bw, key='term_prem_3mo'),
               sg.Combo(values=value_range, default_value=0.75, **bw, key='term_prem_5yr'),
               sg.Combo(values=value_range, default_value=1.0, **bw, key='term_prem_10yr'),
               sg.Combo(values=value_range, default_value=1.25, **bw, key='term_prem_30yr')],

              [sg.T('', **bw), 
               sg.T('US', **bw), 
               sg.T('Global', **bw), 
               sg.T('Emerging', **bw)],       
              [sg.T('Term Premium Adjust (%)', **bw), 
               sg.Combo(values=value_range, default_value=0, **bw, key='us_theme_tp_adjust'),
               sg.Combo(values=value_range, default_value=0, **bw, key='gl_theme_tp_adjust'),
               sg.Combo(values=value_range, default_value=0, **bw, key='em_theme_tp_adjust')],

              [sg.T('', **bw), 
               sg.T('US', **bw), 
               sg.T('Global', **bw), 
               sg.T('Emerging', **bw)],       
              [sg.T('Yrs to Normal Yields', **bw), 
               sg.Combo(values=[0,1,2,3,4,5,6,7,8,9,10], default_value=3, **bw, key='yield_norm_yrs'),
               sg.Combo(values=[0,1,2,3,4,5,6,7,8,9,10], default_value=5, **bw, key='gl_yield_norm_yrs'),
               sg.Combo(values=[0,1,2,3,4,5,6,7,8,9,10], default_value=5, **bw, key='em_yield_norm_yrs')],

              [sg.T('', **bw), 
               sg.T('US', **bw), 
               sg.T('Global', **bw), 
               sg.T('Emerging', **bw)],       
              [sg.T('Yrs to Normal Spreads', **bw), 
               sg.Combo(values=[0,1,2,3,4,5,6,7,8,9,10], default_value=5, **bw, key='spread_norm_yrs'),
               sg.Combo(values=[0,1,2,3,4,5,6,7,8,9,10], default_value=5, **bw, key='gl_spread_norm_yrs'),
               sg.Combo(values=[0,1,2,3,4,5,6,7,8,9,10], default_value=5, **bw, key='em_spread_norm_yrs')],
              [sg.T('_'*190)]]


# %%
# Equity Tab
equity_len = len(list(equity_us_base.keys()))
equity_nonus_len = len(list(equity_nonus_base.keys()))

equity_layout = [[sg.T('Asset Class', size=(35,1)), sg.T('Bloomberg Code', size=(17,1)), sg.T('Beta Relative To', size=(35,1))]] +\
                [[sg.In(list(equity_us_base.keys())[i], disabled=True, size=(40,1), key='equity_us_name' + str(i)), 
                  sg.In(list(equity_us_base.values())[i][0], size=(20,1), key='equity_us_code' + str(i)),
                  sg.Drop(values=beta_equity, default_value=list(equity_us_base.values())[i][1], size=(37,1), key='equity_us_beta' + str(i))] 
                  for i in range(1, equity_len)] +\
                [[sg.In(size=(40,1), key='equity_us_name' + str(equity_len)), sg.In(size=(20,1), key='equity_us_code' + str(equity_len)), 
                  sg.Drop(values=beta_equity, default_value='', size=(37,1),  key='equity_us_beta' + str(equity_len))]] +\
                [[sg.In(size=(40,1), key='equity_us_name' + str(equity_len+1)), sg.In(size=(20,1), key='equity_us_code' + str(equity_len+1)), 
                  sg.Drop(values=beta_equity, default_value='', size=(37,1),  key='equity_us_beta' + str(equity_len+1))]]


equity_nonus_layout =   [[sg.T('Asset Class', size=(35,1)), sg.T('Bloomberg Code', size=(17,1)), sg.T('Beta Relative To', size=(35,1))]] +\
                        [[sg.In(list(equity_nonus_base.keys())[i], disabled=True, size=(40,1), key='equity_nonus_name' + str(i)), 
                          sg.In(list(equity_nonus_base.values())[i][0], size=(20,1), key='equity_nonus_code' + str(i)),
                          sg.Drop(values=beta_equity, default_value=list(equity_nonus_base.values())[i][1], size=(37,1), key='equity_nonus_beta' + str(i))] 
                          for i in range(1, equity_nonus_len)] +\
                        [[sg.In(size=(40,1), key='equity_nonus_name' + str(equity_nonus_len)), sg.In(size=(20,1), key='equity_nonus_code' + str(equity_nonus_len)), 
                          sg.Drop(values=beta_equity, default_value='', size=(37,1),  key='equity_nonus_beta' + str(equity_nonus_len))]] +\
                        [[sg.In(size=(40,1), key='equity_nonus_name' + str(equity_nonus_len+1)), sg.In(size=(20,1), key='equity_nonus_code' + str(equity_nonus_len+1)), 
                          sg.Drop(values=beta_equity, default_value='', size=(37,1),  key='equity_nonus_beta' + str(equity_nonus_len+1))]]

# %%
# Fixed Income Tab
fixed_len = len(list(fixed_us_base.keys()))
fixed_nonus_len = len(list(fixed_nonus_base.keys()))

fixed_layout =  [[sg.T('Asset Class', size=(35,1)), sg.T('Bloomberg Code', size=(17,1)), sg.T('Beta Relative To', size=(35,1)),
                  sg.T('Term Structure', size=(15,1)), sg.T('Default Rate (%)', size=(15,1)), sg.T('Recovery Rate (%)', size=(15,1))]] +\
                [[sg.In(list(fixed_us_base.keys())[i], disabled=True, size=(40,1), key='fixed_us_name' + str(i)), 
                  sg.In(list(fixed_us_base.values())[i][0], size=(20,1), key='fixed_us_code' + str(i)),
                  sg.Drop(values=beta_fixed, default_value=list(fixed_us_base.values())[i][1], size=(37,1), key='fixed_us_beta' + str(i)),
                  sg.Drop(values=term_struc, default_value=list(fixed_us_base.values())[i][2], size=(14,1), key='fixed_us_term' + str(i)),
                  sg.Drop(values=default_val, default_value=list(fixed_us_base.values())[i][3], size=(14,1), key='fixed_us_default' + str(i)),
                  sg.Drop(values=recovery_val, default_value=list(fixed_us_base.values())[i][4], size=(14,1), key='fixed_us_recover' + str(i))] 
                  for i in range(1, fixed_len)] +\
                [[sg.In(size=(40,1), key='fixed_us_name' + str(fixed_len)), sg.In(size=(20,1), key='fixed_us_code' + str(fixed_len)), 
                  sg.Drop(values=beta_fixed, default_value='', size=(37,1), key='fixed_us_beta' + str(fixed_len)),
                  sg.Drop(values=term_struc, default_value='', size=(14,1), key='fixed_us_term' + str(fixed_len)), 
                  sg.Drop(values=default_val, default_value='', size=(14,1), key='fixed_us_default' + str(fixed_len)), 
                  sg.Drop(values=recovery_val, default_value='', size=(14,1), key='fixed_us_recover' + str(fixed_len))]] +\
                [[sg.In(size=(40,1), key='fixed_us_name' + str(fixed_len+1)), sg.In(size=(20,1), key='fixed_us_code' + str(fixed_len+1)), 
                  sg.Drop(values=beta_fixed, default_value='', size=(37,1), key='fixed_us_beta' + str(fixed_len+1)),
                  sg.Drop(values=term_struc, default_value='', size=(14,1), key='fixed_us_term' + str(fixed_len+1)), 
                  sg.Drop(values=default_val, default_value='', size=(14,1), key='fixed_us_default' + str(fixed_len+1)), 
                  sg.Drop(values=recovery_val, default_value='', size=(14,1), key='fixed_us_recover' + str(fixed_len+1))]]

fixed_nonus_layout =    [[sg.T('Asset Class', size=(35,1)), sg.T('Bloomberg Code', size=(17,1)), sg.T('Beta Relative To', size=(35,1)),
                          sg.T('Term Structure', size=(15,1)), sg.T('Default Rate (%)', size=(15,1)), sg.T('Recovery Rate (%)', size=(15,1))]] +\
                        [[sg.In(list(fixed_nonus_base.keys())[i], disabled=True, size=(40,1), key='fixed_nonus_name' + str(i)), 
                          sg.In(list(fixed_nonus_base.values())[i][0], size=(20,1), key='fixed_nonus_code' + str(i)),
                          sg.Drop(values=beta_fixed, default_value=list(fixed_nonus_base.values())[i][1], size=(37,1), key='fixed_nonus_beta' + str(i)),
                          sg.Drop(values=term_struc, default_value=list(fixed_nonus_base.values())[i][2], size=(14,1), key='fixed_nonus_term' + str(i)),
                          sg.Drop(values=default_val, default_value=list(fixed_nonus_base.values())[i][3], size=(14,1), key='fixed_nonus_default' + str(i)),
                          sg.Drop(values=recovery_val, default_value=list(fixed_nonus_base.values())[i][4], size=(14,1), key='fixed_nonus_recover' + str(i))] 
                          for i in range(1, fixed_nonus_len)] +\
                        [[sg.In(size=(40,1), key='fixed_nonus_name' + str(fixed_nonus_len)), sg.In(size=(20,1), key='fixed_nonus_code' + str(fixed_nonus_len)), 
                          sg.Drop(values=beta_fixed, default_value='', size=(37,1), key='fixed_nonus_beta' + str(fixed_nonus_len)),
                          sg.Drop(values=term_struc, default_value='', size=(14,1), key='fixed_nonus_term' + str(fixed_nonus_len)), 
                          sg.Drop(values=default_val, default_value='', size=(14,1), key='fixed_nonus_default' + str(fixed_nonus_len)), 
                          sg.Drop(values=recovery_val, default_value='', size=(14,1), key='fixed_nonus_recover' + str(fixed_nonus_len))]] +\
                        [[sg.In(size=(40,1), key='fixed_nonus_name' + str(fixed_nonus_len+1)), sg.In(size=(20,1), key='fixed_nonus_code' + str(fixed_nonus_len+1)), 
                          sg.Drop(values=beta_fixed, default_value='', size=(37,1), key='fixed_nonus_beta' + str(fixed_nonus_len+1)),
                          sg.Drop(values=term_struc, default_value='', size=(14,1), key='fixed_nonus_term' + str(fixed_nonus_len+1)), 
                          sg.Drop(values=default_val, default_value='', size=(14,1), key='fixed_nonus_default' + str(fixed_nonus_len+1)), 
                          sg.Drop(values=recovery_val, default_value='', size=(14,1), key='fixed_nonus_recover' + str(fixed_nonus_len+1))]]


# %%
# Alts Tab
alts_len = len(list(alts_us_base.keys()))
alts_nonus_len = len(list(alts_nonus_base.keys()))

alts_layout = [[sg.T('Asset Class', size=(35,1)), sg.T('Bloomberg Code', size=(17,1)), sg.T('Beta Relative To', size=(35,1)), sg.T('Information Ratio', size=(15,1))]] +\
                [[sg.In(list(alts_us_base.keys())[i], disabled=True, size=(40,1), key='alts_us_name' + str(i)),
                  sg.In(list(alts_us_base.values())[i][0], size=(20,1), key='alts_us_code' + str(i)),
                  sg.Drop(values=beta_alts, default_value=list(alts_us_base.values())[i][1], size=(37,1), key='alts_us_beta' + str(i)),
                  sg.Drop(values=ir_val, default_value=list(alts_us_base.values())[i][2], size=(14,1), key='alts_us_ir' + str(i))] 
                  for i in range(1, alts_len)] +\
                [[sg.In(size=(40,1), key='alts_us_name' + str(alts_len)), sg.In(size=(20,1), key='alts_us_code' + str(alts_len)), 
                  sg.Drop(values=beta_equity, default_value='', size=(37,1), key='alts_us_beta' + str(alts_len)), 
                  sg.Drop(values=ir_val, default_value='', size=(14,1), key='alts_us_ir' + str(alts_len))]] +\
                [[sg.In(size=(40,1), key='alts_us_name' + str(alts_len+1)), sg.In(size=(20,1), key='alts_us_code' + str(alts_len+1)), 
                  sg.Drop(values=beta_equity, default_value='', size=(37,1), key='alts_us_beta' + str(alts_len+1)), 
                  sg.Drop(values=ir_val, default_value='', size=(14,1), key='alts_us_ir' + str(alts_len+1))]]

alts_nonus_layout = [[sg.T('Asset Class', size=(35,1)), sg.T('Bloomberg Code', size=(17,1)), sg.T('Beta Relative To', size=(35,1)), sg.T('Information Ratio', size=(15,1))]] +\
                    [[sg.In(list(alts_nonus_base.keys())[i], disabled=True, size=(40,1), key='alts_nonus_name' + str(i)),
                      sg.In(list(alts_nonus_base.values())[i][0], size=(20,1), key='alts_nonus_code' + str(i)),
                      sg.Drop(values=beta_alts, default_value=list(alts_nonus_base.values())[i][1], size=(37,1), key='alts_nonus_beta' + str(i)),
                      sg.Drop(values=ir_val, default_value=list(alts_nonus_base.values())[i][2], size=(14,1), key='alts_nonus_ir' + str(i))] 
                      for i in range(1, alts_nonus_len)] +\
                    [[sg.In(size=(40,1), key='alts_nonus_name' + str(alts_nonus_len)), sg.In(size=(20,1), key='alts_nonus_code' + str(alts_nonus_len)), 
                      sg.Drop(values=beta_equity, default_value='', size=(37,1), key='alts_nonus_beta' + str(alts_nonus_len)), 
                      sg.Drop(values=ir_val, default_value='', size=(14,1), key='alts_nonus_ir' + str(alts_nonus_len))]] +\
                    [[sg.In(size=(40,1), key='alts_nonus_name' + str(alts_nonus_len+1)), sg.In(size=(20,1), key='alts_nonus_code' + str(alts_nonus_len+1)), 
                      sg.Drop(values=beta_equity, default_value='', size=(37,1), key='alts_nonus_beta' + str(alts_nonus_len+1)), 
                      sg.Drop(values=ir_val, default_value='', size=(14,1), key='alts_nonus_ir' + str(alts_nonus_len+1))]]

# %%
#Layout Configuration
layout = [[sg.TabGroup([[sg.Tab('Building Blocks', build_layout), 
                         sg.Tab('Equity-USD', equity_layout), 
                         sg.Tab('Equity-NonUSD', equity_nonus_layout), 
                         sg.Tab('Fixed-USD', fixed_layout), 
                         sg.Tab('Fixed-NonUSD', fixed_nonus_layout), 
                         sg.Tab('Alts-USD', alts_layout), 
                         sg.Tab('Alts-NonUSD', alts_nonus_layout)]])],    
         [sg.Button('Calculate'), sg.Button('Exit')]] 

window = sg.Window('Capital Market Assumptions', layout)      

while True:
    event, values = window.Read()
    if event in (None, 'Exit'):
        break
    if event == 'Calculate':
        val_dict = values

window.Close()
