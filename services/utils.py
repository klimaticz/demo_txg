import pandas as pd
import streamlit as st


@st.cache_data
def load_data(dir):
    return pd.read_csv(dir)


@st.cache_data
def get_mid(df):
    mean_latitude = df['Latitude'].mean()
    mean_longitude = df['Longitude'].mean()
    return mean_latitude, mean_longitude


@st.cache_data
def format_transform_bar(df, start, end=None):
    data = df.iloc[:, start:end]
    data_t = data.T.reset_index()
    data_t.columns = ['key', 'value']
    return data_t


@st.cache_data
def format_data(df, start, end, abbr):
    df_formatted = format_transform_bar(df, start, end)
    baseline_rows = df_formatted[df_formatted['key'].str.contains(
        'baseline')].set_index('key')['value'].to_dict()
    baseline_df = pd.DataFrame(baseline_rows.items(), columns=['key', 'value'])
    df_formatted = df_formatted[~df_formatted['key'].str.contains('baseline')]
    df_formatted = pd.concat([df_formatted, baseline_df.assign(key=lambda x: x['key'] + '_2041-2060'),
                              baseline_df.assign(key=lambda x: x['key'] + '_2081-2100')], ignore_index=True)
    df_formatted['year'] = df_formatted['key'].str.extract(r'(\d{4}-\d{4})')
    df_formatted = df_formatted.replace(
        ['_2041-2060', '_2081-2100'], '', regex=True)
    df_formatted = df_formatted.replace(abbr, '', regex=True)

    df_formatted['return_period'] = df_formatted['key'].str.extract(
        r'(\d+)_ARI_(RCP\d+|baseline)')[0]
    df_formatted['senario'] = df_formatted['key'].str.extract(
        r'(\d+)_ARI_(RCP\d+|baseline)')[1]
    df_formatted = df_formatted.drop('key', axis=1)
    df_formatted['year'] = df_formatted['year'].replace(
        {'2041-2060': '2050', '2081-2100': '2080'})

    df_formatted = df_formatted.pivot(index=['return_period', 'year'], columns=[
        'senario'], values='value').reset_index()
    df_formatted['return_period'] = df_formatted['return_period'].astype(
        int)
    df_formatted = df_formatted.sort_values(by='return_period')
    df_formatted = df_formatted[[
        'return_period', 'year', 'baseline', 'RCP45', 'RCP85']]
    return df_formatted


@st.cache_data
def filter_data(df, year):
    df = df[df['year'] == year]
    df_melt = df.drop(columns=['year'], axis=1)
    df_melt = df_melt.melt(id_vars='return_period',
                           var_name='senario', value_name='value')
    df_melt['return_period'] = df_melt['return_period']
    return df_melt

@st.cache_data
def format_scenario(scenario):
    scenario = scenario.replace('Avg', '')

    if scenario.startswith('Index_'):
        parts = scenario.split('_')
        if len(parts) >= 3:  # Ensure there are enough parts to extract
            scenario = f"Scenario {parts[1]}_{parts[2]}"
            scenario = scenario.strip('_')
            return scenario
        else:
            # Return the original scenario if unable to format
            return f"Scenario {scenario}"
    elif scenario.startswith('Baseline'):
        return 'Scenario Baseline'
    else:
        parts = scenario.split('_')
        if len(parts) >= 2:  # Ensure there are enough parts to extract
            return f"Scenario {parts[0]}_{parts[1]}"
        else:

            return f"Scenario {scenario}"