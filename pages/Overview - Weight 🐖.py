import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
from google_sheets import GoogleSheetsInterface
import plotly.express as px

gsheets = GoogleSheetsInterface()

st.set_page_config(page_title="Weight Overview", page_icon="🐖")

st.markdown("# Weight Overview 🐖")
st.write("View and log your weight.")

who = st.pills("Who", options=["Bela", "Marleen"], default="Bela", selection_mode="single")
df_weight_log = gsheets.load_google_sheet_data(sheet_name=f"weight_log_{who.lower()}")

current_weight = float(df_weight_log["weight"].values[-1])

df = df_weight_log.rename(columns={"date": "Date", "weight": "Weight (kg)"})
st.write(df)
df_weight_log_plot = df_weight_log.copy()
df_weight_log_plot = df_weight_log_plot.sort_values(by="date")

plot = px.line(df_weight_log_plot, x="date", y="weight", labels={"weight": "Weight (kg)"})
minval = int(df_weight_log_plot["weight"].min()-1.5)
maxval = int(df_weight_log_plot["weight"].max()+1.5)

plot.update_yaxes(range=[minval, maxval])

st.plotly_chart(plot, use_container_width=True)




st.write(f"### Log Weight")
date = st.date_input("Date", value=datetime.today().date())
weight = st.slider("Weight (kg)", min_value=current_weight-5, max_value=current_weight+5, value=current_weight, step=0.1)
# weight = st.number_input("Weight (kg)", min_value=current_weight, step=0.1)

new_row = {
    "date": date.strftime("%Y-%m-%d"),
    "weight": weight
}
df_weight_log = pd.concat([df_weight_log, pd.DataFrame([new_row])], ignore_index=True)

if st.button("Add Weight"):
    st.write("updated data:")
    st.dataframe(df_weight_log.tail(1))

    gsheets.update_google_sheet(
        sheet_name=f"weight_log_{who.lower()}",
        updated_data=df_weight_log
    )
    st.success("Food log added successfully!")
