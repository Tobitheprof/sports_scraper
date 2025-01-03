import os
import logging
import requests

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "8084219997:AAFG3_uGNP-UjvFpsN_W1CN45g8ntw3ZVUM")  # or configure in settings.py
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "-1002342442974")

def send_telegram_alert(title, url, source, date, matched_keywords):
    """
    Sends a Telegram message to a pre-defined chat/group.
    """
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        logging.warning("Telegram token or chat ID not set. Skipping alert.")
        return

    base_api_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

    # Build message
    matched_part = ""
    if matched_keywords:
        matched_part = f"Matched: {', '.join(matched_keywords)}\n"
    
    message_text = (
        f"**New Article Found**\n\n"
        f"**Title**: {title}\n"
        f"**URL**: {url}\n"
        f"**Source**: {source}\n"
        f"**Date**: {date}\n"
        f"{matched_part}"
    )

    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message_text,
        "parse_mode": "Markdown"
    }

    try:
        resp = requests.post(base_api_url, data=payload)
        if resp.status_code != 200:
            logging.error(f"Failed to send Telegram alert: {resp.text}")
        else:
            logging.info("Telegram alert sent successfully.")
    except Exception as ex:
        logging.error(f"Exception sending Telegram alert: {ex}")
