import os
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 8604692393

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
                "🎓 Paid Course",
                callback_data="paid_course"
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


# ---------------- PAID COURSE ----------------

async def paid_course(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    text = (
        "🎓 Paid Course\n\n"
        "5 free lectures के बाद हर lecture की कीमत ₹5 है।\n\n"
        "💳 Payment के लिए UPI ID:\n"
        "respect-girls@ybl\n\n"
        "Payment के बाद UTR / Transaction ID और "
        "screenshot verification के लिए भेजें।"
    )

    keyboard = [
        [
            InlineKeyboardButton(
                "🌐 Open Website",
                url="https://vishrat.com.in"
            )
        ],
        [
            InlineKeyboardButton(
                "⬅️ Back to Courses",
                callback_data="courses"
            )
        ]
    ]

    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    context.user_data["payment_waiting"] = True


# ---------------- PAYMENT VERIFICATION ----------------

async def payment_message(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not context.user_data.get("payment_waiting"):
        return

    user = update.effective_user

    # UTR / Transaction ID
    if update.message.text:

        utr = update.message.text.strip()

        if len(utr) < 4:
            await update.message.reply_text(
                "❌ कृपया सही UTR / Transaction ID भेजें।"
            )
            return

        context.user_data["utr"] = utr

        await update.message.reply_text(
            "✅ UTR प्राप्त हो गया।\n\n"
            "अब कृपया payment का screenshot भेजें 📸"
        )
        return

    # Payment Screenshot
    if update.message.photo:

        utr = context.user_data.get("utr")

        if not utr:
            await update.message.reply_text(
                "❌ पहले अपना UTR / Transaction ID भेजें।"
            )
            return

        caption = (
            "💰 PAYMENT VERIFICATION REQUEST\n\n"
            f"👤 Name: {user.full_name}\n"
            f"🆔 User ID: {user.id}\n"
            f"🔢 UTR: {utr}"
        )

        keyboard = [
            [
                InlineKeyboardButton(
                    "✅ Accept",
                    callback_data=f"accept_{user.id}"
                ),
                InlineKeyboardButton(
                    "❌ Reject",
                    callback_data=f"reject_{user.id}"
                )
            ]
        ]

        # Screenshot admin को forward
        await update.message.forward(chat_id=ADMIN_ID)

        # Verification details admin को भेजें
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=caption,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

        await update.message.reply_text(
            "✅ आपका payment proof admin को भेज दिया गया है।\n\n"
            "Verification के बाद आपको जानकारी दी जाएगी।"
        )

        context.user_data["payment_waiting"] = False
        context.user_data.pop("utr", None)


# ---------------- ACCEPT / REJECT ----------------

async def payment_decision(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    data = query.data

    if data.startswith("accept_"):
        user_id = int(data.split("_")[1])

        await context.bot.send_message(
            chat_id=user_id,
            text=(
                "✅ आपका payment verify हो गया है।\n\n"
                "🎓 आपका paid course access जल्द activate किया जाएगा।"
            )
        )

        await query.edit_message_reply_markup(reply_markup=None)

        await query.message.reply_text(
            "✅ Payment ACCEPTED"
        )

    elif data.startswith("reject_"):
        user_id = int(data.split("_")[1])

        await context.bot.send_message(
            chat_id=user_id,
            text=(
                "❌ आपका payment verification reject हो गया है।\n\n"
                "कृपया सही payment proof / UTR के साथ दोबारा संपर्क करें।"
            )
        )

        await query.edit_message_reply_markup(reply_markup=None)

        await query.message.reply_text(
            "❌ Payment REJECTED"
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

    # Start / Help
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))

    # Courses button
    app.add_handler(
        CallbackQueryHandler(
            courses_menu,
            pattern="^courses$"
        )
    )

    # Paid Course button
    app.add_handler(
        CallbackQueryHandler(
            paid_course,
            pattern="^paid_course$"
        )
    )

    # Study options
    app.add_handler(
        CallbackQueryHandler(
            study_option,
            pattern="^(upsc|ncert|material|current|test)$"
        )
    )

    # Accept / Reject
    app.add_handler(
        CallbackQueryHandler(
            payment_decision,
            pattern="^(accept|reject)_"
        )
    )

    # Back button
    app.add_handler(
        CallbackQueryHandler(
            back_home,
            pattern="^back$"
        )
    )

    # Payment UTR + Screenshot
    app.add_handler(
        MessageHandler(
            filters.TEXT | filters.PHOTO,
            payment_message
        )
    )

    app.run_polling()


# ---------------- RUN BOT ----------------

if __name__ == "__main__":
    main()
