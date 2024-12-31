import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
from google_sheets import GoogleSheetsInterface

gsheets = GoogleSheetsInterface()



st.set_page_config(page_title="Goals", page_icon="🎯")

st.markdown("# Targets 🎯")
st.sidebar.header("Targets")
st.write(
    """
    Set and track your targets! You can do it! 💪

    You can either use the calculator to determine your dailty caloric deficit target, or set it manually.
    """
)
who = st.selectbox("Who", options=["Bela", "Marleen"])

df_target = gsheets.load_google_sheet_data(sheet_name=f"target_{who.lower()}")
df_weight = gsheets.load_google_sheet_data(sheet_name=f"weight_log_{who.lower()}")

target = df_target["target"].values[0]
st.write(f"#### Current Goal: {target} kcal deficit")

st.divider()

st.header("Weight Loss Goal Calculator")



start_weight = int(round(df_weight["weight"].values[0], 0))
current_weight = int(round(df_weight["weight"].values[-1],0))

max_weight = round((current_weight + 10)/10, 0)*10
min_weight = round((current_weight - 20)/10, 0)*10
weight_range = np.arange(min_weight, max_weight+1, 1)
current_weight = st.select_slider("Current Weight", options=weight_range, value=current_weight)
desired_weight = st.select_slider("Desired Weight", options=weight_range, value=start_weight-10)

start_date = st.date_input("Start Date", value=datetime.today().date())
target_date = st.date_input("Target Date", value=datetime(year=2025, month=12, day=31))

time_delta = target_date - start_date
days_to_target = time_delta.days
weeks_to_target = days_to_target // 7

weight_delta = current_weight - desired_weight

weight_loss_per_week = weight_delta / weeks_to_target
weight_loss_per_day = weight_delta / days_to_target
calorie_deficit_per_day = weight_loss_per_day * 7700

st.write(f"#### Lose {weight_delta} kg in {days_to_target} days")
st.write(f"""
    * That's {weight_loss_per_week:.2f} kg per week
    * Or {weight_loss_per_day:.2f} kg per day
    * Or a daily calorie deficit of {calorie_deficit_per_day:.2f} kcal
""")

st.write(f"### Calorie Goal: {calorie_deficit_per_day:.2f} kcal deficit per day")

if st.button("Set Calculated Calorie Goal"):
    df_target.values[0] = calorie_deficit_per_day
    gsheets.update_google_sheet(
        sheet_name=f"target_{who.lower()}",
        updated_data=df_target
    )
    st.success("Calorie goal set successfully!")



st.divider()

st.header("Set Manually")
manual_calorie_deficit_per_day = st.number_input("Caloric Deficit Goal (kcal)", min_value=0, step=1, value=250)
if st.button("Set Manual Calorie Goal"):
    df_target.values[0] = manual_calorie_deficit_per_day
    gsheets.update_google_sheet(
        sheet_name=f"target_{who.lower()}",
        updated_data=df_target
    )
    st.success("Calorie goal set successfully!")
