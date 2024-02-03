import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
from services.utils import load_data, get_mid
from branca.element import Template, MacroElement

df = load_data('./data/data.csv')


def format_rcp(rcp):
    return "baseline" if rcp == "Baseline" else str(int(float(rcp)*10))


def format_year(year):
    return "2041-2060" if year == "2050" else "2081-2100"


col1, col2, col3 = st.columns(3)

with col1:
    RCP = st.selectbox('RCP', ("Baseline", "4.5", "8.5"))

with col2:
    RP = st.selectbox('RP', ("1000", "500", "100", "50", "20", "10"))

with col3:
    Year = st.selectbox("Year", ("2050", "2080")
                        ) if RCP != "Baseline" else None

RCP = format_rcp(RCP)
Year = format_year(Year) if RCP != "baseline" else None
column_string = f"SPD_tc_{RP}_ARI_RCP{RCP}_{Year}" if Year else f"SPD_tc_{RP}_ARI_{RCP}"


df_viz = pd.concat(
    [df['Address'], df['Latitude'], df['Longitude'], df[column_string]], axis=1)

mean_latitude, mean_longitude = get_mid(df_viz)
m = folium.Map(location=[mean_latitude, mean_longitude], zoom_start=5)

color_scale = {
    'Category - 1': 'green',
    'Category - 2': 'yellow',
    'Category - 3': 'orange',
    'Category - 4': 'red',
    'Category - 5': 'purple'
}

template = """
{% macro html(this, kwargs) %}
<div id='maplegend' class='maplegend' 
    style='position: absolute; z-index:9999; background-color:rgba(255, 255, 255, 0.5);
     border-radius:6px; padding: 10px; font-size:10.5px; right: 20px; top: 20px;'>     
<div class='legend-scale'>
  <ul class='legend-labels'>
    <li><span style='background:green; opacity:0.75;'></span>Wind speed <= 55.21</li>
    <li><span style='background:yellow; opacity:0.75;'></span>55.65 <= Wind speed <= 64.29</li>
    <li><span style='background:orange; opacity:0.75;'></span>64.50 <= Wind speed <= 75.76</li>
    <li><span style='background:red; opacity:0.75;'></span>75.90 <= Wind speed <= 90.56</li>
    <li><span style='background:purple; opacity:0.75;'></span>Wind speed >= 91.07</li>
  </ul>
</div>
</div> 
<style type='text/css'>
  .maplegend .legend-scale ul {margin: 0; padding: 0; color: #0f0f0f;}
  .maplegend .legend-scale ul li {list-style: none; line-height: 18px; margin-bottom: 1.5px;}
  .maplegend ul.legend-labels li span {float: left; height: 16px; width: 16px; margin-right: 4.5px;}
</style>
{% endmacro %}"""

for index, row in df_viz.iterrows():
    category = None
    if row[column_string] <= 55.21:
        category = 'Category - 1'
    elif 55.65 <= row[column_string] <= 64.29:
        category = 'Category - 2'
    elif 64.50 <= row[column_string] <= 75.76:
        category = 'Category - 3'
    elif 75.90 <= row[column_string] <= 90.56:
        category = 'Category - 4'
    elif row[column_string] >= 91.07:
        category = 'Category - 5'

    if category:
        folium.CircleMarker(
            location=[row['Latitude'], row['Longitude']],
            stroke=False,
            radius=10,
            color=color_scale[category],
            fill=True,
            fill_color=color_scale[category],
            fill_opacity=0.7,
            tooltip=f"Wind Speed: {round(row[column_string], 2)}"
        ).add_to(m)

macro = MacroElement()
macro._template = Template(template)
m.get_root().add_child(macro)
folium.plugins.Draw(export=True).add_to(m)
output = st_folium(m, width=700, height=500)

st.write(df_viz)
