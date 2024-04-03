import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
from services.utils import load_data, get_mid, format_data, filter_data, format_transform_bar, format_scenario
from graphs.bar import grouped_bar, bar
from branca.element import Template, MacroElement
import altair as alt
from services.components import add_logo

add_logo()

st.header("Portfolio Level Analysis")
df = load_data('./data/data.csv')

color_palette = ["#e07a5f", "#3d405b", "#81b29a", "#f2cc8f", "#f4f1de"]


st.subheader("Portfolio level Average Damage Ratio")
data4 = format_transform_bar(df, 70, 75)
data4['key'] = data4['key'].apply(format_scenario)
bar(data4, 'value:Q', 'key:O', '',
    'Average Damage Ratio', order=["Baseline"])

st.subheader("Portfolio Level Total Loss in Miillion US Dollars")
data5 = format_transform_bar(df, 66, 71)
data5['key'] = data5['key'].apply(format_scenario)
data5['value'] = data5['value']/1000
bar(data5, 'value:Q', 'key:O', '', 'Total Loss in Miillion US $')

st.subheader("Portfolio Level- Mean Damage Ratio Index")
data6 = format_transform_bar(df, 75)
data6['key'] = data6['key'].apply(format_scenario)
bar(data6, 'value:Q', 'key:O', '',
    'Mean Damage Ratio Index', order=["Baseline"])
