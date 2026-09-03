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

    # PhonePe QR भेजें
    await context.bot.send_photo(
        chat_id=query.from_user.id,
        photo="https://raw.githubusercontent.com/kgsias01-source/http-Vishrat.com.in/main/IMG_20260903_093348_965.jpg",
        caption=f"📱 PhonePe QR Scan करके ₹{PRICE} Pay करें"
    )

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
