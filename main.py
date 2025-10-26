import logging
import socket
import config
import os
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, ConversationHandler, MessageHandler, filters, ContextTypes
from requests import get

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)

# Commands:
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.chat_id in config.CHATIDLIST:
        await update.message.reply_text("I'm a bot, please talk to me!")

async def where(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f'Chat_id: {update.message.chat_id}')
    if update.message.chat_id in config.CHATIDLIST:
        ip_list = socket.gethostbyname_ex(socket.gethostname())
        await update.message.reply_text(f'Hostname: {ip_list[0]}')
        for number, ip in enumerate(ip_list[2]):
            msg = f'IP #{number + 1} - {ip}'
            await update.message.reply_text(msg)
        
        public_ip = get('https://api.ipify.org').text
        await update.message.reply_text(f'Public IP: {public_ip}')

async def getid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(str(update.message.chat_id))


SHUTDOWN = 1

async def shutdown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.chat_id in config.CHATIDLIST:
        yes_no = [['Yes', 'No']]
        await update.message.reply_text('Are you sure?', reply_markup=ReplyKeyboardMarkup(yes_no, one_time_keyboard=True))
        return SHUTDOWN
    else:
        return ConversationHandler.END

async def shutdown_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == 'Yes':
        await update.message.reply_text('Shutting system down', reply_markup=ReplyKeyboardRemove())
        
        # Execute appropriate shutdown command based on OS
        if os.name == 'nt':  # Windows
            os.system('shutdown /s /t 1')
        else:  # Linux/Unix
            os.system('sudo shutdown -h now')
            
    elif update.message.text == 'No':
        await update.message.reply_text('You can call me if you change your mind!', reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Cancelled')
    return ConversationHandler.END

def main():
    import asyncio
    
    # Create and set event loop for Windows
    if os.name == 'nt':  # Windows
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    # Create the Application
    application = Application.builder().token(config.TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('where', where))
    application.add_handler(CommandHandler('getid', getid))

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('shutdown', shutdown)],
        states={
            SHUTDOWN: [MessageHandler(filters.Regex('^(Yes|No)$'), shutdown_cmd)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    application.add_handler(conv_handler)

    print('IP Bot Started')
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()