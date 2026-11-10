import os
import logging
from telegram import (
    Update, ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton
)
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler,
    ContextTypes, filters
)

# Set these as environment variables on your hosting service.
BOT_TOKEN = os.getenv("BOT_TOKEN", "PASTE_YOUR_BOT_TOKEN_HERE")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID", "PASTE_YOUR_TELEGRAM_NUMERIC_ID_HERE")

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

MENU = ReplyKeyboardMarkup(
    [
        [KeyboardButton("🚀 خرید کانفیگ"), KeyboardButton("🧪 اکانت تست")],
        [KeyboardButton("📞 پشتیبانی"), KeyboardButton("🎁 معرفی به دوستان")],
    ],
    resize_keyboard=True
)

WELCOME = (
    "سلام دوست عزیز! 👋❤️\n\n"
    "به ربات رسمی Adnan VPN خوش اومدی.\n"
    "برای دیدن گزینه‌ها از منوی پایین استفاده کن."
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(WELCOME, reply_markup=MENU)

async def send_order_to_admin(update, context, order_text):
    if not ADMIN_CHAT_ID.isdigit():
        await update.message.reply_text(
            "ربات هنوز به پنل مدیریت وصل نشده. مدیر باید ADMIN_CHAT_ID را تنظیم کند."
        )
        return
    user = update.effective_user
    who = f"@{user.username}" if user.username else f"کاربر با شناسه {user.id}"
    msg = f"📥 سفارش جدید\n{who}\nشناسه: {user.id}\n\n{order_text}"
    await context.bot.send_message(chat_id=int(ADMIN_CHAT_ID), text=msg)
    await update.message.reply_text(
        "✅ درخواستت برای مدیر ارسال شد. بعد از بررسی، خود مدیر در تلگرام باهات هماهنگ می‌کنه.",
        reply_markup=MENU
    )

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "🚀 خرید کانفیگ":
        context.user_data["waiting_for"] = "buy"
        await update.message.reply_text(
            "لطفاً حجم و مدت‌زمان موردنظرت رو بنویس؛ مثلاً: ۳۰ گیگ، یک ماه."
        )
    elif text == "🧪 اکانت تست":
        context.user_data["waiting_for"] = "test"
        await update.message.reply_text(
            "برای درخواست اکانت تست، بنویس «اکانت تست می‌خوام»."
        )
    elif text == "📞 پشتیبانی":
        await update.message.reply_text(
            "برای پشتیبانی، پیام خودت رو همین‌جا بنویس تا درخواستت برای مدیر ارسال بشه."
        )
        context.user_data["waiting_for"] = "support"
    elif text == "🎁 معرفی به دوستان":
        me = await context.bot.get_me()
        link = f"https://t.me/{me.username}?start=ref_{update.effective_user.id}"
        await update.message.reply_text(f"🎁 لینک معرفی تو:\n{link}")
    elif context.user_data.get("waiting_for") in {"buy", "test", "support"}:
        kind = context.user_data.pop("waiting_for")
        label = {"buy": "خرید کانفیگ", "test": "درخواست اکانت تست", "support": "درخواست پشتیبانی"}[kind]
        await send_order_to_admin(update, context, f"{label}\nجزئیات: {text}")
    else:
        await update.message.reply_text("لطفاً یکی از گزینه‌های منو رو انتخاب کن.", reply_markup=MENU)

def main():
    if BOT_TOKEN == "PASTE_YOUR_BOT_TOKEN_HERE":
        raise SystemExit("ابتدا مقدار BOT_TOKEN را در تنظیمات میزبانی وارد کن.")
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.run_polling()

if __name__ == "__main__":
    main()
