import os
import csv
import random
import telebot
import requests
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# קבלת טוקן ונתיב chromedriver מהסביבה
BOT_TOKEN = os.getenv('BOT_TOKEN')
if BOT_TOKEN:
    BOT_TOKEN = BOT_TOKEN.strip()
else:
    raise ValueError("ERROR: BOT_TOKEN not found in environment variables")

CHROMEDRIVER_PATH = os.getenv('CHROMEDRIVER_PATH')
if not CHROMEDRIVER_PATH:
    raise ValueError("ERROR: CHROMEDRIVER_PATH not found in environment variables")

CHANNEL_ID = '@smartlego_israel'
CSV_FILE = 'products.csv'

bot = telebot.TeleBot(BOT_TOKEN)


def generate_marketing_text(product_name: str, price: str | None = None) -> str:
    name = product_name.lower()
    description_parts = []

    if "lego" in name:
        description_parts.append("סט לגו מרהיב להרכבה מהנה ופיתוח חשיבה יצירתית!")
    elif "robot" in name or "robotic" in na
