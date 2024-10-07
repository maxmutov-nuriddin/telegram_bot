from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import aiohttp
import asyncio

# Ваш токен бота
TOKEN = '7435741097:AAEVsd3t6sgkNUQoAWAO8NKvhdMmfCVv0S4'
# Ваш ID (администратора)
ADMIN_ID = 1604384939

# URL MockAPI
MOCKAPI_URL = 'https://6703f9f6ab8a8f8927327c94.mockapi.io/chat_users'

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.chat.id
    await update.message.reply_text('Привет! Все ваши сообщения будут отправлены администратору.')

async def forward_user_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.chat.id
    message_text = update.message.text
    
    # Отправляем сообщение на MockAPI
    async with aiohttp.ClientSession() as session:
        async with session.post(MOCKAPI_URL, json={"user_id": user_id, "message": message_text}) as response:
            if response.status == 201:
                await context.bot.send_message(chat_id=ADMIN_ID, text=f'Сообщение от пользователя {user_id}: {message_text}')
                await update.message.reply_text('Ваше сообщение было отправлено администратору.')
            else:
                await update.message.reply_text('Произошла ошибка при отправке сообщения.')

async def forward_admin_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message.chat.id == ADMIN_ID:
        parts = update.message.text.split()
        if len(parts) > 1:
            user_id = parts[0]
            message_to_user = ' '.join(parts[1:])

            if user_id.isdigit():
                user_id = int(user_id)

                # Получаем сообщения от MockAPI
                async with aiohttp.ClientSession() as session:
                    async with session.get(MOCKAPI_URL) as response:
                        if response.status == 200:
                            messages = await response.json()
                            user_messages = [msg for msg in messages if msg['user_id'] == user_id]

                            if user_messages:
                                # Отправляем сообщение пользователю
                                await context.bot.send_message(chat_id=user_id, text=f'Ответ от администратора: {message_to_user}')
                                await context.bot.send_message(chat_id=ADMIN_ID, text=f'Сообщение отправлено пользователю {user_id}: {message_to_user}')
                            else:
                                await context.bot.send_message(chat_id=ADMIN_ID, text='Пользователь не найден или не начал разговор.')
                        else:
                            await context.bot.send_message(chat_id=ADMIN_ID, text='Ошибка при получении сообщений от MockAPI.')
            else:
                await context.bot.send_message(chat_id=ADMIN_ID, text='ID пользователя должен быть числом.')
        else:
            await context.bot.send_message(chat_id=ADMIN_ID, text='Пожалуйста, укажите ID пользователя и сообщение.')
    else:
        await update.message.reply_text('Вы не имеете прав для отправки сообщений администратору.')

def main():
    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & ~filters.User(ADMIN_ID), forward_user_message))
    application.add_handler(MessageHandler(filters.TEXT & filters.User(ADMIN_ID), forward_admin_message))

    application.run_polling()

if __name__ == '__main__':
    main()
