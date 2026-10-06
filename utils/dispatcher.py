import os
import requests

try:
    from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
except ImportError:
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def _dispatch_chunk(chunk: str, bot_token: str, chat_id: str) -> bool:
    """Helper to transmit a single message block with Markdown parse-safety."""
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": chunk,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True
    }
    
    try:
        response = requests.post(url, json=payload, timeout=15)
        
        # Fallback if markdown parsing fails due to unescaped characters in text
        if response.status_code == 400 and "can't parse entities" in response.text.lower():
            payload.pop("parse_mode")
            response = requests.post(url, json=payload, timeout=15)

        if response.status_code == 200:
            return True
        else:
            print(f"[!] Telegram API Failed: {response.text}")
            return False
    except Exception as e:
        print(f"[!] Network error: {e}")
        return False

def send_telegram_message(body_text: str) -> bool:
    """
    Transmits alert text directly to Telegram.
    Automatically chunks payloads exceeding Telegram's 4,096-character limit.
    """
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN", TELEGRAM_BOT_TOKEN)
    chat_id = os.getenv("TELEGRAM_CHAT_ID", TELEGRAM_CHAT_ID)
    
    if not body_text or not body_text.strip():
        return False

    max_chunk = 4000
    if len(body_text) <= max_chunk:
        success = _dispatch_chunk(body_text, bot_token, chat_id)
        if success:
            print("[+] Successfully sent alert to Telegram!")
        return success

    all_success = True
    start = 0
    while start < len(body_text):
        chunk = body_text[start:start + max_chunk]
        if not _dispatch_chunk(chunk, bot_token, chat_id):
            all_success = False
        start += max_chunk

    if all_success:
        print("[+] Successfully sent split alert to Telegram!")
    return all_success
