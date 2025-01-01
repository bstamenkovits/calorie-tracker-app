import streamlit as st
import pandas as pd
import gspread
from gspread import Client
import oauth2client
from oauth2client import crypt
from typing import List
from oauth2client.service_account import ServiceAccountCredentials
import os


class GoogleSheetsInterface:

    cache_path = "cache/gsheets"

    def __init__(self):
        self.client = self._get_client()
        self.url = st.secrets["connections"]["gsheets"]["spreadsheet"]

    def load_google_sheet_data(self, sheet_name:str) -> pd.DataFrame:
        """
        Load data from a Google Sheet

        The Google Sheets API has a limit of 60 requests per minute. Each time
        a dropdown is changed in the Streamlit app, this method is called for
        each dataset. This can cause the limit to be reached. To prevent this
        the data is stored in a csv file and only downloaded again if the file
        is older than 3 minutes.

        Args:
            sheet_name (str): The name of the sheet in the Google Sheet document

        Returns:
            data(pd.DataFrame): The data from the Google Sheet as a pandas DataFrame
        """
        # check if file exists
        if os.path.exists(f"{self.cache_path}/{sheet_name}.csv"):
            # check how old the file is
            file_creation_time = os.path.getctime(f"{self.cache_path}/{sheet_name}.csv")
            current_time = pd.Timestamp.now().timestamp()
            elapsed_time = current_time - file_creation_time # miliseconds

            limit = 60*5 # 5 minutes
            limit += 3600 # 1 hour (daylight saving time or timezone difference)
            
            # if the file is not too old, use return data from file
            if  elapsed_time < limit:
                return pd.read_csv(f"{self.cache_path}/{sheet_name}.csv")

        print("API Call")
        # if the file is too old, download the data from Google Sheets
        sheet = self.client.open_by_url(self.url).worksheet(sheet_name)
        data = pd.DataFrame(sheet.get_all_records())

        # store the data in a csv file
        if os.path.exists(f"{self.cache_path}/{sheet_name}.csv"):
            os.remove(f"{self.cache_path}/{sheet_name}.csv")
        data.to_csv(f"{self.cache_path}/{sheet_name}.csv", index=False)
        return data

    def update_google_sheet(self, sheet_name:str, updated_data:pd.DataFrame) -> None:
        """
        Update a Google Sheet with new data.

        The Google Sheets API is used to clear the sheet and fill it with the
        data inside of updated_data. Make sure the updated_data is the same
        shape as the data that is already in the Google Sheet. It is adviced to
        use the load_google_sheet_data method to get the data from the Google
        Sheet, add a new row to it, and then use this method to update the data.

        Downloaded data files are stored in the same directory as the script.
        They are removed after an update, this will cause load_google_sheet_data
        to download the data again. This is necessary to get up to date data
        after an update takes place.

        Args:
            sheet_name (str): The name of the sheet in the Google Sheet document
            updated_data (pd.DataFrame): The updated data (old data + new data)
                to be uploaded to the Google Sheet
        """
        sheet = self.client.open_by_url(self.url).worksheet(sheet_name)
        sheet.clear()
        sheet.update([updated_data.columns.values.tolist()] + updated_data.values.tolist())

        # remove sheet_name.csv file to force download from Google Sheets
        if os.path.exists(f"{self.cache_path}/{sheet_name}.csv"):
            os.remove(f"{self.cache_path}/{sheet_name}.csv")

    def _get_client(self) -> Client:
        """
        Get a client object to interact with Google Sheets API

        Returns:
            gspread.Client: A client object that can be used to interact with Google Sheets API
        """
        scopes = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive"
        ]
        creds = self._get_credentials(scopes)
        client = gspread.authorize(creds)
        return client

    def _get_credentials(
        self,
        scopes: List[str],
    ) -> ServiceAccountCredentials:
        """
        Create a credentials object from streamlit secrets

        The logic in this function is copied from the _from_parsed_json_keyfile
        method in oauth2client.service_account module. The only difference is
        that the keyfile_dict is loaded from streamlit secrets insteaed from a
        json keyfile.

        Args:
            scopes (List[str]): List of scopes to request access to the Google Sheets API
        Returns:
            ServiceAccountCredentials: A credentials object that can be used to authenticate
                with the Google Sheets API
        """
        keyfile_dict = st.secrets["connections"]["gsheets"]

        service_account_email = keyfile_dict['client_email']
        private_key_pkcs8_pem = keyfile_dict['private_key']
        private_key_id = keyfile_dict['private_key_id']
        client_id = keyfile_dict['client_id']
        token_uri = keyfile_dict.get('token_uri', oauth2client.GOOGLE_TOKEN_URI)
        revoke_uri = keyfile_dict.get('revoke_uri', oauth2client.GOOGLE_REVOKE_URI)
        signer = crypt.Signer.from_string(private_key_pkcs8_pem)

        credentials = ServiceAccountCredentials(
            service_account_email,
            signer,
            scopes=scopes,
            private_key_id=private_key_id,
            client_id=client_id,
            token_uri=token_uri,
            revoke_uri=revoke_uri,
        )
        credentials._private_key_pkcs8_pem = private_key_pkcs8_pem

        return credentials
