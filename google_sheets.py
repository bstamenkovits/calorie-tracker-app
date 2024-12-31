import streamlit as st
import pandas as pd
import gspread
import oauth2client
from oauth2client import crypt
from typing import List
from oauth2client.service_account import ServiceAccountCredentials


class GoogleSheetsInterface:

    def __init__(self):
        self.client = self._get_client()
        self.url = st.secrets["connections"]["gsheets"]["spreadsheet"]

    def load_google_sheet_data(self, sheet_name):
        sheet = self.client.open_by_url(self.url).worksheet(sheet_name)
        data = pd.DataFrame(sheet.get_all_records())
        return data

    def update_google_sheet(self, sheet_name, updated_data):
        sheet = self.client.open_by_url(self.url).worksheet(sheet_name)
        sheet.clear()
        sheet.update([updated_data.columns.values.tolist()] + updated_data.values.tolist())

    def _get_client(self):
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
