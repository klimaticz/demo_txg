#!/usr/bin/env python
# coding: utf-8

import os
import requests
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

# Google Geocoding API key.
API_KEY = os.environ.get('key')

# Streamlit App
location =  st.text_input('Enter your Address: ', placeholder='Enter any address')

# Submit button
submit_btn = st.button('Get Geo Coordinates.')

if submit_btn:
    # Create the API request URL
    GEOCODING_URL = f'https://maps.googleapis.com/maps/api/geocode/json?address={location}&key={API_KEY}'
    # Make the API request
    response = requests.get(GEOCODING_URL)

    # Check for a successful response
    if response.status_code == 200:
        data = response.json()
        # Access the geocoding results from the response
        results = data.get('results', [])
        if results:
            # Extract geocoding information (e.g., latitude and longitude)
            geometry = results[0].get('geometry', {})
            location_info = geometry.get('location', {})
            latitude = location_info.get('lat')
            longitude = location_info.get('lng')
            st.write(f"Latitude: {latitude}, Longitude: {longitude}")
        else:
            st.write("No geocoding results found.")
    else:
        st.write("Failed to fetch geocoding data. Check your API key and request.")

    # Create a Map Object
    map_data = {
        "lat": [latitude],
        "lon": [longitude],
        "City": [location]
    }

    # Create a Pandas Data-Frame
    df = pd.DataFrame(map_data)

    # Write data to streamlit
    st.write(df)

    # Plot Map co-ordinates
    st.map(data=df, zoom=12)
