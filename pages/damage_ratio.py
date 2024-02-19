import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
from services.utils import load_data, get_mid, format_data, filter_data
from branca.element import Template, MacroElement
import altair as alt


st.header("Damage Ratio")
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
            tooltip=f"Id: {row['ID']}, Damage Ratio: {round(row[column_string], 2)}",
        ).add_to(m)

macro = MacroElement()
macro._template = Template(template)
m.get_root().add_child(macro)

output = st_folium(m, width=1000, height=450)

id = None
try:
    id = int(output['last_object_clicked_tooltip'].split(",")[0].strip("Id: "))

except:
    st.warning("No Address is selected")


if id is not None:
    df = df[df['ID'] == id]
    data = format_data(df, 36, 66, 'DM_tc_')
    year = st.radio("year", [
                    "2050", "2080"], index=0, horizontal=True)

    data = filter_data(data, year)

    chart = alt.Chart(data).mark_bar().encode(
        x=alt.X('senario:N', title=None, axis=alt.Axis(labels=False)),
        y=alt.Y('value:Q', title="Damage Ratio"),
        color='senario:N',
        column=alt.Column(
            'return_period:O',
            title="Return Period",
            header=alt.Header(labelOrient='bottom',
                              titleOrient='bottom', labelPadding=10),
        ),
    ).properties(
        width=100,
        height=300
    )

    st.altair_chart(chart, theme="streamlit", use_container_width=False)

    data2 = df.iloc[:, 70:75]
    df2_formatted = data2.T.reset_index()
    df2_formatted.columns = ['key', 'value']
    df2_formatted.sort_values(by=['key'], inplace=True)
    chart2 = alt.Chart(df2_formatted).mark_line().encode(
        x='key',
        y='value'
    ).properties(
        width=800,
        height=400
    )
    st.write(df2_formatted)
    st.altair_chart(chart2, theme="streamlit", use_container_width=False)

    data3 = df.iloc[:, 66:70]
    df3_formatted = data3.T.reset_index()
    df3_formatted.columns = ['key', 'value']
    st.write(df3_formatted)

    chart3 = alt.Chart(df3_formatted).mark_arc().encode(
        theta="value",
        color="key"
    ).properties(
        width=600,
        height=400
    )

    st.altair_chart(chart3, theme="streamlit", use_container_width=False)
