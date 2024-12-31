import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from google_sheets import GoogleSheetsInterface

gsheets = GoogleSheetsInterface()

def main():
    st.title("Calorie Tracker 2")
    st.write("Original Data from Google Sheets:")
    df = pd.DataFrame({
        "Food": ["Apple", "Banana", "Carrot"],
        "Calories": [95, 105, 25],
        "Quantity": [1, 2, 3]
    })

    st.dataframe(df)


    st.divider()
    st.title("Add Food")
    name = st.selectbox("Food Name", options=df["Food"])
    meal = st.selectbox("Meal", options=["Breakfast", "Lunch", "Dinner", "Snack"])
    serving = st.selectbox("Servings", options=[i for i in range(1, 11)])

    st.write(f"### For {meal}, {serving} {name} = {serving*100} kcal")
    st.button("Add Food")


    with st.expander("Edit Data"):
        sheet_name = st.selectbox("Select a sheet", ["food_data", "new_worksheet"])

        data = gsheets.load_google_sheet_data(sheet_name=sheet_name)
        df = st.data_editor(data, num_rows="dynamic")

        if st.button("Save Changes"):
            gsheets.update_google_sheet(sheet_name=sheet_name, updated_data=df)
            st.success("Google Sheet updated successfully!")

if __name__ == "__main__":
    main()
