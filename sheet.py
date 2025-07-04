# sheet.py
import gspread
import logging

class GoogleSheet:
    def __init__(self, credentials: dict, sheet_id: str):
        """
        Initializes the connection to Google Sheets.

        Args:
            credentials: The service account credentials dictionary.
            sheet_id: The ID of the Google Spreadsheet.
        """
        try:
            gc = gspread.service_account_from_dict(credentials)
            self.spreadsheet = gc.open_by_key(sheet_id)
            self.worksheet = self.spreadsheet.sheet1
            logging.info("Successfully connected to Google Sheet.")
        except gspread.exceptions.SpreadsheetNotFound:
            logging.error("Spreadsheet not found. Check the SHEET_ID.")
            raise
        except Exception as e:
            logging.error(f"Failed to initialize GoogleSheet: {e}")
            raise

    def search_movies(self, query: str) -> list:
        """
        Searches for movies in the sheet based on a query.
        This reads the sheet in real-time.

        Args:
            query: The search term (e.g., 'avatar').

        Returns:
            A list of matching movie records (dictionaries).
        """
        try:
            logging.info(f"Searching for '{query}' in Google Sheet...")
            all_records = self.worksheet.get_all_records()
            
            query_lower = query.lower()
            
            # Find movies where the query is a substring of the title (case-insensitive)
            matched_movies = [
                record for record in all_records 
                if query_lower in record.get('Title', '').lower()
            ]
            
            return matched_movies
        except Exception as e:
            logging.error(f"Error searching Google Sheet: {e}")
            # Attempt to re-authenticate and retry once, could help with token expiry
            try:
                self.__init__(self.creds, self.spreadsheet.id)
                all_records = self.worksheet.get_all_records()
                matched_movies = [record for record in all_records if query.lower() in record.get('Title', '').lower()]
                return matched_movies
            except Exception as retry_e:
                logging.error(f"Retry failed when searching Google Sheet: {retry_e}")
                return []