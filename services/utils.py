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
