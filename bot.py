import telebot
import requests

# Bot Token
TOKEN = "7399378678:AAFN8Gvwjz_aEcASevD1p5MxSL6QKkh1pX0"
bot = telebot.TeleBot(TOKEN)

# ইউজার লগইন তথ্য
user_data = {}

# /start
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "👋 স্বাগতম!\n\n📌 লগইন করুন: `/login SID TOKEN`\n📞 নম্বর দেখুন: `/numbers`\n📩 মেসেজ দেখুন: `/messages`\n💰 ব্যালেন্স দেখুন: `/balance`\n🧾 SID দেখুন: `/mysid`\n🔑 Token দেখুন: `/mytoken`\n🚪 লগআউট করুন: `/logout`", parse_mode="Markdown")

# /login SID TOKEN
@bot.message_handler(commands=['login'])
def login(message):
    chat_id = message.chat.id
    args = message.text.split()

    if len(args) != 3:
        bot.send_message(chat_id, "❌ সঠিক ফরম্যাট: `/login SID TOKEN`", parse_mode="Markdown")
        return

    sid = args[1]
    token = args[2]
    url = f"https://api.twilio.com/2010-04-01/Accounts/{sid}.json"

    response = requests.get(url, auth=(sid, token))
    if response.status_code == 200:
        user_data[chat_id] = {"sid": sid, "token": token}
        bot.send_message(chat_id, "✅ লগইন সফলভাবে সম্পন্ন হয়েছে!")
    else:
        bot.send_message(chat_id, "❌ SID বা TOKEN ভুল!")

# /logout
@bot.message_handler(commands=['logout'])
def logout(message):
    chat_id = message.chat.id
    if chat_id in user_data:
        user_data.pop(chat_id)
        bot.send_message(chat_id, "🚪 আপনি সফলভাবে লগআউট হয়েছেন।")
    else:
        bot.send_message(chat_id, "❌ আপনি লগইন করেননি।")

# /me
@bot.message_handler(commands=['me'])
def me(message):
    chat_id = message.chat.id
    if chat_id in user_data:
        sid = user_data[chat_id]['sid']
        bot.send_message(chat_id, f"🔐 আপনি লগইন করেছেন।\nSID: `{sid}`", parse_mode="Markdown")
    else:
        bot.send_message(chat_id, "❌ আপনি এখনো লগইন করেননি।")

# /mysid
@bot.message_handler(commands=['mysid'])
def mysid(message):
    chat_id = message.chat.id
    if chat_id in user_data:
        sid = user_data[chat_id]['sid']
        bot.send_message(chat_id, f"🧾 আপনার SID:\n`{sid}`", parse_mode="Markdown")
    else:
        bot.send_message(chat_id, "❌ লগইন করুন আগে।")

# /mytoken
@bot.message_handler(commands=['mytoken'])
def mytoken(message):
    chat_id = message.chat.id
    if chat_id in user_data:
        token = user_data[chat_id]['token']
        bot.send_message(chat_id, f"🔑 আপনার Token:\n`{token}`", parse_mode="Markdown")
    else:
        bot.send_message(chat_id, "❌ লগইন করুন আগে।")

# /balance
@bot.message_handler(commands=['balance'])
def balance(message):
    chat_id = message.chat.id
    if chat_id in user_data:
        sid = user_data[chat_id]['sid']
        token = user_data[chat_id]['token']
        url = f"https://api.twilio.com/2010-04-01/Accounts/{sid}/Balance.json"
        response = requests.get(url, auth=(sid, token))

        if response.status_code == 200:
            data = response.json()
            balance = data.get('balance')
            currency = data.get('currency')
            bot.send_message(chat_id, f"💰 আপনার ব্যালেন্স: `{balance} {currency}`", parse_mode="Markdown")
        else:
            bot.send_message(chat_id, "⚠️ ব্যালেন্স আনতে সমস্যা হচ্ছে।")
    else:
        bot.send_message(chat_id, "❌ আগে লগইন করুন।")

# /numbers
@bot.message_handler(commands=['numbers'])
def numbers(message):
    chat_id = message.chat.id
    if chat_id in user_data:
        sid = user_data[chat_id]['sid']
        token = user_data[chat_id]['token']
        url = f"https://api.twilio.com/2010-04-01/Accounts/{sid}/IncomingPhoneNumbers.json"
        response = requests.get(url, auth=(sid, token))

        if response.status_code == 200:
            data = response.json()
            phone_numbers = data['incoming_phone_numbers']
            if not phone_numbers:
                bot.send_message(chat_id, "📭 কোনো নম্বর পাওয়া যায়নি।")
                return

            msg = "📱 আপনার নম্বরসমূহ:\n"
            for p in phone_numbers:
                num = p.get('phone_number')
                sid = p.get('sid')
                msg += f"- `{num}` (SID: `{sid}`)\n"
            bot.send_message(chat_id, msg, parse_mode="Markdown")
        else:
            bot.send_message(chat_id, "⚠️ নম্বর আনতে সমস্যা হচ্ছে।")
    else:
        bot.send_message(chat_id, "❌ আগে লগইন করুন।")

# /messages
@bot.message_handler(commands=['messages'])
def messages_handler(message):
    chat_id = message.chat.id
    if chat_id in user_data:
        sid = user_data[chat_id]['sid']
        token = user_data[chat_id]['token']
        url = f"https://api.twilio.com/2010-04-01/Accounts/{sid}/Messages.json"
        response = requests.get(url, auth=(sid, token))

        if response.status_code == 200:
            data = response.json()
            messages = data['messages'][:5]  # সর্বশেষ ৫টি মেসেজ

            if not messages:
                bot.send_message(chat_id, "📭 কোনো মেসেজ পাওয়া যায়নি।")
                return

            msg = "📩 সর্বশেষ মেসেজসমূহ:\n"
            for m in messages:
                from_ = m.get('from')
                to = m.get('to')
                body = m.get('body')
                msg += f"\n🧾 From: `{from_}`\n➡️ To: `{to}`\n💬 Message: `{body}`\n"
            bot.send_message(chat_id, msg, parse_mode="Markdown")
        else:
            bot.send_message(chat_id, "⚠️ মেসেজ আনতে সমস্যা হচ্ছে।")
    else:
        bot.send_message(chat_id, "❌ আগে লগইন করুন।")

# বট চালু
print("🤖 Bot চালু হয়েছে...")
bot.infinity_polling()
