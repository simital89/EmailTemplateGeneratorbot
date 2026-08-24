import os
import sys
import time
import requests

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TOKEN:
    sys.exit(1)

API_URL = f"https://api.telegram.org/bot{TOKEN}"
user_templates = {}

def send_msg(chat_id, text, reply_markup=None):
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    if reply_markup:
        payload["reply_markup"] = reply_markup
    try:
        requests.post(f"{API_URL}/sendMessage", json=payload, timeout=10)
    except Exception:
        pass

def generate_html(style, title, body, cta_text="", cta_url=""):
    cta = ""
    if cta_text and cta_url:
        cta = f'<tr><td align="center" style="padding:20px 0;"><a href="{cta_url}" style="background-color:#007bff;color:#ffffff;padding:12px 24px;text-decoration:none;border-radius:5px;font-weight:bold;display:inline-block;">{cta_text}</a></td></tr>'
    
    bg = "#f4f4f7" if style == "promo" else "#ffffff"
    return f'<!DOCTYPE html><html><body style="margin:0;padding:20px;background-color:{bg};font-family:Arial,sans-serif;"><table align="center" border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width:600px;background-color:#ffffff;border:1px solid #dddddd;border-radius:8px;padding:20px;"><tr><td style="font-size:24px;font-weight:bold;color:#333333;padding-bottom:15px;border-bottom:2px solid #007bff;">{title}</td></tr><tr><td style="padding:20px 0;color:#555555;font-size:16px;line-height:1.6;">{body}</td></tr>{cta}</table></body></html>'

def main():
    offset = 0
    while True:
        try:
            res = requests.get(f"{API_URL}/getUpdates", params={"offset": offset, "timeout": 20}, timeout=25)
            if res.status_code == 200:
                data = res.json()
                for update in data.get("result", []):
                    offset = update["update_id"] + 1
                    
                    if "message" in update and "text" in update["message"]:
                        chat_id = update["message"]["chat"]["id"]
                        text = update["message"]["text"].strip()
                        
                        if text == "/start":
                            keyboard = {"inline_keyboard": [[{"text": "📢 Promotional", "callback_data": "promo"}], [{"text": "✉️ Simple Outreach", "callback_data": "simple"}]]}
                            send_msg(chat_id, "Choose a template style:", keyboard)
                        elif "|" in text:
                            parts = [p.strip() for p in text.split("|")]
                            title = parts[0]
                            body = parts[1] if len(parts) > 1 else ""
                            cta_text = parts[2] if len(parts) > 2 else ""
                            cta_url = parts[3] if len(parts) > 3 else ""
                            style = user_templates.get(chat_id, "simple")
                            
                            html = generate_html(style, title, body, cta_text, cta_url)
                            send_msg(chat_id, "Here is your HTML:")
                            send_msg(chat_id, f"<pre>{html}</pre>")
                        else:
                            send_msg(chat_id, "Send text as:\n<code>Title | Body | Button Text | Button Link</code>")
                            
                    elif "callback_query" in update:
                        chat_id = update["callback_query"]["message"]["chat"]["id"]
                        user_templates[chat_id] = update["callback_query"]["data"]
                        send_msg(chat_id, "Style saved! Now send your details like this:\n\n<code>Title | Body | Button Text | Button Link</code>")
        except Exception:
            time.sleep(3)

if __name__ == "__main__":
    main()
