import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
from google_sheets import GoogleSheetsInterface

gsheets = GoogleSheetsInterface()



st.set_page_config(page_title="Data", page_icon="📋")

st.markdown("# View & Edit Data 📋")
st.sidebar.header("Data")
st.write(
    """
    View and edit data in Google Sheets manually.
    """
)

sheet_name = st.selectbox("Select a sheet", [
    "food_data",
    "food_log_bela",
    "food_log_marleen",
    "target_bela",
    "target_marleen",
    "weight_log_bela",
    "weight_log_marleen"
])

data = gsheets.load_google_sheet_data(sheet_name=sheet_name)
df = st.data_editor(data, num_rows="dynamic")

if st.button("Save Changes"):
    gsheets.update_google_sheet(sheet_name=sheet_name, updated_data=df)
    st.success("Google Sheet updated successfully!")
