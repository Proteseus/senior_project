import os
import sys
import time
import asyncio
import logging
import tracemalloc

from dotenv import load_dotenv
import requests

from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton, Bot, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand, BotCommandScopeChat
from telegram.ext import Application, CallbackContext, CallbackQueryHandler, CommandHandler, ConversationHandler, filters, MessageHandler, Updater

load_dotenv()

sys.path.append(os.getcwd())

from bot import Bot as BT
from app.file_processor.chunker import Chunker
from app.file_processor.vectorizer import Vectorizer

TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=[logging.INFO, logging.ERROR])
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

FILES, DELETE_SELECTED, DELETE_ALL  = range(3)

async def start(update: Update, context: CallbackContext):
    await context.bot.set_my_commands(
        commands=[
            BotCommand('start', 'Initialize bot'),
            BotCommand('add_files', 'Add Files to Read'),
            BotCommand('delete_files', 'Delete Files from Read'),
            BotCommand('delete_all_files', 'Delete All Files from Read'),
            BotCommand('cancel', 'End Conversation'),
        ],
        scope=BotCommandScopeChat(chat_id=update.effective_chat.id)
    )
    
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Welcome to Reno!\nPress the menu and start setting up the bot"
    )
    
    if not os.path.exists(f'{os.getcwd()}/files/{update.effective_chat.id}'):
        os.makedirs(f'{os.getcwd()}/files/{update.effective_chat.id}')
        
        logger.info("Files directory created for %s", update.effective_chat.id)
        
    if not os.path.exists(f'{os.getcwd()}/vectors/{update.effective_chat.id}'):
        os.makedirs(f'{os.getcwd()}/vectors/{update.effective_chat.id}')
        
        logger.info("Vectors directory created for %s", update.effective_chat.id)

    logger.info("Bot initialized for %s", update.effective_chat.id)

async def add_files(update: Update, context: CallbackContext) -> None:
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Send me a document"
    )
    
    logger.info("Adding files for %s", update.effective_chat.id)
    
    return FILES

async def files_(update: Update, context: CallbackContext) -> None:
    file = await context.bot.get_file(update.message.document.file_id)
    
    logger.info("file_id: %s", update.message.document.file_id)
    logger.info("file_size: %s", update.message.document.file_size)
    logger.info("file_name: %s", update.message.document.file_name)
    
    await file.download_to_drive(custom_path=f'{os.getcwd()}/files/{update.effective_chat.id}/{update.message.document.file_name}')
    
    while not os.path.exists(f'{os.getcwd()}/files/{update.effective_chat.id}/{update.message.document.file_name}'):
        time.sleep(1)
        
    logger.info("File %s downloaded", update.message.document.file_name)
    
    await chunk_and_vectorize(update=update, context=context, fileName=update.message.document.file_name)

async def chunk_and_vectorize(update: Update, context: CallbackContext, fileName):
    context.user_data['file'] = str(update.effective_chat.id) + '/' + fileName
    files = f'{os.getcwd()}/files/{update.effective_chat.id}/{update.message.document.file_name}'
    
    if not os.path.exists(f'{os.getcwd()}/vectors/{update.effective_chat.id}/{fileName[:-4]}.pkl'):
        api_endpoint = os.getenv('FILE_PROCESSOR_API')
        
        await update.message.reply_text('Please wait while the bot is processing your file...')
        
        with open(files, 'rb') as f:
            response = requests.post(f'{api_endpoint}/file/upload/', files={'file': f}, data={'chat_id': update.effective_chat.id})

        # Handle the API response accordingly
        if response.status_code == 200:
            await update.message.reply_text('File uploaded and processed successfully.')
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="You can now ask your questions:"
            )
        
        else:
            await update.message.reply_text('Error uploading file to the server.')

    return ConversationHandler.END

async def reply(update: Update, context: CallbackContext):
    bot = BT()
    # context.user_data['file'] = str(update.effective_chat.id) + '/Galactic Empires Pythonic Dreams.txt'
    vectorIndex = Vectorizer(file_path=context.user_data['file']).load_index()
    
    if vectorIndex:
        try:
            response = bot.get_response(vectorIndex=vectorIndex, query=update.message.text)
            
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"{response['answer']}\n{response['sources']}"
            )
            
            logger.info("Answer: %s", response['answer'])
            logger.info("Sources: %s", response['sources'])
        except Exception as e:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Error: " + str(e)
            )
            
            logger.error("Error: %s", e)
    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="No index found"
        )
        
        logger.info("No index found")

async def delete_files(update: Update, context: CallbackContext):
    file_list = os.listdir(f'{os.getcwd()}/files/{update.effective_chat.id}')
    if file_list:
        keyboard = [[InlineKeyboardButton(file, callback_data=file)] for file in file_list]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Please select a file to delete:",
            reply_markup=reply_markup
        )
        return DELETE_SELECTED
    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="No files found"
        )
        
    return ConversationHandler.END

async def delete_selected_file(update: Update, context: CallbackContext):
    query = update.callback_query
    selected_file = query.data
    
    os.remove(f'{os.getcwd()}/files/{update.effective_chat.id}/{selected_file}')
    os.remove(f'{os.getcwd()}/vectors/{update.effective_chat.id}/{selected_file[:-4]}.pkl')
    
    await query.answer()
    await context.bot.edit_message_text(
        message_id=query.message.message_id,
        chat_id=update.effective_chat.id,
        text=f"File {selected_file} deleted"
    )
    
    logger.info("File %s deleted", selected_file)
    
    return ConversationHandler.END

async def delete_all_files(update: Update, context: CallbackContext):
    file_list = os.listdir(f'{os.getcwd()}/files/{update.effective_chat.id}')
    if file_list:
        for file in os.listdir(f'{os.getcwd()}/files/{update.effective_chat.id}'):
            os.remove(f'{os.getcwd()}/files/{update.effective_chat.id}/{file}')
        
        for file in os.listdir(f'{os.getcwd()}/vectors/{update.effective_chat.id}'):
            os.remove(f'{os.getcwd()}/vectors/{update.effective_chat.id}/{file}')
        
        
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="All files deleted"
        )
        
        logger.info("All files deleted")
    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="No files found"
        )
        
    return ConversationHandler.END

async def cancel(update: Update, context: CallbackContext) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    await update.message.reply_text(
        "Bye! I hope we can talk again some day.",
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END

# Define an error handler function
async def error(update, context):
    """Log errors."""
    logging.error(f'Update {update} caused error {context.error}')

def main():
    application = Application.builder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    
    file_add = ConversationHandler(
        entry_points=[CommandHandler('add_files', add_files)],
        states={
            FILES: [MessageHandler(filters.ATTACHMENT, files_)]
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )
    
    file_delete = ConversationHandler(
        entry_points=[CommandHandler('delete_files', delete_files)],
        states={
            DELETE_SELECTED: [CallbackQueryHandler(delete_selected_file)],
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )
    
    application.add_handler(CommandHandler('delete_all_files', delete_all_files))
    
    application.add_handler(file_add)
    application.add_handler(file_delete)
    application.add_handler(MessageHandler(filters.TEXT, reply))
    application.add_error_handler(error)
    
    # Run bot
    application.run_polling(allowed_updates=Update.ALL_TYPES, poll_interval=1.0)

if __name__ == '__main__':
    tracemalloc.start()
    
    main()
    
    tracemalloc.stop()
    print(tracemalloc.get_object_traceback())