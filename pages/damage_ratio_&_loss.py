import streamlit as st
from services.utils import load_data, get_mid

df = load_data()
st.write(df)
