import os
import threading
import sqlite3
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 8604692393
DB_FILE = "payments.db"

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN environment variable is missing.")


# =========================================================
# DATABASE
# =========================================================

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            lecture INTEGER NOT NULL,
            utr TEXT NOT NULL,
            status TEXT DEFAULT 'pending'
        )
    """)

    conn.commit()
    conn.close()


# =========================================================
# RENDER HEALTH SERVER
# =========================================================

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(b"KGS IAS Bot is running!")

    def log_message(self, format, *args):
        pass


def run_health_server():
    port = int(os.getenv("PORT", "10000"))

    server = ThreadingHTTPServer(
        ("0.0.0.0", port),
        HealthHandler
    )

    server.serve_forever()


# =========================================================
# START
# =========================================================

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


# =========================================================
# COURSES
# =========================================================

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


# =========================================================
# STUDY OPTIONS
# =========================================================

async def study_option(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    option = query.data

    if option == "upsc":
        text = (
            "🏛️ UPSC Course\n\n"
            "UPSC Civil Services की तैयारी के लिए "
            "courses और study resources उपलब्ध होंगे।"
        )

    elif option == "ncert":
        text = (
            "📚 NCERT Course\n\n"
            "Class 6 से 12 तक की NCERT आधारित "
            "study सामग्री यहाँ उपलब्ध होगी।"
        )

    elif option == "material":
        text = (
            "📖 Study Material\n\n"
            "UPSC preparation के लिए notes, PDFs और "
            "अन्य study material यहाँ मिलेगा।"
        )

    elif option == "current":
        text = (
            "📰 Current Affairs\n\n"
            "Daily और Monthly Current Affairs "
            "यहाँ उपलब्ध कराए जाएंगे।"
        )

    elif option == "test":
        text = (
            "📝 Test Series\n\n"
            "UPSC preparation के लिए test series और "
            "practice questions यहाँ मिलेंगे।"
        )

    else:
        return

    keyboard = [[
        InlineKeyboardButton(
            "🔙 Back to Courses",
            callback_data="courses"
        )
    ]]

    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# =========================================================
# PAID COURSE
# =========================================================

async def paid_course(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    keyboard = [
        [
            InlineKeyboardButton(
                "🎥 Lecture 6 - ₹2",
                callback_data="buy_6"
            )
        ],
        [
            InlineKeyboardButton(
                "🎥 Lecture 7 - ₹2",
                callback_data="buy_7"
            )
        ],
        [
            InlineKeyboardButton(
                "🎥 Lecture 8 - ₹2",
                callback_data="buy_8"
            )
        ],
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
        ],
    ]

    await query.edit_message_text(
        "🎓 Paid Lectures\n\n"
        "5 lectures FREE हैं।\n"
        "Lecture 6 के बाद हर lecture ₹2 का है।\n\n"
        "जिस lecture को खरीदना है, उसे चुनें:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# =========================================================
# BUY LECTURE
# =========================================================

async def buy_lecture(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    lecture = int(query.data.split("_")[1])

    context.user_data["payment_waiting"] = True
    context.user_data["lecture"] = lecture
    context.user_data.pop("utr", None)

    await query.edit_message_text(
        f"🎥 Lecture {lecture}\n\n"
        "💰 Price: ₹2\n\n"
        "💳 UPI ID:\n"
        "respect-girls@ybl\n\n"
        "₹2 payment करने के बाद\n"
        "UTR / Transaction ID भेजें।\n\n"
        "उसके बाद payment screenshot भेजें 📸"
    )


# =========================================================
# PAYMENT MESSAGE
# =========================================================

async def payment_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if not context.user_data.get("payment_waiting"):
        return

    user = update.effective_user

    if update.message is None:
        return

    lecture = context.user_data.get("lecture")

    # UTR
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
            "अब payment का screenshot भेजें 📸"
        )

        return

    # SCREENSHOT
    if update.message.photo:

        utr = context.user_data.get("utr")

        if not utr or not lecture:
            await update.message.reply_text(
                "❌ पहले lecture select करके payment करें।"
            )
            return

        conn = sqlite3.connect(DB_FILE)
        cur = conn.cursor()

        cur.execute(
            """
            INSERT INTO payments
            (user_id, lecture, utr, status)
            VALUES (?, ?, ?, 'pending')
            """,
            (user.id, lecture, utr)
        )

        payment_id = cur.lastrowid

        conn.commit()
        conn.close()

        caption = (
            "💰 PAYMENT VERIFICATION REQUEST\n\n"
            f"👤 Name: {user.full_name}\n"
            f"🆔 User ID: {user.id}\n"
            f"🎥 Lecture: {lecture}\n"
            f"💵 Amount: ₹2\n"
            f"🔢 UTR: {utr}\n"
            f"🧾 Payment ID: {payment_id}"
        )

        keyboard = [[
            InlineKeyboardButton(
                "✅ Accept",
                callback_data=f"accept_{payment_id}"
            ),
            InlineKeyboardButton(
                "❌ Reject",
                callback_data=f"reject_{payment_id}"
            )
        ]]

        await update.message.forward(
            chat_id=ADMIN_ID
        )

        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=caption,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

        await update.message.reply_text(
            "✅ आपका payment proof admin को भेज दिया गया है।\n\n"
            "Verification के बाद आपको बताया जाएगा।"
        )

        context.user_data["payment_waiting"] = False
        context.user_data.pop("utr", None)
        context.user_data.pop("lecture", None)


# =========================================================
# ACCEPT / REJECT
# =========================================================

async def payment_decision(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query
    await query.answer()

    data = query.data

    payment_id = int(data.split("_")[1])

    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    cur.execute(
        "SELECT user_id, lecture FROM payments WHERE id = ?",
        (payment_id,)
    )

    row = cur.fetchone()

    if not row:
        conn.close()
        await query.message.reply_text(
            "❌ Payment record नहीं मिला।"
        )
        return

    user_id, lecture = row

    if data.startswith("accept_"):

        cur.execute(
            """
            UPDATE payments
            SET status = 'approved'
            WHERE id = ?
            """,
            (payment_id,)
        )

        conn.commit()
        conn.close()

        await context.bot.send_message(
            chat_id=user_id,
            text=(
                "✅ Payment ACCEPTED\n\n"
                f"🎥 Lecture {lecture} का payment verify हो गया है।\n\n"
                "अब website खोलकर lecture देखें।"
            ),
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton(
                    "🌐 Open Website",
                    url="https://vishrat.com.in"
                )
            ]])
        )

        await query.edit_message_reply_markup(
            reply_markup=None
        )

        await query.message.reply_text(
            f"✅ Payment ACCEPTED - Lecture {lecture}"
        )

    elif data.startswith("reject_"):

        cur.execute(
            """
            UPDATE payments
            SET status = 'rejected'
            WHERE id = ?
            """,
            (payment_id,)
        )

        conn.commit()
        conn.close()

        await context.bot.send_message(
            chat_id=user_id,
            text=(
                "❌ Payment verification reject हो गया है।\n\n"
                "कृपया सही payment proof / UTR के साथ दोबारा payment करें।"
            )
        )

        await query.edit_message_reply_markup(
            reply_markup=None
        )

        await query.message.reply_text(
            f"❌ Payment REJECTED - Lecture {lecture}"
        )


# =========================================================
# BACK HOME
# =========================================================

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


# =========================================================
# HELP
# =========================================================

async def help_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    await update.message.reply_text(
        "ℹ️ Help\n\n"
        "/start - Bot शुरू करें\n"
        "/help - Help देखें"
    )


# =========================================================
# MAIN
# =========================================================

def main():

    init_db()

    threading.Thread(
        target=run_health_server,
        daemon=True
    ).start()

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(
        CommandHandler("start", start)
    )

    app.add_handler(
        CommandHandler("help", help_command)
    )

    app.add_handler(
        CallbackQueryHandler(
            courses_menu,
            pattern=r"^courses$"
        )
    )

    app.add_handler(
        CallbackQueryHandler(
            paid_course,
            pattern=r"^paid_course$"
        )
    )

    app.add_handler(
        CallbackQueryHandler(
            buy_lecture,
            pattern=r"^buy_[6-9][0-9]*$"
        )
    )

    app.add_handler(
        CallbackQueryHandler(
            study_option,
            pattern=r"^(upsc|ncert|material|current|test)$"
        )
    )

    app.add_handler(
        CallbackQueryHandler(
            payment_decision,
            pattern=r"^(accept|reject)_"
        )
    )

    app.add_handler(
        CallbackQueryHandler(
            back_home,
            pattern=r"^back$"
        )
    )

    app.add_handler(
        MessageHandler(
            filters.TEXT | filters.PHOTO,
            payment_message
        )
    )

    app.run_polling(
        drop_pending_updates=True
    )


if __name__ == "__main__":
    main()
