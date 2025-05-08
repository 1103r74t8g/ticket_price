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

# 目標網站的 URL
URL = "https://gametime.co/concert/ado-tickets/7-29-2025-baltimore-md-cfg-bank-arena/events/671b084afb59e4425bdc20c0"

LOWEST_PRICE_FILE = "lowest_price.txt"

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

def get_lowest_price():
    """
    從檔案中讀取最低價格
    """
    if os.path.exists(LOWEST_PRICE_FILE):
        with open(LOWEST_PRICE_FILE, "r") as file:
            try:
                return float(file.read().strip())
            except ValueError:
                return None
    return None


def save_lowest_price(price):
    """
    將最低價格儲存到檔案
    """
    with open(LOWEST_PRICE_FILE, "w") as file:
        file.write(str(price))


if __name__ == "__main__":
    try:
        # 抓取網站的票價
        price = get_ticket_price(URL)
        if price is not None:
            print(f"網站的票價為：${price}")

            # 讀取最低價格
            lowest_price = get_lowest_price()
            if lowest_price is None or price < lowest_price:
                # 更新最低價格並發送通知
                save_lowest_price(price)
                print(f"發現新低價：${price}")
                subject = "票價創新低通知"
                body = f"目前網站的票價為 ${price}，創新低！請前往查看：{URL}"
                send_email(subject, body)
            else:
                print(f"目前票價 ${price} 未低於最低價格 ${lowest_price}")
        else:
            print("抓取網站的票價失敗")
    except Exception as e:
        print(f"程式執行時發生錯誤：{e}")
