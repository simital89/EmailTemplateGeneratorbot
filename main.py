import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

def build_template(template_type: str, title: str, body: str, cta_text: str = "", cta_url: str = "") -> str:
    cta_html = ""
    if cta_text and cta_url:
        cta_html = f'''
        <tr>
            <td align="center" style="padding: 20px 0;">
                <a href="{cta_url}" style="background-color: #007bff; color: #ffffff; padding: 12px 24px; text-decoration: none; border-radius: 5px; font-weight: bold; display: inline-block;">{cta_text}</a>
            </td>
        </tr>
        '''

    bg_color = "#f4f4f7" if template_type == "promo" else "#ffffff"
    
    html = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
</head>
<body style="margin: 0; padding: 20px; background-color: {bg_color}; font-family: Arial, sans-serif;">
    <table align="center" border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width: 600px; background-color: #ffffff; border: 1px solid #dddddd; border-radius: 8px; padding: 20px;">
        <tr>
            <td style="font-size: 24px; font-weight: bold; color: #333333; padding-bottom: 15px; border-bottom: 2px solid #007bff;">
                {title}
            </td>
        </tr>
        <tr>
            <td style="padding: 20px 0; color: #555555; font-size: 16px; line-height: 1.6;">
                {body}
            </td>
        </tr>
        {cta_html}
        <tr>
            <td align="center" style="padding-top: 20px; border-top: 1px solid #eeeeee; font-size: 12px; color: #aaaaaa;">
                Sent via Email Template Generator
            </td>
        </tr>
    </table>
</body>
</html>'''
    return html

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📢 Promotional Email", callback_data="tmpl_promo")],
        [InlineKeyboardButton("📰 Newsletter Email", callback_data="tmpl_news")],
        [InlineKeyboardButton("✉️ Simple Outreach", callback_data="tmpl_simple")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Welcome to **Email Template Generator**!\n\nSelect a template layout to get started:",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    template_type = query.data.replace("tmpl_", "")
    context.user_data["template_type"] = template_type
    
    await query.edit_message_text(
        "Great! Send your content in this format:\n\n"
        "`Title | Main Body | Button Text | Button URL`\n\n"
        "**Example:**\n"
        "`Exclusive Offer | Get 20% off all plans today! | Claim Discount | https://example.com`",
        parse_mode="Markdown"
    )

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    parts = [p.strip() for p in user_text.split("|")]
    
    if len(parts) < 2:
        await update.message.reply_text(
            "⚠️ Please use the correct format:\n`Title | Main Body | Button Text | Button URL`",
            parse_mode="Markdown"
        )
        return
        
    title = parts[0]
    body = parts[1]
    cta_text = parts[2] if len(parts) > 2 else ""
    cta_url = parts[3] if len(parts) > 3 else ""
    
    template_type = context.user_data.get("template_type", "simple")
    
    html_output = build_template(template_type, title, body, cta_text, cta_url)
    
    await update.message.reply_text("Here is your HTML Email Template:")
    await update.message.reply_text(f"```html\n{html_output}\n```", parse_mode="Markdown")

def main():
    if not TOKEN:
        raise ValueError("TELEGRAM_BOT_TOKEN environment variable is missing!")
        
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    logger.info("Bot starting...")
    app.run_polling()

if __name__ == "__main__":
    main()
