import os
import random
import telebot
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup


# קבלת הטוקן מה-Environment Variable והדפסת בדיקה
BOT_TOKEN = os.getenv('BOT_TOKEN')
if BOT_TOKEN:
    BOT_TOKEN = BOT_TOKEN.strip()
else:
    raise ValueError("ERROR: BOT_TOKEN not found in environment variables")

CHANNEL_ID = '@smartlego_israel'
CSV_FILE = 'products.csv'

bot = telebot.TeleBot(BOT_TOKEN)

def fetch_product_details_selenium(url):
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')

    service = Service(CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=options)

    try:
        driver.get(url)
        # מחכים לכותרת המוצר או ל-meta og:title (עד 20 שניות)
        WebDriverWait(driver, 20).until(
            EC.any_of(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'h1.product-title-text')),
                EC.presence_of_element_located((By.CSS_SELECTOR, 'meta[property="og:title"]'))
            )
        )

        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # כותרת מוצר
        og_title_tag = soup.find("meta", property="og:title")
        if og_title_tag and og_title_tag.get("content"):
            title = og_title_tag["content"].strip()
            if " - AliExpress" in title:
                title = title.split(" - AliExpress")[0].strip()
        else:
            h1 = soup.find("h1", class_="product-title-text")
            title = h1.text.strip() if h1 else "מוצר מאלי אקספרס"

        # תמונה ראשית
        og_image_tag = soup.find("meta", property="og:image")
        image_url = og_image_tag["content"] if og_image_tag else None

        # מחירים אפשריים - מנסים כמה סלקטורים עם Selenium
        price = None
        price_selectors = [
            'span.product-price-value',
            'div.product-price-current',
            'span.uniform-banner-box-price',
            'div.product-price',
            'div.price-item span.amount',
            'div.current-price span.value'
        ]
        for selector in price_selectors:
            try:
                elem = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                price_text = elem.text.strip()
                if price_text and len(price_text) > 2:
                    price = price_text
                    break
            except:
                continue

        return title, image_url, price

    finally:
        driver.quit()


def generate_marketing_text(title, price=None):
    text = f"🔥 {title} 🔥\n\n"
    if price:
        text += f"💰 מחיר: {price}\n\n"

    # תיאור מותאם מילים מתוך הכותרת
    lower_title = title.lower()
    if "lego" in lower_title:
        text += "סט לגו מדהים להרכבה ולפיתוח יצירתיות!\n"
    elif "robot" in lower_title or "robotic" in lower_title:
        text += "רובוט חכם לילדים שאוהבים טכנולוגיה ומשחקים חכמים!\n"
    elif "watch" in lower_title or "smartwatch" in lower_title:
        text += "שעון חכם מתקדם עם פונקציות מגניבות.\n"
    elif "lamp" in lower_title or "light" in lower_title:
        text += "תאורה ייחודית שתוסיף אווירה לכל חדר.\n"
    else:
        text += "מוצר איכותי וחדש מאלי אקספרס – אל תפספסו!\n"

    text += "\n📦 משלוח מהיר לישראל!\n🔥 קנייה חכמה עם קישור שותפים.\n"
    return text


if __name__ == "__main__":
    CSV_FILE = 'products.csv'

    import csv
    with open(CSV_FILE, newline='', encoding='utf-8') as csvfile:
        reader = list(csv.DictReader(csvfile))
        product = random.choice(reader)
        product_url = product['product_url']
        affiliate_link = product['affiliate_link']

        title, image_url, price = fetch_product_details_selenium(product_url)
        marketing_text = generate_marketing_text(title, price)
        message = f"{marketing_text}\n🔗 להזמנה: {affiliate_link}"

        if image_url:
            bot.send_photo(CHANNEL_ID, image_url, caption=message)
        else:
            bot.send_message(CHANNEL_ID, message)
