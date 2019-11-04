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
import PySimpleGUI as sg

# %%
sg.SetOptions(font=("Arial", 10), element_padding=(0, 1))

fmt_header = {"title_location": "n", "title_color": "black"}
fmt_drop = {"size": (10, 1), "pad": (0, 3)}

# %%
labels = [
    "Inflation (%)",
    "Real Cash Rate (%)",
    "Real Earnings Growth (%)",
    "Real GDP Growth (%)",
    "Valuation Adjustment (%)",
    "Equity Income (%)",
    "Equity Buybacks (%)",
]

us = {
    "infl": 2.2,
    "rcr": 0.5,
    "reg": 2.0,
    "gdp": 2.0,
    "eq_val": -0.5,
    "eq_inc": 1.9,
    "eq_bback": 0.7,
}
gl = {
    "infl": 1.8,
    "rcr": 0.5,
    "reg": '',
    "gdp": '',
    "eq_val": '',
    "eq_inc": '',
    "eq_bback": '',
}
gl_exus = {
    "infl": 1.6,
    "rcr": 0.5,
    "reg": 1.5,
    "gdp": '',
    "eq_val": -0.3,
    "eq_inc": 2.8,
    "eq_bback": 0.0,
}
europe_exuk = {
    "infl": '',
    "rcr": '',
    "reg": '',
    "gdp": 1.5,
    "eq_val": -0.25,
    "eq_inc": 3.1,
    "eq_bback": 0.0,
}
uk = {
    "infl": '',
    "rcr": '',
    "reg": '',
    "gdp": 1.7,
    "eq_val": -0.25,
    "eq_inc": 3.5,
    "eq_bback": 0.0,
}
japan = {
    "infl": 2.2,
    "rcr": 0.5,
    "reg": 2.0,
    "gdp": 2.0,
    "eq_val": 2.0,
    "eq_inc": 2.0,
    "eq_bback": 2.0,
}
japan = {
    "infl": '',
    "rcr": '',
    "reg": '',
    "gdp": 0.8,
    "eq_val": -0.25,
    "eq_inc": 1.7,
    "eq_bback": 0.0,
}
apac_exjapan = {
    "infl": '',
    "rcr": '',
    "reg": '',
    "gdp": 2.6,
    "eq_val": -0.25,
    "eq_inc": 3.8,
    "eq_bback": 0.0,
}
em = {
    "infl": 3.0,
    "rcr": 2.0,
    "reg": 3.8,
    "gdp": 3.8,
    "eq_val": 0.0,
    "eq_inc": 2.5,
    "eq_bback": 0.0,
}

# %%
value_range = [(x / 20) for x in range(-100, 101)]
value_range.insert(0, 0.0)

# %%
label_col = [[sg.T(labels[i], pad=(0, 4))] for i in range(7)]
us_col = [[sg.Combo(values=value_range, default_value=list(us.values())[i], key='us_' + list(us.keys())[i], **fmt_drop)] for i in range(7)]

gl_col = [[sg.Combo(values=value_range, default_value=list(gl.values())[i], key='gl_' + list(gl.keys())[i], **fmt_drop)] for i in range(2)]
gl_col += [[sg.Text('', pad=(0, 4))] for i in range(5)]

gl_exus_col = [[sg.Combo(values=value_range, default_value=list(gl_exus.values())[i], key='gl_exus_' + list(gl_exus.keys())[i], **fmt_drop)] for i in range(3)]
gl_exus_col += [[sg.Text('', pad=(0, 4))] for i in range(1)]
gl_exus_col += [[sg.Combo(values=value_range, default_value=list(gl_exus.values())[i], key='gl_exus_' + list(gl_exus.keys())[i], **fmt_drop)] for i in range(4, 7)]

europe_exuk_col = [[sg.Text('', pad=(0, 4))] for i in range(3)]
europe_exuk_col += [[sg.Combo(values=value_range, default_value=list(europe_exuk.values())[i], key='europe_exuk_' + list(europe_exuk.keys())[i], **fmt_drop)] for i in range(3, 7)]

uk_col = [[sg.Text('', pad=(0, 4))] for i in range(3)]
uk_col += [[sg.Combo(values=value_range, default_value=list(uk.values())[i],  key='uk_' + list(uk.keys())[i], **fmt_drop)] for i in range(3, 7)]

japan_col = [[sg.Text('', pad=(0, 4))] for i in range(3)]
japan_col += [[sg.Combo(values=value_range, default_value=list(japan.values())[i],  key='japan_' + list(japan.keys())[i], **fmt_drop)] for i in range(3, 7)]

apac_exjapan_col = [[sg.Text('', pad=(0, 4))] for i in range(3)]
apac_exjapan_col += [[sg.Combo(values=value_range, default_value=list(apac_exjapan.values())[i], key='apac_exjapan_' + list(apac_exjapan.keys())[i], **fmt_drop)] for i in range(3,7)]

em_col = [[sg.Combo(values=value_range, default_value=list(em.values())[i], key='em_' + list(em.keys())[i], **fmt_drop)] for i in range(7)]

# %%
layout = [
    [
        sg.Frame("Building Blocks", label_col),
        sg.Frame("US Equity", us_col),
        sg.Frame("Global", gl_col),
        sg.Frame("Global Ex-US", gl_exus_col),
        sg.Frame("Europe Ex-UK", europe_exuk_col),
        sg.Frame("UK", uk_col),
        sg.Frame("Japan", japan_col),
        sg.Frame("APAC Ex-Japan", apac_exjapan_col),
        sg.Frame("Emerging Mkts", em_col),
    ],
    [sg.Button("Calculate"), sg.Button("Exit")],
]

window = sg.Window("Capital Market Assumptions").Layout(layout)

while True:
    event, values = window.Read()
    if event in (None, "Exit"):
        break
    if event == "Calculate":
        val_dict = values
        print(val_dict)

window.Close()

# %%
