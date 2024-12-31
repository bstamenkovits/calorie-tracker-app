import streamlit as st
import pandas as pd
from datetime import datetime
from google_sheets import GoogleSheetsInterface

gsheets = GoogleSheetsInterface()
df_food_data = gsheets.load_google_sheet_data(sheet_name="food_data")


st.set_page_config(page_title="Goals", page_icon="🚀")

st.markdown("# Goals 🚀")
st.sidebar.header("Goals")
st.write(
    """
    Set and track your goals!
    """
)

who = st.selectbox("Who", options=["Bela", "Marleen"])

current_weight = st.select_slider("Current Weight", options=[i for i in range(50, 150, 1)], value=111)
desired_weight = st.select_slider("Desired Weight", options=[i for i in range(50, 150, 1)], value=99)
target_date = st.date_input("Target Date", value=datetime(year=2025, month=12, day=31))

time_delta = target_date - datetime.today().date()
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

if st.button("Set Calorie Goal"):
    st.success("Calorie goal set successfully!")
# st.write(f"##### Or {weight_loss_per_day:.2f} kg per day")
# st.write(f"##### Or a daily calorie deficit of {calorie_deficit_per_day:.2f} kcal")
