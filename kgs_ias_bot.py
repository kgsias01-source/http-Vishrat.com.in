import os
import sqlite3
import threading
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

# =========================================================
# SETTINGS
# =========================================================

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 8604692393

WEBSITE_URL = "https://http-vishrat-com-in-1.onrender.com"

UPI_ID = "respect-girls@ybl"
PRICE = 2

DB_FILE = "payments.db"

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN environment variable is missing.")


# =========================================================
# DATABASE
# =========================================================

def db_connect():
    return sqlite3.connect(DB_FILE)


def init_db():
    conn = db_connect()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            lecture INTEGER NOT NULL,
            utr TEXT DEFAULT '',
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS access (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            lecture INTEGER NOT NULL,
            payment_id INTEGER,
            granted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, lecture)
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

    context.user_data.pop("payment_waiting", None)

    keyboard = [
        [
            InlineKeyboardButton(
                "🎓 Free Lectures",
                callback_data="free_menu"
            )
        ],
        [
            InlineKeyboardButton(
                "💳 Paid Lectures",
                callback_data="paid_menu"
            )
        ],
        [
            InlineKeyboardButton(
                "🌐 Open Website",
                url=WEBSITE_URL
            )
        ]
    ]

    await update.message.reply_text(
        "🌸 Welcome to Vishrat!\n\n"
        "🎓 UPSC Preparation\n"
        "📚 Lectures & Courses\n\n"
        "👇 नीचे से option चुनें:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# =========================================================
# HELP
# =========================================================

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "📖 Help\n\n"
        "1️⃣ Free Lectures खोलें\n"
        "2️⃣ Paid Lecture चुनें\n"
        "3️⃣ ₹2 payment करें\n"
        "4️⃣ Payment का screenshot भेजें\n"
        "5️⃣ Admin verification करेगा\n"
        "6️⃣ Accept होने के बाद lecture unlock होगा\n\n"
        "❌ UTR भेजने की जरूरत नहीं है."
    )


# =========================================================
# FREE MENU
# =========================================================

