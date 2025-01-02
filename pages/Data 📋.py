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

st.divider()
st.write("### Add Food Data")
st.write("Add new food data to the Google Sheet.")

df_food_data = gsheets.load_google_sheet_data(sheet_name="food_data")

name = st.text_input("Name", value="")
type = st.selectbox("Type", options=df_food_data["Type"].unique())

st.write("##### Nutritional Value per 100g")
calories = st.number_input("Calories (kcal)", value=0)
fat = st.number_input("Fat (g)", value=0.)
carbs = st.number_input("Carbs (g)", value=0.)
protein = st.number_input("Protein (g)", value=0.)


st.write("#### Serving Size")
serving_name = st.text_input("Serving Name", value="portion(s)")
serving_size = st.number_input("Single Serving Size (g)", value=100)

if st.button("Add Food Item"):
    new_row = {
        "Name": name,
        "Fat (g)": fat,
        "Carbs (g)": carbs,
        "Protein (g)": protein,
        "Calories (kcal)": calories,
        "Serving Name": serving_name,
        "Single Serving (g)": serving_size,
        "Type": type,
    }
    df_food_data = pd.concat([df_food_data, pd.DataFrame([new_row])], ignore_index=True)
    gsheets.update_google_sheet(sheet_name="food_data", updated_data=df_food_data)
    st.success("Food item added successfully!")
    st.rerun()



st.divider()
st.write("### Edit Raw Data")
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
