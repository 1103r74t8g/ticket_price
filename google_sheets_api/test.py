import gspread
from google.oauth2.service_account import Credentials

scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds = Credentials.from_service_account_file("credentials.json", scopes=scope)
client = gspread.authorize(creds)

try:
    sheet = client.open("lowest_price").sheet1
    print("connected:", sheet.title)
    sheet.update("A1", [["test"]])
    print("success")
except Exception as e:
    print("wrong:", e)
