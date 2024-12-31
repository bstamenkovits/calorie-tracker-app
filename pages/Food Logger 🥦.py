import streamlit as st
import pandas as pd
from google_sheets import GoogleSheetsInterface

gsheets = GoogleSheetsInterface()
df_food_data = gsheets.load_google_sheet_data(sheet_name="food_data")


st.set_page_config(page_title="Food Logger", page_icon="🥦")

st.markdown("# Food Logger 🥦")
st.sidebar.header("Food Logger")
st.write(
    """
    Log Food and Calorie Intake
    """
)


"""
Interface for adding food log
"""
who = st.selectbox("Who", options=["Bela", "Marleen"])

st.write("#### When 🕙")
date = st.date_input("Date", value=pd.to_datetime("today"))
meal = st.selectbox("Meal", options=["Breakfast", "Lunch", "Dinner", "Snack"])

st.write("#### What ❓")
type = st.selectbox("Type of Food", options = df_food_data["Type"].unique())
name = st.selectbox("Food Name", options=df_food_data[df_food_data["Type"]==type].sort_values(by="Name")["Name"])

st.write("#### Amount ⚖️")
serving_options = df_food_data[df_food_data["Name"]==name]["Serving Name"].to_list()
serving_options.append("g")
serving = st.selectbox("Type of serving", options=serving_options)

if serving == "g":
    quantity = st.number_input("Quantity (g)", min_value=0, step=1)
    weight = quantity
else:
    quantity = st.selectbox("Servings", options=[i for i in range(1, 11)])
    weight = (quantity * df_food_data[df_food_data["Name"]==name]["Single Serving (g)"]).values[0]

kcal_per_100g = df_food_data[df_food_data["Name"]==name]["Calories (kcal)"].values[0]
kcal = (kcal_per_100g * weight) / 100
st.write(f"### For {meal}, {quantity} {serving} of {name} =  {kcal} kcal")


"""
Add food to the google sheet
"""
if st.button("Add Food"):
    df_food_log = gsheets.load_google_sheet_data(sheet_name=f"food_log_{who.lower()}")
    new_row = {
        "date": date.strftime("%Y-%m-%d"),
        "meal": meal,
        "name": name,
        "quantity": quantity,
        "serving": serving,
    }
    df_food_log = pd.concat([df_food_log, pd.DataFrame([new_row])], ignore_index=True)

    st.write("updated data:")
    st.dataframe(df_food_log.tail(1))

    gsheets.update_google_sheet(
        sheet_name=f"food_log_{who.lower()}",
        updated_data=df_food_log
    )
    st.success("Food log added successfully!")

# df_food_log = gsheets.load_google_sheet_data(sheet_name=f"food_log_{who.lower()}")
# st.dataframe(df_food_log)



# Streamlit widgets automatically run the script from top to bottom. Since
# this button is not connected to any other logic, it just causes a plain
# rerun.
# st.button("Re-run")
