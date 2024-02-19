import streamlit as st
import pandas as pd
import altair as alt
from services.utils import load_data

st.header("Property Level WindSpeed, Damage Ratio & Loss")

df = load_data('./data/data.csv')


@st.cache_data
def format_data(df):
    mean = df.iloc[:, 36:66].mean(axis=0).round(3)
    st.write(mean)
    df_mean = pd.DataFrame(
        {'key': mean.index, 'value': mean.values}, columns=['key', 'value'])

    baseline_rows = df_mean[df_mean['key'].str.contains(
        'baseline')].set_index('key')['value'].to_dict()

    baseline_df = pd.DataFrame(baseline_rows.items(), columns=['key', 'value'])
    df_mean = df_mean[~df_mean['key'].str.contains('baseline')]

    # Add suffixes and append the rows back to the original DataFrame
    df_mean = pd.concat([df_mean, baseline_df.assign(key=lambda x: x['key'] + '_2041-2060'),
                         baseline_df.assign(key=lambda x: x['key'] + '_2081-2100')], ignore_index=True)

    df_mean['year'] = df_mean['key'].str.extract(r'(\d{4}-\d{4})')
    df_mean = df_mean.replace(['_2041-2060', '_2081-2100'], '', regex=True)
    df_mean = df_mean.replace('DM_tc_', '', regex=True)

    df_mean['return_period'] = df_mean['key'].str.extract(
        r'(\d+)_ARI_(RCP\d+|baseline)')[0]
    df_mean['senario'] = df_mean['key'].str.extract(
        r'(\d+)_ARI_(RCP\d+|baseline)')[1]
    df_mean = df_mean.drop('key', axis=1)
    df_mean['year'] = df_mean['year'].replace(
        {'2041-2060': '2050', '2081-2100': '2080'})

    transformed_df_mean = df_mean.pivot(index=['return_period', 'year'], columns=[
                                        'senario'], values='value').reset_index()
    transformed_df_mean['return_period'] = transformed_df_mean['return_period'].astype(
        int)
    transformed_df_mean = transformed_df_mean.sort_values(by='return_period')
    transformed_df_mean = transformed_df_mean[[
        'return_period', 'year', 'baseline', 'RCP45', 'RCP85']]
    return transformed_df_mean


@st.cache_data
def filter_data(df, year):
    df = df[df['year'] == year]
    df_melt = df.drop(columns=['year'], axis=1)
    df_melt = df_melt.melt(id_vars='return_period',
                           var_name='senario', value_name='value')
    df_melt['return_period'] = df_melt['return_period']
    return df_melt


year = st.radio("year", [
                "2050", "2080"], index=0, horizontal=True)

data = format_data(df)
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
)

st.altair_chart(chart, theme="streamlit", use_container_width=False)
