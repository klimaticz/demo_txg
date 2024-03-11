import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
from services.utils import load_data, get_mid, format_data, filter_data
from graphs.bar import grouped_bar
from branca.element import Template, MacroElement
import altair as alt

st.header("Damage Ratio")
df = load_data('./data/data.csv')

color_palette = ["#e07a5f", "#3d405b", "#81b29a", "#f2cc8f"]


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
column_string = f"DM_tc_{RP}_ARI_RCP{RCP}_{Year}" if Year else f"DM_tc_{RP}_ARI_{RCP}"

df_viz = pd.concat(
    [df['ID'], df['Address'], df['Latitude'], df['Longitude'], df[column_string]], axis=1)

mean_latitude, mean_longitude = get_mid(df_viz)
m = folium.Map(location=[mean_latitude, mean_longitude],
               zoom_start=5)

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
    <li><span style='background:green; opacity:0.75;'></span>Damage <= 0.2</li>
    <li><span style='background:yellow; opacity:0.75;'></span>0.2 < Damage <= 0.4</li>
    <li><span style='background:orange; opacity:0.75;'></span>0.4 < Damage <= 0.6</li>
    <li><span style='background:red; opacity:0.75;'></span>0.6 < Damage <= 0.8</li>
    <li><span style='background:purple; opacity:0.75;'></span>Damage > 0.8</li>
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
    if row[column_string] <= 0.2:
        category = 'Category - 1'
    elif 0.02 < row[column_string] <= 0.4:
        category = 'Category - 2'
    elif 0.4 < row[column_string] <= 0.6:
        category = 'Category - 3'
    elif 0.6 < row[column_string] <= 0.8:
        category = 'Category - 4'
    elif row[column_string] > 0.8:
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
            tooltip=f"Address: {row['Address']} <br>Damage Ratio: {round(row[column_string], 2)}",
        ).add_to(m)

macro = MacroElement()
macro._template = Template(template)
m.get_root().add_child(macro)

output = st_folium(m, width=1000, height=450)


address = None
try:
    address = str(output['last_object_clicked_tooltip'].split("Damage Ratio")[
        0].strip("Address:").strip(" "))

except:
    st.warning("No Address is selected")


if address is not None:

    df = df[df['Address'] == address]
    st.subheader("Property Level Damage Ratio")
    data = format_data(df, 36, 66, 'DM_tc_')

    year = st.radio("Year", [
                    "2050", "2080"], index=0, horizontal=True)

    data = filter_data(data, year)
    grouped_bar(data, 'value:Q', "Damage Ratio")

    st.subheader("Average Damage Ratio")
    data2 = df.iloc[:, 70:75]
    df2_formatted = data2.T.reset_index()
    df2_formatted.columns = ['key', 'value']

    x_format = {
        'Baseline_Avg_DM': 'Baseline',
        '45_2041Avg_DM': 'Scenario 4.5, 2050',
        '45_2081Avg_DM': 'Scenario 4.5, 2080',
        '85_2041Avg_DM': 'Scenario 8.5, 2050',
        '85_2081Avg_DM': 'Scenario 8.5, 2080'
    }

    df2_formatted['formatted_key'] = df2_formatted['key'].map(x_format)
    line_color = "#3d405b"

    chart2 = alt.Chart(df2_formatted).mark_line(stroke=line_color).encode(
        x=alt.X('formatted_key:N', title='Average Damage Ratio',
                sort=list(x_format.values())),
        y=alt.Y('value:Q', title=None),
    ).properties(
        width=800,
        height=400
    )

    st.altair_chart(chart2, theme="streamlit", use_container_width=False)

    st.subheader("Average Loss in US $")
    data3 = df.iloc[:, 66:70]
    df3_formatted = data3.T.reset_index()
    df3_formatted.columns = ['key', 'value']
    pie_renamed_keys = {'45_2041Avg_Loss': 'Scenario 4.5 in 2050',
                        '45_2081Avg_Loss': 'Scenario 4.5 in 2080', '85_2041Avg_Loss': 'Scenario 8.5 in 2050', '85_2081Avg_Loss': 'Scenario 8.5 in 2080'}
    df3_formatted['Senarios'] = df3_formatted['key'].map(pie_renamed_keys)

    base = alt.Chart(df3_formatted).encode(
        alt.Theta("value:Q", stack=True),
        alt.Color("Senarios:N", scale=alt.Scale(range=color_palette))
    ).properties(
        width=600,
        height=400
    )

    pie = base.mark_arc(outerRadius=120)
    text = base.mark_text(radius=140, size=14, fill="black").encode(
        text="value:N"
    )

    st.altair_chart(pie + text, theme="streamlit", use_container_width=True)
