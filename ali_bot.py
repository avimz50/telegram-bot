import csv
import os
import requests
from bs4 import BeautifulSoup
import telebot

# Load environment variable for bot token
BOT_TOKEN = os.getenv('BOT_TOKEN')
print("BOT_TOKEN loaded:", bool(BOT_TOKEN))

bot = telebot.TeleBot(BOT_TOKEN)

CSV_URL = 'https://raw.githubusercontent.com/avimz30/telegram-bot/main/products.csv'
POSTED_LINKS_FILE = 'posted_links.txt'
CHANNEL_ID = '@smartlego_israel'

def get_unposted_products():
    posted_links = set()
    if os.path.exists(POSTED_LINKS_FILE):
        with open(POSTED_LINKS_FILE, 'r') as f:
            posted_links = set(line.strip() for line in f)

    response = requests.get(CSV_URL)
    response.encoding = 'utf-8'
    lines = response.text.splitlines()
    reader = csv.reader(lines)
    unposted = []

    for row in reader:
        if len(row) >= 2:
            original_link, affiliate_link = row
            if affiliate_link not in posted_links:
                unposted.append((original_link.strip(), affiliate_link.strip()))
    return unposted

def save_posted_link(link):
    with open(POSTED_LINKS_FILE, 'a') as f:
        f.write(link + '\n')

def get_product_details(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')

        title = soup.title.string.strip() if soup.title else "מוצר מאלי אקספרס"
        
        # ניסיון לשלוף תמונה ראשית
        image = ''
        og_image = soup.find('meta', property='og:image')
        if og_image:
            image = og_image.get('content', '')

        return title, image
    except Exception as e:
        print("Error fetching details:", e)
        return "מוצר מאלי אקספרס", ''

def generate_marketing_text(product_name: str, price: str = None) -> str:
    name = product_name.lower()
    description_parts = []

    if "lego" in name:
        description_parts.append("סט לגו מרהיב להרכבה מהנה ופיתוח חשיבה יצירתית!")
    elif "robot" in name or "robotic" in name:
        description_parts.append("רובוט חכם – צעצוע טכנולוגי שילדים פשוט אוהבים!")
    elif "watch" in name or "smartwatch" in name:
        description_parts.append("שעון חכם בעיצוב מודרני עם תכונות מתקדמות.")
    elif "rc" in name or "remote control" in name:
        description_parts.append("מוצר על שלט רחוק – כיף בלתי נגמר לילדים ומבוגרים!")
    elif "lamp" in name or "light" in name:
        description_parts.append("תאורה מהממת שתשדרג כל חדר בבית.")
    elif "car" in name and "toy" in name:
        description_parts.append("מכונית צעצוע איכותית ומרגשת לילדים שאוהבים מהירות!")
    elif "car" in name and ("holder" in name or "mount" in name):
        description_parts.append("מתקן איכותי לטלפון לרכב – יציב, נוח ומעוצב!")
    elif "phone holder" in name:
        description_parts.append("מתקן חכם לטלפון – מתאים לרכב ולמשרד!")
    elif "headphone" in name or "earbuds" in name:
        description_parts.append("אוזניות איכותיות לצליל נקי בכל מצב.")
    elif "camera" in name:
        description_parts.append("מצלמה איכותית ללכידת כל רגע חשוב.")
    else:
        description_parts.append("מוצר חם עכשיו באלי אקספרס – שווה הצצה!")

    if price:
        description_parts.append(f"💰 רק ב-{price}!")

    description_parts.append("📦 משלוח מהיר לישראל ✔️")
    description_parts.append("🔥 אל תפספסו – זה הזמן להתחדש במחיר שווה!")

    return "\n".join(description_parts)

def post_to_telegram(title, image_url, affiliate_link, description):
    try:
        caption = f"🛒 *{title}*\n\n{description}\n\n[קנה עכשיו]({affiliate_link})"
        bot.send_photo(CHANNEL_ID, photo=image_url, caption=caption, parse_mode='Markdown')
        print("Posted to Telegram:", title)
    except Exception as e:
        print("Failed to post:", e)

def main():
    products = get_unposted_products()
    if not products:
        print("No new products to post.")
        return

    for original_link, affiliate_link in products:
        title, image_url = get_product_details(original_link)
        description = generate_marketing_text(title)
        if image_url:
            post_to_telegram(title, image_url, affiliate_link, description)
            save_posted_link(affiliate_link)
            break  # פרסם מוצר אחד בכל הרצה
        else:
            print("No image found, skipping.")

if __name__ == '__main__':
    main()
