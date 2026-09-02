import os
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN environment variable is missing.")


# ---------------- HEALTH SERVER FOR RENDER ----------------

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"KGS IAS Bot is running!")

    def log_message(self, format, *args):
        return


def run_health_server():
    port = int(os.getenv("PORT", "10000"))
    server = ThreadingHTTPServer(("0.0.0.0", port), HealthHandler)
    server.serve_forever()


# ---------------- START COMMAND ----------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    keyboard = [
        [
            InlineKeyboardButton(
                "🌐 Vishrat.com.in",
                url="https://vishrat.com.in"
            )
        ],
        [
            InlineKeyboardButton(
                "📲 Telegram Bot",
                url="https://t.me/KGS_IAS_OFFICIAL_BOT"
            )
        ],
        [
            InlineKeyboardButton(
                "📚 Courses / Notes",
                callback_data="courses"
            )
        ],
    ]

    await update.message.reply_text(
        "🌟 Welcome to KGS IAS Official Bot!\n\n"
        "यहाँ आपको KGS IAS से जुड़ी जानकारी,\n"
        "courses और study resources मिलेंगे।\n\n"
        "नीचे दिए options में से चुनें:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# ---------------- COURSES MENU ----------------

async def courses_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    keyboard = [
        [
            InlineKeyboardButton(
                "🏛️ UPSC Course",
                callback_data="upsc"
            )
        ],
        [
            InlineKeyboardButton(
                "📚 NCERT Course",
                callback_data="ncert"
            )
        ],
        [
            InlineKeyboardButton(
                "📖 Study Material",
                callback_data="material"
            )
        ],
        [
            InlineKeyboardButton(
                "📰 Current Affairs",
                callback_data="current"
            )
        ],
        [
            InlineKeyboardButton(
                "📝 Test Series",
                callback_data="test"
            )
        ],
        [
            InlineKeyboardButton(
                "🔙 Back",
                callback_data="back"
            )
        ],
    ]

    await query.edit_message_text(
        "📚 KGS IAS Study Resources\n\n"
        "नीचे दिए गए option में से चुनें:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# ---------------- STUDY OPTIONS ----------------

async def study_option(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    option = query.data

    if option == "upsc":
        text = (
            "🏛️ UPSC Course\n\n"
            "UPSC Civil Services की तैयारी के लिए "
            "यहाँ courses और study resources उपलब्ध होंगे।\n\n"
            "🔗 Course link जल्द जोड़ा जाएगा।"
        )

    elif option == "ncert":
        text = (
            "📚 NCERT Course\n\n"
            "Class 6 से 12 तक की NCERT आधारित "
            "study सामग्री यहाँ उपलब्ध होगी।\n\n"
            "🔗 NCERT resources जल्द जोड़े जाएंगे।"
        )

    elif option == "material":
        text = (
            "📖 Study Material\n\n"
            "UPSC preparation के लिए notes, PDFs और "
            "अन्य study material यहाँ मिलेगा।\n\n"
            "📂 Study material जल्द जोड़ा जाएगा।"
        )

    elif option == "current":
        text = (
            "📰 Current Affairs\n\n"
            "Daily और Monthly Current Affairs "
            "यहाँ उपलब्ध कराए जाएंगे।\n\n"
            "🗞️ Current Affairs resources जल्द जोड़े जाएंगे।"
        )

    elif option == "test":
        text = (
            "📝 Test Series\n\n"
            "UPSC preparation के लिए test series और "
            "practice questions यहाँ मिलेंगे।\n\n"
            "📝 Test Series जल्द जोड़ी जाएगी।"
        )

    else:
        return

    keyboard = [
        [
            InlineKeyboardButton(
                "🔙 Back to Courses",
                callback_data="courses"
            )
        ]
    ]

    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# ---------------- BACK TO HOME ----------------

async def back_home(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    keyboard = [
        [
            InlineKeyboardButton(
                "🌐 Vishrat.com.in",
                url="https://vishrat.com.in"
            )
        ],
        [
            InlineKeyboardButton(
                "📲 Telegram Bot",
                url="https://t.me/KGS_IAS_OFFICIAL_BOT"
            )
        ],
        [
            InlineKeyboardButton(
                "📚 Courses / Notes",
                callback_data="courses"
            )
        ],
    ]

    await query.edit_message_text(
        "🌟 KGS IAS Official Bot\n\n"
        "Study और UPSC preparation से जुड़ी "
        "जानकारी के लिए नीचे दिए options चुनें:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# ---------------- HELP ----------------

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "ℹ️ Help\n\n"
        "/start - Bot शुरू करें\n"
        "/help - Help देखें"
    )


# ---------------- MAIN ----------------

def main():

    # Render health server
    threading.Thread(
        target=run_health_server,
        daemon=True
    ).start()

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))

    # Courses button
    app.add_handler(
        CallbackQueryHandler(
            courses_menu,
            pattern="^courses$"
        )
    )

    # Study options
    app.add_handler(
        CallbackQueryHandler(
            study_option,
            pattern="^(upsc|ncert|material|current|test)$"
        )
    )

    # Back button
    app.add_handler(
        CallbackQueryHandler(
            back_home,
            pattern="^back$"
        )
    )

    app.run_polling()


if __name__ == "__main__":
    main()
