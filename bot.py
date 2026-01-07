from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters
)

BOT_TOKEN = "8593977769:AAH9MOpwAeYbxTrdcjVyDrMGf8B4qMhX18k"  # <-- এখানে তোমার Telegram Bot Token রাখবে
ADMIN_ID = 7441252176
OTP_GROUP_LINK = "https://t.me/otpwhu"

CHANNELS = ["@bd_wh_eran1", "@nameber_channel12", "@hnculc"]

# শুধুমাত্র অনুমোদিত দেশ
ALLOWED_COUNTRIES = [
    "Bangladesh", "India", "Pakistan", "Nepal", "Sri Lanka", "China",
    "Japan", "South Korea", "North Korea", "Russia", "United States",
    "Canada", "United Kingdom", "Germany", "France", "Italy", "Spain",
    "Portugal", "Australia", "New Zealand", "Brazil", "Argentina", "Mexico",
    "South Africa", "Egypt", "Turkey", "Saudi Arabia", "UAE", "Thailand",
    "Malaysia", "Singapore", "Indonesia", "Philippines", "Vietnam", "Myanmar",
    "Afghanistan"
]

# দেশ + পতাকা
COUNTRY_FLAGS = {
    "Bangladesh": "🇧🇩",
    "India": "🇮🇳",
    "Pakistan": "🇵🇰",
    "Nepal": "🇳🇵",
    "Sri Lanka": "🇱🇰",
    "China": "🇨🇳",
    "Japan": "🇯🇵",
    "South Korea": "🇰🇷",
    "North Korea": "🇰🇵",
    "Russia": "🇷🇺",
    "United States": "🇺🇸",
    "Canada": "🇨🇦",
    "United Kingdom": "🇬🇧",
    "Germany": "🇩🇪",
    "France": "🇫🇷",
    "Italy": "🇮🇹",
    "Spain": "🇪🇸",
    "Portugal": "🇵🇹",
    "Australia": "🇦🇺",
    "New Zealand": "🇳🇿",
    "Brazil": "🇧🇷",
    "Argentina": "🇦🇷",
    "Mexico": "🇲🇽",
    "South Africa": "🇿🇦",
    "Egypt": "🇪🇬",
    "Turkey": "🇹🇷",
    "Saudi Arabia": "🇸🇦",
    "UAE": "🇦🇪",
    "Thailand": "🇹🇭",
    "Malaysia": "🇲🇾",
    "Singapore": "🇸🇬",
    "Indonesia": "🇮🇩",
    "Philippines": "🇵🇭",
    "Vietnam": "🇻🇳",
    "Myanmar": "🇲🇲",
    "Afghanistan": "🇦🇫",
}

numbers = {}
used_numbers = {}
user_data = {}

# -------- LOAD NUMBERS ----------
def load_numbers():
    global numbers
    numbers = {}
    try:
        with open("numbers.txt", "r") as f:
            for line in f:
                if "|" in line:
                    country, num = line.strip().split("|")
                    country = country.strip()
                    num = num.strip()
                    if country in ALLOWED_COUNTRIES:
                        numbers.setdefault(country, []).append(num)
    except FileNotFoundError:
        print("numbers.txt ফাইল পাওয়া যায়নি।")

# -------- CHECK CHANNEL JOIN ----------
async def is_joined_all(bot, user_id):
    for ch in CHANNELS:
        try:
            m = await bot.get_chat_member(ch, user_id)
            if m.status not in ["member", "administrator", "creator"]:
                return False
        except:
            return False
    return True

# -------- START ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    buttons = [[InlineKeyboardButton(f"Join {ch}", url=f"https://t.me/{ch[1:]}")] for ch in CHANNELS]
    buttons.append([InlineKeyboardButton("✅ Continue", callback_data="continue")])

    await update.message.reply_text(
        "🔐 সবগুলো Channel Join করুন তারপর Continue চাপুন",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

# -------- CONTINUE ----------
async def continue_btn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if not await is_joined_all(context.bot, query.from_user.id):
        await query.answer("❌ সবগুলো Channel Join করেননি", show_alert=True)
        return

    keyboard = [[InlineKeyboardButton(f"{COUNTRY_FLAGS.get(c, '')} {c}", callback_data=f"country|{c}")]
                for c in numbers.keys()]

    await query.message.reply_text(
        "🌍 Country Select করুন",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# -------- COUNTRY ----------
async def select_country(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    country = query.data.split("|")[1]
    user_data[query.from_user.id] = {"country": country}

    await send_number(query)

# -------- SEND NUMBER ----------
async def send_number(query):
    uid = query.from_user.id
    country = user_data[uid]["country"]

    used = used_numbers.setdefault(uid, set())

    for num in numbers.get(country, []):
        if num not in used:
            used.add(num)
            buttons = [
                [InlineKeyboardButton("🔄 Change Number", callback_data="change")],
                [InlineKeyboardButton("📩 OTP Group", url=OTP_GROUP_LINK)],
                [InlineKeyboardButton("🌍 Change Country", callback_data="change_country")]
            ]
            await query.message.reply_text(
                f"📱 COUNTRY: {country}\n\n📞 NUMBER:\n`{num}`",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup(buttons)
            )
            return

    await query.message.reply_text("❌ এই Country তে আর নাম্বার নেই")

# -------- CHANGE NUMBER ----------
async def change_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await send_number(update.callback_query)

# -------- CHANGE COUNTRY ----------
async def change_country(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    keyboard = [[InlineKeyboardButton(f"{COUNTRY_FLAGS.get(c, '')} {c}", callback_data=f"country|{c}")]
                for c in numbers.keys()]

    await query.message.reply_text(
        "🌍 নতুন Country Select করুন",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# -------- ADMIN UPLOAD ----------
async def upload(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    file = await update.message.document.get_file()
    await file.download("numbers.txt")  # নতুন ফাইল ডাউনলোড হবে
    load_numbers()  # লোড হবে

    await update.message.reply_text("✅ numbers.txt Updated Successfully")

# -------- MAIN ----------
load_numbers()

app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(continue_btn, pattern="continue"))
app.add_handler(CallbackQueryHandler(select_country, pattern="country"))
app.add_handler(CallbackQueryHandler(change_number, pattern="change"))
app.add_handler(CallbackQueryHandler(change_country, pattern="change_country"))
app.add_handler(MessageHandler(filters.Document.TEXT, upload))

print("✅ Bot Running...")
app.run_polling()
