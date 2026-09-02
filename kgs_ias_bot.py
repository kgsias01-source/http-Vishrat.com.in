import os
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes


BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN environment variable is missing.")


# Render ke liye simple HTTP server
class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running")

    def log_message(self, format, *args):
        return


def run_health_server():
    port = int(os.getenv("PORT", "10000"))
    server = ThreadingHTTPServer(("0.0.0.0", port), HealthHandler)
    server.serve_forever()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🌐 Vishrat.com.in", url="https://vishrat.com.in")],
        [InlineKeyboardButton("📲 Telegram Bot", url="https://t.me/KGS_IAS_OFFICIAL_BOT")],
        [InlineKeyboardButton("📚 Courses / Notes", callback_data="courses")],
    ]

    await update.message.reply_text(
        "🌟 Welcome to KGS IAS Official Bot!\n\n"
        "यहाँ आपको KGS IAS से जुड़ी जानकारी, courses और study resources मिलेंगे।\n\n"
        "नीचे दिए options में से चुनें:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "ℹ️ Help\n\n"
        "/start - Bot शुरू करें\n"
        "/help - Help देखें"
    )


async def courses(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    await query.message.reply_text(
        "📚 Courses / Notes\n\n"
        "अपने courses, notes या channel links यहाँ add कर सकते हैं।"
    )


def main():
    # Render ko port dikhane ke liye server start
    threading.Thread(target=run_health_server, daemon=True).start()

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("courses", courses))

    app.run_polling()


if __name__ == "__main__":
    main()
