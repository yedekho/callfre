import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters, ConversationHandler

# States
FIRST_NUMBER = 0
OPERATION = 1
SECOND_NUMBER = 2

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Welcome to Calculator Bot! Please enter your first number:")
    return FIRST_NUMBER

async def first_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        num = float(update.message.text)
        context.user_data['first_number'] = num
        
        # Create inline keyboard for operations
        keyboard = [
            [
                InlineKeyboardButton("Add (+)", callback_data="add"),
                InlineKeyboardButton("Subtract (-)", callback_data="subtract")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "What operation would you like to perform?",
            reply_markup=reply_markup
        )
        return OPERATION
    except ValueError:
        await update.message.reply_text("Please enter a valid number!")
        return FIRST_NUMBER

async def operation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    context.user_data['operation'] = query.data
    await query.message.reply_text("Please enter your second number:")
    return SECOND_NUMBER

async def second_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        num = float(update.message.text)
        first_num = context.user_data['first_number']
        operation = context.user_data['operation']
        
        if operation == "add":
            result = first_num + num
            symbol = "+"
        else:
            result = first_num - num
            symbol = "-"
            
        # Create restart button
        keyboard = [[InlineKeyboardButton("Start New Calculation", callback_data="restart")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f"{first_num} {symbol} {num} = {result}",
            reply_markup=reply_markup
        )
        return ConversationHandler.END
    except ValueError:
        await update.message.reply_text("Please enter a valid number!")
        return SECOND_NUMBER

async def restart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.message.reply_text("Welcome back! Please enter your first number:")
    return FIRST_NUMBER

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Calculator stopped. Type /start to begin again.")
    return ConversationHandler.END

def main():
    # Get token from environment variable
    TOKEN = os.getenv("BOT_TOKEN", "8065931942:AAFqsAZvQ78V0rs6fAuz3SFW0BedUUVkhsY")
    
    # Initialize bot with your token
    application = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            FIRST_NUMBER: [MessageHandler(filters.TEXT & ~filters.COMMAND, first_number)],
            OPERATION: [CallbackQueryHandler(operation)],
            SECOND_NUMBER: [MessageHandler(filters.TEXT & ~filters.COMMAND, second_number)],
        },
        fallbacks=[
            CommandHandler("cancel", cancel),
            CallbackQueryHandler(restart, pattern="^restart$")
        ],
    )

    application.add_handler(conv_handler)
    
    # Start the bot
    application.run_polling()

if __name__ == "__main__":
    main()