import streamlit as st


@st.cache_resource
def add_logo():
    st.markdown(
        """
        <style>
            [data-testid="stSidebarNav"] {
                background-image: url(https://klimaticz.com/wp-content/uploads/2023/07/Logo-klimaticz-1024x273.png);
                background-repeat: no-repeat;
                background-size: contain;
                background-position: center;
                background-size: 50%;
                height: 15vh;

            }
        </style>
        """,
        unsafe_allow_html=True,
    )