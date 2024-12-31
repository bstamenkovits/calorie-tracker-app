import streamlit as st
from google_sheets import GoogleSheetsInterface

gsheets = GoogleSheetsInterface()
df_food_data = gsheets.load_google_sheet_data(sheet_name="food_data")


st.set_page_config(page_title="Food Logger", page_icon="🍔")

st.markdown("# Food Logger 🍔")
st.sidebar.header("Food Logger")
st.write(
    """
    Log Food and Calorie Intake
    """
)

st.write("#### When 🕙")
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



st.button("Add Food")




# Streamlit widgets automatically run the script from top to bottom. Since
# this button is not connected to any other logic, it just causes a plain
# rerun.
# st.button("Re-run")
