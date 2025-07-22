import os
import csv
import random
import requests
from bs4 import BeautifulSoup
import telebot

# קבלת הטוקן מהסביבה
BOT_TOKEN = os.getenv('BOT_TOKEN')
if BOT_TOKEN:
    BOT_TOKEN = BOT_TOKEN.strip()
else:
    raise ValueError("ERROR: BOT_TOKEN not found in environment variables")

CHANNEL_ID = '@smartlego_israel'
CSV_FILE = 'products.csv'

bot = telebot.TeleBot(BOT_TOKEN)

# פונקציה ליצירת תיאור שיווקי לפי שם ומחיר
def generate_marketing_text(product_name: str, price: str = None) -> str:
    name = product_name.lower()
    description_parts = []

    if "lego" in name:
        description_parts.append("🧱 סט לגו מדהים לבנייה יצירתית!")
    elif "robot" in name or "robotic" in name:
        description_parts.append("🤖 רובוט חכם – צעצוע טכנולוגי שילדים פשוט אוהבים!")
    elif "watch" in name or "smartwatch" in name:
        description_parts.append("⌚ שעון חכם בעיצוב מודרני עם פונקציות מתקדמות.")
    elif "rc" in name or "remote control" in name:
        description_parts.append("🚗 שלט רחוק – כיף אינסופי לילדים!")
    elif "lamp" in name or "light" in name:
        description_parts.append("💡 תאורה מדליקה שמשדרגת כל חדר.")
    elif "car" in name and "toy" in name:
        description_parts.append("🏎️ מכונית צעצוע מדהימה לילדים שאוהבים מהירות!")
    elif "headphone" in name or "earbuds" in name:
        description_parts.append("🎧 אוזניות איכותיות לצליל חד ומדויק.")
    elif "camera" in name:
        description_parts.append("📷 מצלמה מושלמת לתיעוד רגעים יפים.")
    else:
        description_parts.append("✨ מוצר לוהט מאלי אקספרס – כדאי לבדוק!")

    if price:
        description_parts.append(f"💰 מחיר: {price}")

    description_parts.append("📦 משלוח מהיר לישראל ✔️")
    description_parts.append("🔥 קנייה חכמה עם קישור שותפים – אל תפספסו!")

    return "\n".join(description_parts)

# פונקציה לשליפת שם מוצר, תמונה ומחיר מהעמוד
def fetch_product_details(url):
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    # שליפת כותרת
    title_tag = soup.find('title')
    title = title_tag.get_text(strip=True).split('|')[0] if title_tag else 'מוצר מאלי אקספרס'

    # שליפת תמונה
    image_tag = soup.find('meta', property='og:image')
    image_url = image_tag['content'] if image_tag else None

    # שליפת מחיר
    price = None
    selectors = [
        {'name': 'class', 'value': 'product-price-value'},
        {'name': 'class', 'value': 'price-current'},
        {'name': 'id', 'value': 'j-sku-discount-price'},
    ]
    for selector in selectors:
        tag = soup.find(**{selector['name']: selector['value']})
        if tag and tag.get_text(strip=True):
            price = tag.get_text(strip=True)
            break

    return title, image_url, price

# טעינת קובץ CSV ובחירת מוצר אקראי
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
