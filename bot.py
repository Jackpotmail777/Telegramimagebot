import os
import telebot
import requests
import time

TELEGRAM_TOKEN = os.environ['TELEGRAM_TOKEN']
AI_KEY = os.environ['STABILITY_API_KEY']
CRYPTO_ADDRESS = os.environ['CRYPTO_ADDRESS']
YOUR_TELEGRAM_ID = int(os.environ['ADMIN_ID'])
PRICE_USDT = int(os.environ.get('PRICE_USDT', 2))

bot = telebot.TeleBot(TELEGRAM_TOKEN)
paid_users = set()

@bot.message_handler(commands=['start'])
def start(message):
    if message.from_user.id in paid_users:
        bot.send_message(message.chat.id, "✅ Оплачено! Пиши что нарисовать.")
    else:
        bot.send_message(message.chat.id, 
            f"🎨 Бот генерации изображений\n💵 Цена: {PRICE_USDT} USDT\n📍 Адрес: `{CRYPTO_ADDRESS}`\n📌 Оплати и пришли хэш транзакции",
            parse_mode='Markdown')

@bot.message_handler(func=lambda m: '0x' in m.text)
def payment(message):
    user_id = message.from_user.id
    bot.send_message(message.chat.id, "✅ Получил хэш! Проверю вручную.")
    bot.send_message(YOUR_TELEGRAM_ID, f"💰 Платёж от {user_id}\nХэш: {message.text}")

@bot.message_handler(commands=['confirm'])
def confirm(message):
    if message.from_user.id == YOUR_TELEGRAM_ID:
        try:
            user_id = int(message.text.split()[1])
            paid_users.add(user_id)
            bot.send_message(user_id, "✅ Оплата подтверждена! Теперь можете использовать бота.")
        except:
            pass

@bot.message_handler(func=lambda m: True)
def generate(message):
    if message.from_user.id not in paid_users and message.from_user.id != YOUR_TELEGRAM_ID:
        bot.send_message(message.chat.id, "❌ Сначала оплатите! /start")
        return
    
    try:
        bot.send_chat_action(message.chat.id, 'upload_photo')
        response = requests.post(
            "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image",
            headers={"Authorization": f"Bearer {AI_KEY}"},
            json={"text_prompts": [{"text": message.text}], "cfg_scale": 7, "height": 1024, "width": 1024, "samples": 1}
        )
        if response.status_code == 200:
            bot.send_photo(message.chat.id, response.content)
        else:
            bot.send_message(message.chat.id, "❌ Ошибка генерации")
    except:
        bot.send_message(message.chat.id, "⚠️ Ошибка")

print("🤖 Бот запущен!")
bot.polling()
