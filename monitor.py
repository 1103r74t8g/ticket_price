import os
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

# 配置參數
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")  # 從環境變數讀取
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")  # 從環境變數讀取
TO_EMAIL = "willy110439@gmail.com" # 收件人電子郵件地址

# 定義網站的 URL
URL = "https://gametime.co/concert/ado-tickets/7-29-2025-baltimore-md-cfg-bank-arena/events/671b084afb59e4425bdc20c0"


def get_ticket_price(url):
    """
    從網站獲取票價
    """
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36"
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # 針對網站的 HTML 結構
        price_element = soup.find("span", class_="components-TicketPrice-TicketPrice-module__suffix")
        if price_element is None:
            raise ValueError("無法找到票價資訊，請檢查 HTML 結構或選擇器")
        
        price_text = price_element.find_parent("span").text.strip()
        return float(price_text.replace("$", "").replace(",", "").replace("/ea", ""))
    except Exception as e:
        print(f"抓取票價時發生錯誤：{e}")
        return None

def send_email(subject, body):
    """
    發送電子郵件
    """
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
        print("電子郵件已成功發送！")
    except Exception as e:
        print(f"發送電子郵件時發生錯誤：{e}")

if __name__ == "__main__":
    try:
        # 抓取網站的票價
        price = get_ticket_price(URL)
        if price is not None:
            print(f"網站的票價為：${price}")

            # 發送電子郵件通知
            subject = "票價通知"
            body = f"目前網站的票價為 ${price}，請前往查看：{URL}"
            send_email(subject, body)
        else:
            print("抓取網站的票價失敗")
    except Exception as e:
        print(f"程式執行時發生錯誤：{e}")
