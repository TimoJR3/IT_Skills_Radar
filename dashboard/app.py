import os

import streamlit as st

st.set_page_config(page_title="IT Skills Radar", page_icon="📊", layout="wide")

api_url = os.getenv("API_URL", "http://localhost:8000")

st.title("IT Skills Radar")
st.caption("Scaffold stage: dashboard placeholder for future vacancy analytics.")

st.subheader("Current Status")
st.write("Backend, database, and dashboard containers are prepared.")
st.write("Next stages will add vacancy ingestion, skill normalization, and analytics.")

st.subheader("Configured API")
st.code(api_url)

