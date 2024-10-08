from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import aiohttp

# Ваш токен бота
TOKEN = '7435741097:AAEVsd3t6sgkNUQoAWAO8NKvhdMmfCVv0S4'
# Ваш ID (администратора)
ADMIN_ID = 1604384939

# URL MockAPI
MOCKAPI_URL = 'https://6703f9f6ab8a8f8927327c94.mockapi.io/chat_users'

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Привет! Все ваши сообщения будут отправлены администратору.')

async def forward_user_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.chat.id
    message_text = update.message.text
    
    # Отправляем сообщение на MockAPI
    async with aiohttp.ClientSession() as session:
        async with session.post(MOCKAPI_URL, json={"user_id": user_id, "message": message_text}) as response:
            if response.status == 201:
                await context.bot.send_message(chat_id=ADMIN_ID, text=f'Сообщение от пользователя {user_id}: {message_text}')
                await update.message.reply_text(
                    '✉️ Ваше сообщение было успешно отправлено администратору!\n'
                    'Пожалуйста, подождите, пока мы подготовим для вас ответ.\n'
                    'Мы ценим ваше терпение! 🌟'
                )
            else:
                await update.message.reply_text('Произошла ошибка при отправке сообщения.')

async def forward_admin_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message.chat.id == ADMIN_ID:
        if update.message.text:  # Если это текстовое сообщение
            parts = update.message.text.split(maxsplit=1)
            user_id = int(parts[0]) if len(parts) > 0 and parts[0].isdigit() else None
            message_to_user = parts[1] if len(parts) > 1 else ""

            if user_id is not None:
                async with aiohttp.ClientSession() as session:
                    async with session.get(MOCKAPI_URL) as response:
                        if response.status == 200:
                            messages = await response.json()
                            user_messages = [msg for msg in messages if msg['user_id'] == user_id]

                            if user_messages:
                                if message_to_user:
                                    await context.bot.send_message(chat_id=user_id, text=f'📝 Ответ от администратора:\n\n{message_to_user}')
                                    await context.bot.send_message(chat_id=ADMIN_ID, text=f'Сообщение отправлено пользователю {user_id}:\n\n{message_to_user}')
                                else:
                                    await context.bot.send_message(chat_id=ADMIN_ID, text='Сообщение пустое, не отправлено.')
                            else:
                                await context.bot.send_message(chat_id=ADMIN_ID, text='Пользователь не найден или не начал разговор.')
                        else:
                            await context.bot.send_message(chat_id=ADMIN_ID, text='Ошибка при получении сообщений от MockAPI.')
        elif update.message.document:  # Если это документ
            user_id = int(update.message.caption.split()[0]) if update.message.caption else None
            if user_id is not None:
                await context.bot.send_document(chat_id=user_id, document=update.message.document.file_id)
                await context.bot.send_message(chat_id=ADMIN_ID, text=f'Документ отправлен пользователю {user_id}.')
            else:
                await context.bot.send_message(chat_id=ADMIN_ID, text='Пожалуйста, укажите корректный ID пользователя в подписи к документу.')
        elif update.message.photo:  # Если это фото
            user_id = int(update.message.caption.split()[0]) if update.message.caption else None
            if user_id is not None:
                await context.bot.send_photo(chat_id=user_id, photo=update.message.photo[-1].file_id)  # Отправка самого высокого качества
                await context.bot.send_message(chat_id=ADMIN_ID, text=f'Фото отправлено пользователю {user_id}.')
            else:
                await context.bot.send_message(chat_id=ADMIN_ID, text='Пожалуйста, укажите корректный ID пользователя в подписи к фото.')
    else:
        await update.message.reply_text('Вы не имеете прав для отправки сообщений администратору.')

def main():
    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & ~filters.User(ADMIN_ID), forward_user_message))

    # Для текстовых сообщений
    application.add_handler(MessageHandler(filters.User(ADMIN_ID) & filters.TEXT, forward_admin_message))
    # Для документов
    application.add_handler(MessageHandler(filters.User(ADMIN_ID) & filters.Document.ALL, forward_admin_message))  # Исправлено
    # Для фото
    # application.add_handler(MessageHandler(filters.User(ADMIN_ID) & filters.Photo.ALL, forward_admin_message))  # Исправлено

    application.run_polling()

if __name__ == '__main__':
    main()
