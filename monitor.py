import os
import requests
import smtplib
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import gspread
from google.oauth2.service_account import Credentials

load_dotenv()

# 雜七雜八資料
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
TO_EMAIL = "willy110439@gmail.com"

URL = "https://gametime.co/concert/ado-tickets/7-29-2025-baltimore-md-cfg-bank-arena/events/671b084afb59e4425bdc20c0"

SPREADSHEET_NAME = "lowest_price"  

def get_ticket_price(url):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0"
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        price_element = soup.find("span", class_="components-TicketPrice-TicketPrice-module__suffix")
        if price_element is None:
            raise ValueError("找不到票價資訊")

        price_text = price_element.find_parent("span").text.strip()
        return float(price_text.replace("$", "").replace(",", "").replace("/ea", ""))
    except Exception as e:
        print(f"抓取票價錯誤：{e}")
        return None

def send_email(subject, body):
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = TO_EMAIL
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)
        print("📧 郵件發送成功")
    except Exception as e:
        print(f"發送郵件錯誤：{e}")

def get_lowest_price(sheet):
    try:
        lowest_price = sheet.acell("A1").value
        if lowest_price is None:
            return None
        return float(lowest_price)
    except Exception as e:
        print(f"讀取錯誤：{e}")
        return None


def write_to_google_sheet(price):
    try:
        sheet.update("A1", [[price]])
        print("成功寫入到 Google Sheets")
    except Exception as e:
        print(f"寫入 Google Sheets 錯誤：{e}")

if __name__ == "__main__":
    try:
        price = get_ticket_price(URL)
        if price is not None:
            print(f"目前票價：${price}")
     
            scope = [
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive"
            ]
            google_creds_json = os.environ.get("GOOGLE_CREDENTIALS_JSON")
            creds_dict = json.loads(google_creds_json)
            creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
            client = gspread.authorize(creds)
            sheet = client.open(SPREADSHEET_NAME).sheet1
            
            # 讀取最低價
            lowest_price = get_lowest_price(sheet)

            if lowest_price is None or price < lowest_price:
                write_to_google_sheet(price)
                print(f"📉 新低價：${price}")
                subject = "票價下跌通知"
                body = f"目前票價為 ${price}。\n網址：{URL}"
                send_email(subject, body)
            elif price > lowest_price:
                write_to_google_sheet(price)
                print(f"📈 票價上漲 ${price}")
                subject = "票價上漲通知"
                body = f"目前票價為 ${price}。\n網址：{URL}"
                send_email(subject, body)
            else:
                print(f"價格持平 ${lowest_price}")
        else:
            print("❌ 抓取票價失敗")
    except Exception as e:
        print(f"執行錯誤：{e}")
