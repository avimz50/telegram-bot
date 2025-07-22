import os
import csv
import random
import requests
from bs4 import BeautifulSoup
import telebot

# קבלת הטוקן מה-Environment Variable והדפסת בדיקה
BOT_TOKEN = "7885672101:AAFe53N-viS2lfDNhHvj0TWqlMIv7OvrDiQ"

print(f"BOT_TOKEN loaded: {BOT_TOKEN is not None}")
if BOT_TOKEN:
    print(f"BOT_TOKEN partial: {BOT_TOKEN[:10]}...")  # מציג רק חלק מהטוקן לשמירה על סודיות
else:
    raise ValueError("ERROR: BOT_TOKEN not found in environment variables")

CHANNEL_ID = '@smartlego_israel'
CSV_FILE = 'products.csv'

bot = telebot.TeleBot(BOT_TOKEN)

# פונקציה ליצירת תיאור שיווקי קצר
def generate_marketing_text(title):
    return f"""🔥 {title} 🔥

מוצר איכותי במחיר משתלם במיוחד!
🚀 מתאים לכל אחד – פשוט ונוח
🎁 אידיאלי כמתנה או שימוש יומיומי

💥 אל תפספסו – מלאי מוגבל! 💥
"""

# פונקציה לשליפת שם המוצר והתמונה מהדף
def fetch_product_details(url):
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    # שליפת כותרת
    title_tag = soup.find('title')
    title = title_tag.get_text(strip=True).split('|')[0] if title_tag else 'מוצר מאלי אקספרס'

    # שליפת תמונה ראשית
    image_tag = soup.find('meta', property='og:image')
    image_url = image_tag['content'] if image_tag else None

    return title, image_url

# טעינת מוצרים מקובץ
# טעינת מוצרים מקובץ
with open(CSV_FILE, newline='', encoding='utf-8') as csvfile:
    reader = list(csv.DictReader(csvfile))
    product = random.choice(reader)
    product_url = product['product_url']
    affiliate_link = product['affiliate_link']

    title, image_url = fetch_product_details(product_url)
    description = generate_marketing_text(title)
    message = f"{description}\n🔗 להזמנה: {affiliate_link}"

    if image_url:
        bot.send_photo(CHANNEL_ID, image_url, caption=message)
    else:
        bot.send_message(CHANNEL_ID, message)
