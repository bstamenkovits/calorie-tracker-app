import streamlit as st
import pandas as pd
from google_sheets import GoogleSheetsInterface
from datetime import datetime
import plotly.express as px

gsheets = GoogleSheetsInterface()


st.set_page_config(
    page_title="Health Tracker",
    page_icon="🍎",
)

st.write("# Healthy Plapjes! 🍎")
weight_log_bela = gsheets.load_google_sheet_data(sheet_name="weight_log_bela")
weight_log_bela = weight_log_bela.sort_values(by="date")
start_bela = weight_log_bela["weight"].values[0]
weight_log_bela["delta"] = weight_log_bela["weight"] - start_bela

weight_log_marleen = gsheets.load_google_sheet_data(sheet_name="weight_log_marleen")
weight_log_marleen = weight_log_marleen.sort_values(by="date")
start_marleen = weight_log_marleen["weight"].values[0]
weight_log_marleen["delta"] = weight_log_marleen["weight"] - start_marleen

df = weight_log_bela.merge(weight_log_marleen, on="date", suffixes=("_bela", "_marleen"), how="outer")

df = df.rename(columns={
    "date": "Date",
    "weight_bela": "Weight Bela (kg)",
    "weight_marleen": "Weight Marleen (kg)",
    "delta_bela": "Delta Bela (kg)",
    "delta_marleen": "Delta Marleen (kg)"
})

st.write(df)
fig = px.line(df, x="Date", y=["Delta Bela (kg)", "Delta Marleen (kg)"], title="Weight Loss Over Time")
st.plotly_chart(fig)