async def free_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    keyboard = [
        [
            InlineKeyboardButton(
                "📚 Lecture 1",
                url="https://youtu.be/Ww8CFGeHaqE"
            )
        ],
        [
            InlineKeyboardButton(
                "📚 Lecture 2",
                url="https://youtu.be/GKQw8vFCM7w"
            )
        ],
        [
            InlineKeyboardButton(
                "📚 Lecture 3",
                url="https://youtu.be/VRKvJYlQN-0"
            )
        ],
        [
            InlineKeyboardButton(
                "📚 Lecture 4",
                url="https://youtu.be/T7JrQ9vv-DY"
            )
        ],
        [
            InlineKeyboardButton(
                "📚 Lecture 5",
                url="https://youtu.be/UcMjneaHW1c"
            )
        ],
        [
            InlineKeyboardButton(
                "⬅️ Back",
                callback_data="home"
            )
        ]
    ]

    await query.edit_message_text(
        "🎓 Free Lectures\n\n"
        "नीचे से lecture चुनें:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# =========================================================
# PAID MENU
# =========================================================

async def paid_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    keyboard = [
        [
            InlineKeyboardButton(
                "🔒 Lecture 6 - ₹2",
                callback_data="buy_6"
            )
        ],
        [
            InlineKeyboardButton(
                "🔒 Lecture 7 - ₹2",
                callback_data="buy_7"
            )
        ],
        [
            InlineKeyboardButton(
                "🔒 Lecture 8 - ₹2",
                callback_data="buy_8"
            )
        ],
        [
            InlineKeyboardButton(
                "⬅️ Back",
                callback_data="home"
            )
        ]
    ]

    await query.edit_message_text(
        "💎 Full Course\n\n"
        "🔒 Paid Lectures\n"
        "💰 प्रत्येक lecture = ₹2\n\n"
        "Lecture चुनकर payment करें:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# =========================================================
# BUY LECTURE
# =========================================================

async def buy_lecture(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    lecture = int(query.data.split("_")[1])

    context.user_data["payment_waiting"] = lecture

    keyboard = [
        [
            InlineKeyboardButton(
                "🌐 Open Website",
                url=WEBSITE_URL
            )
        ],
        [
            InlineKeyboardButton(
                "⬅️ Paid Lectures",
                callback_data="paid_menu"
            )
        ]
    ]

    await query.edit_message_text(
        f"🔒 Lecture {lecture}\n\n"
        f"💰 Amount: ₹{PRICE}\n\n"
        f"📱 UPI ID:\n"
        f"{UPI_ID}\n\n"
        "Payment करने के बाद:\n\n"
        "📸 केवल payment screenshot यहाँ भेजें.\n\n"
        "❌ UTR की जरूरत नहीं है.\n"
        "❌ कोई text भेजने की जरूरत नहीं है.\n\n"
        "Screenshot भेजते ही Admin को verification के लिए चला जाएगा.",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# =========================================================
# PAYMENT SCREENSHOT
# =========================================================

async def payment_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user
    message = update.message

    lecture = context.user_data.get("payment_waiting")

    if not lecture:
        await message.reply_text(
            "⚠️ पहले Paid Lecture चुनें.\n\n"
            "फिर payment screenshot भेजें."
        )
        return

    conn = db_connect()
    cur = conn.cursor()

    # Check duplicate pending request
    cur.execute("""
        SELECT id
        FROM payments
        WHERE user_id = ?
          AND lecture = ?
          AND status = 'pending'
        LIMIT 1
    """, (user.id, lecture))

    existing = cur.fetchone()

    if existing:
        conn.close()

        await message.reply_text(
            "⏳ आपका payment screenshot पहले ही verification में है.\n\n"
            "कृपया Admin के decision का इंतजार करें."
        )
        return

    # Create payment request
    cur.execute("""
        INSERT INTO payments
        (user_id, lecture, utr, status)
        VALUES (?, ?, '', 'pending')
    """, (user.id, lecture))

    payment_id = cur.lastrowid

    conn.commit()
    conn.close()

    # Admin buttons
    keyboard = [
        [
            InlineKeyboardButton(
                "✅ ACCEPT",
                callback_data=f"accept_{payment_id}"
            ),
            InlineKeyboardButton(
                "❌ REJECT",
                callback_data=f"reject_{payment_id}"
            )
        ]
    ]

    username = (
        f"@{user.username}"
        if user.username
        else "No username"
    )

    caption = (
        "💳 NEW PAYMENT REQUEST\n\n"
        f"🆔 Payment ID: {payment_id}\n"
        f"👤 User ID: {user.id}\n"
        f"👤 Username: {username}\n"
        f"📚 Lecture: {lecture}\n"
        f"💰 Amount: ₹{PRICE}\n\n"
        "📸 Payment screenshot नीचे है.\n"
        "👇 Decision करें:"
    )

    try:

        await context.bot.send_photo(
            chat_id=ADMIN_ID,
            photo=message.photo[-1].file_id,
            caption=caption,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

        await message.reply_text(
            "✅ Screenshot successfully भेज दिया गया है.\n\n"
            "⏳ Admin verification के बाद आपका lecture unlock होगा."
        )

        context.user_data.pop("payment_waiting", None)

    except Exception as e:

        # Roll back payment if admin message fails
        conn = db_connect()
        cur = conn.cursor()

        cur.execute(
            "DELETE FROM payments WHERE id = ?",
            (payment_id,)
        )

        conn.commit()
        conn.close()

        await message.reply_text(
            "❌ Screenshot भेजने में समस्या आई.\n"
            "कृपया थोड़ी देर बाद दोबारा कोशिश करें."
        )

        print("ADMIN SEND ERROR:", e)


# =========================================================
# ADMIN ACCEPT / REJECT
# =========================================================

async def payment_decision(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    # Only Admin
    if query.from_user.id != ADMIN_ID:

        await query.answer(
            "❌ केवल Admin यह action कर सकता है.",
            show_alert=True
        )

        return

    await query.answer()

    action, payment_id_text = query.data.split("_", 1)

    payment_id = int(payment_id_text)

    conn = db_connect()
    cur = conn.cursor()

    cur.execute("""
        SELECT user_id, lecture, status
        FROM payments
        WHERE id = ?
    """, (payment_id,))

    payment = cur.fetchone()

    if not payment:

        conn.close()

        await query.edit_message_caption(
            caption="❌ Payment request नहीं मिली."
        )

        return

    user_id, lecture, status = payment

    # Already processed
    if status != "pending":

        conn.close()

        await query.answer(
            f"Already {status}.",
            show_alert=True
        )

        return

    # =====================================================
    # ACCEPT
    # =====================================================

    if action == "accept":

        cur.execute("""
            UPDATE payments
            SET status = 'accepted'
            WHERE id = ?
              AND status = 'pending'
        """, (payment_id,))

        cur.execute("""
            INSERT OR IGNORE INTO access
            (user_id, lecture, payment_id)
            VALUES (?, ?, ?)
        """, (user_id, lecture, payment_id))

        conn.commit()
        conn.close()

        try:

            await context.bot.send_message(
                chat_id=user_id,
                text=(
                    "🎉 PAYMENT ACCEPTED!\n\n"
                    f"📚 Lecture {lecture} unlock हो गया है.\n\n"
                    "🌐 Website खोलें और अपना course access करें."
                ),
                reply_markup=InlineKeyboardMarkup([
                    [
                        InlineKeyboardButton(
                            "🌐 Open Website",
                            url=WEBSITE_URL
                        )
                    ]
                ])
            )

        except Exception as e:
            print("USER MESSAGE ERROR:", e)

        await query.edit_message_caption(
            caption=(
                "✅ PAYMENT ACCEPTED\n\n"
                f"Payment ID: {payment_id}\n"
                f"User ID: {user_id}\n"
                f"Lecture: {lecture}\n"
                f"Amount: ₹{PRICE}"
            )
        )

    # =====================================================
    # REJECT
    # =====================================================

    elif action == "reject":

        cur.execute("""
            UPDATE payments
            SET status = 'rejected'
            WHERE id = ?
              AND status = 'pending'
        """, (payment_id,))

        conn.commit()
        conn.close()

        try:

            await context.bot.send_message(
                chat_id=user_id,
                text=(
                    "❌ PAYMENT REJECTED\n\n"
                    f"Lecture: {lecture}\n\n"
                    "Payment screenshot verification में accept नहीं हुआ.\n"
                    "कृपया सही payment screenshot के साथ दोबारा कोशिश करें."
                )
            )

        except Exception as e:
            print("USER MESSAGE ERROR:", e)

        await query.edit_message_caption(
            caption=(
                "❌ PAYMENT REJECTED\n\n"
                f"Payment ID: {payment_id}\n"
                f"User ID: {user_id}\n"
                f"Lecture: {lecture}"
            )
        )


# =========================================================
# HOME
# =========================================================

async def home(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    keyboard = [
        [
            InlineKeyboardButton(
                "🎓 Free Lectures",
                callback_data="free_menu"
            )
        ],
        [
            InlineKeyboardButton(
                "💳 Paid Lectures",
                callback_data="paid_menu"
            )
        ],
        [
            InlineKeyboardButton(
                "🌐 Website",
                url=WEBSITE_URL
            )
        ]
    ]

    await query.edit_message_text(
        "🏠 Vishrat Home\n\n"
        "👇 Option चुनें:",
        reply_markup=InlineKeyboardMarkup(keyboard)
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

    app = (
        Application.builder()
        .token(BOT_TOKEN)
        .build()
    )

    # Commands
    app.add_handler(
        CommandHandler("start", start)
    )

    app.add_handler(
        CommandHandler("help", help_command)
    )

    # Menus
    app.add_handler(
        CallbackQueryHandler(
            free_menu,
            pattern="^free_menu$"
        )
    )

    app.add_handler(
        CallbackQueryHandler(
            paid_menu,
            pattern="^paid_menu$"
        )
    )

    app.add_handler(
        CallbackQueryHandler(
            home,
            pattern="^home$"
        )
    )

    # Buy buttons
    app.add_handler(
        CallbackQueryHandler(
            buy_lecture,
            pattern="^buy_[6-8]$"
        )
    )

    # Admin decisions
    app.add_handler(
        CallbackQueryHandler(
            payment_decision,
            pattern="^(accept|reject)_[0-9]+$"
        )
    )

    # Payment screenshots
    app.add_handler(
        MessageHandler(
            filters.PHOTO,
            payment_photo
        )
    )

    print("Vishrat Bot Started...")

    app.run_polling(
        allowed_updates=Update.ALL_TYPES
    )


if __name__ == "__main__":
    main()
