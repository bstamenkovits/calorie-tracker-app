import streamlit as st
import pandas as pd
from google_sheets import GoogleSheetsInterface
from datetime import datetime
import time
from gspread.exceptions import APIError

gsheets = GoogleSheetsInterface()

df = gsheets.load_google_sheet_data(sheet_name="food_data")

st.set_page_config(
    page_title="Test",
    page_icon="T",
)

st.write("# Test ")
st.write("some text")
st.write(df)
