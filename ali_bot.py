import os
import csv
import random
import requests
from bs4 import BeautifulSoup
import telebot

# קבלת הטוקן מה-Environment Variable והדפסת בדיקה
BOT_TOKEN = os.getenv('BOT_TOKEN')
if BOT_TOKEN:
    BOT_TOKEN = BOT_TOKEN.strip()
else:
    raise ValueError("ERROR: BOT_TOKEN not found in environment variables")

CHANNEL_ID = '@smartlego_israel'
CSV_FILE = 'products.csv'

bot = telebot.TeleBot(BOT_TOKEN)

# פונקציה ליצירת תיאור שיווקי מגוון עם מחיר (אם יש)
def generate_marketing_text(title, price=None):
    price_text = f"💰 מחיר משתלם: {price}" if price else "💰 מחיר משתלם!"
    marketing_texts = [
        f"🔥 {title} - הזדמנות שלא כדאי לפספס!\n{price_text}\n🚀 איכות מובטחת ושירות מהיר.",
        f"✨ {title} עכשיו במחיר מיוחד!\n{price_text}\n🎁 מושלם עבורך או כמתנה.",
        f"🎉 {title} – הטוב ביותר בשוק!\n{price_text}\n📦 משלוח מהיר ואמין.",
        f"🎯 רוצה איכות במחיר מעולה? {title} כאן בשבילך!\n{price_text}\n✅ אל תחמיץ את ההזדמנות.",
        f"🔥 מוצר מומלץ: {title}\n{price_text}\n🎁 מתאים לכל בית ולכל שימוש."
    ]
    return random.choice(marketing_texts) + "\n\n💥 הזמינו עכשיו לפני שייגמר המלאי!"

# פונקציה לשליפת שם המוצר, תמונה ומחיר מהדף
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

    # ניסיון לשלוף מחיר בכמה דרכים שונות
    price_selectors = [
        {'name': 'class', 'value': 'product-price-value'},
        {'name': 'class', 'value': 'price-current'},
        {'name': 'id', 'value': 'j-sku-discount-price'},
        # ניתן להוסיף עוד selectors אם צריך
    ]

    price = None
    for selector in price_selectors:
        if selector['name'] == 'class':
            tag = soup.find(class_=selector['value'])
        elif selector['name'] == 'id':
            tag = soup.find(id=selector['value'])
        else:
            tag = None

        if tag:
            price = tag.get_text(strip=True)
            if price:
                break

    return title, image_url, price

# טעינת מוצרים מקובץ והפצה בטלגרם
with open(CSV_FILE, newline='', encoding='utf-8') as csvfile:
    reader = list(csv.DictReader(csvfile))
    product = random.choice(reader)
    product_url = product['product_url']
    affiliate_link = product['affiliate_link']

    title, image_url, price = fetch_product_details(product_url)
    description = generate_marketing_text(title, price)
    message = f"{description}\n🔗 להזמנה: {affiliate_link}"

    if image_url:
        bot.send_photo(CHANNEL_ID, image_url, caption=message)
    else:
        bot.send_message(CHANNEL_ID, message)
