import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials


def authenticate_google_sheets(creds_file):
    scopes = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_name(creds_file, scopes)
    client = gspread.authorize(creds)
    return client


def load_google_sheet_data(sheet_url, sheet_name):
    client = authenticate_google_sheets("private-key.json")
    sheet = client.open_by_url(sheet_url).worksheet(sheet_name)
    data = pd.DataFrame(sheet.get_all_records())
    return data, sheet


def update_google_sheet(sheet, updated_data):
    sheet.clear()  # Clear existing data
    sheet.update([updated_data.columns.values.tolist()] + updated_data.values.tolist())


def main():
    st.title("Calorie Tracker")
    st.write("Original Data from Google Sheets:")

    df = pd.DataFrame({
        "Food": ["Apple", "Banana", "Carrot"],
        "Calories": [95, 105, 25],
        "Quantity": [1, 2, 3]
    })

    st.dataframe(df)
    st.button("Refresh Data")

    with st.expander("Edit Data"):
        sheet_url = st.secrets["connections"]["gsheets"]["spreadsheet"]
        sheet_name = st.selectbox("Select a sheet", ["food_data", "new_worksheet"])

        # data, sheet = load_google_sheet_data(sheet_url, sheet_name)
        # df = st.data_editor(data, num_rows="dynamic")

        # if st.button("Save Changes"):
        #     update_google_sheet(sheet, df)
        #     st.success("Google Sheet updated successfully!")

if __name__ == "__main__":
    main()
