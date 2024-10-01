from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Ваш токен бота
TOKEN = '7435741097:AAEVsd3t6sgkNUQoAWAO8NKvhdMmfCVv0S4'
# Ваш ID (администратора)
ADMIN_ID = 1604384939

# Словарь для хранения chat_id пользователей
user_messages = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.chat.id
    user_messages[user_id] = user_id  # Сохраняем ID пользователя
    await update.message.reply_text('Привет! Все ваши сообщения будут отправлены администратору.')

async def forward_user_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.chat.id
    # Пересылаем сообщение администратору
    await context.bot.send_message(chat_id=ADMIN_ID, text=f'Сообщение от пользователя {user_id}: {update.message.text}')
    # Отправляем пользователю уведомление
    await update.message.reply_text('Ваше сообщение было отправлено администратору.')

async def forward_admin_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Проверяем, что сообщение отправлено администратором
    if update.message.chat.id == ADMIN_ID:
        # await update.message.reply_text('forward_admin_message вызвана.')
        # await context.bot.send_message(chat_id=ADMIN_ID, text=f'ADMIN_ID: {ADMIN_ID}')  # Отправляем ADMIN_ID

        parts = update.message.text.split()

        # Проверяем, указал ли администратор ID пользователя
        if len(parts) > 1:
            # Извлекаем ID пользователя из первого слова
            user_id = parts[0]
            message_to_user = ' '.join(parts[1:])  # Остальная часть сообщения

            # Убедимся, что user_id является числом
            if user_id.isdigit():
                user_id = int(user_id)  # Преобразуем в целое число

                # Проверяем, существует ли пользователь в словаре
                if user_id in user_messages:
                    # Отправляем сообщение пользователю
                    await context.bot.send_message(chat_id=user_id, text=f'Ответ от администратора: {message_to_user}')
                    # Уведомляем администратора о том, что сообщение отправлено
                    await context.bot.send_message(chat_id=ADMIN_ID, text=f'Сообщение отправлено пользователю {user_id}: {message_to_user}')
                else:
                    # Уведомляем администратора, если пользователь не найден
                    await context.bot.send_message(chat_id=ADMIN_ID, text='Пользователь не найден или не начал разговор.')
            else:
                # Уведомляем администратора, если ID не является числом
                await context.bot.send_message(chat_id=ADMIN_ID, text='ID пользователя должен быть числом.')
        else:
            # Уведомляем администратора, если не указаны ID и сообщение
            await context.bot.send_message(chat_id=ADMIN_ID, text='Пожалуйста, укажите ID пользователя и сообщение.')
    else:
        # Если сообщение отправлено не администратором
        await update.message.reply_text('Вы не имеете прав для отправки сообщений администратору.')

def main():
    # Создаем приложение
    application = ApplicationBuilder().token(TOKEN).build()

    # Обработчики команд и сообщений
    application.add_handler(CommandHandler("start", start))
    
    # Обработчик сообщений от пользователей
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & ~filters.User(ADMIN_ID), forward_user_message))
    
    # Обработчик сообщений от администратора
    application.add_handler(MessageHandler(filters.TEXT & filters.User(ADMIN_ID), forward_admin_message))

    # Запускаем бота
    application.run_polling()

if __name__ == '__main__':
    main()
