#!/usr/bin/env python

import logging
import requests
from telegram import __version__ as TG_VER
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, WebAppInfo
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes
from server_manager import ServerManager
import yaml
from utils import load_config
import argparse
import datetime
import random
import asyncio

# Enable logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)


async def instructions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="""Download the applications below and import the generated link.
                                                                          <b>Android:</b> V2rayNG
                                                                          <b>IOS:</b> NapsternetV, shadowrocket
                                                                          <b>Windows:</b> v2rayN
                                                                          <b>MacOS:</b> V2RayXS """, parse_mode="HTML")
    
async def gen_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    maintenance = await is_maintenance(update, context)
    if maintenance:
        return
    
    if not update.effective_user.username:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Please setup a username for your telegram account.")
        return 
  
    if not await is_member(update, context, send_thank_you=False):
        return
    
    lock = asyncio.Lock()

    async with lock:
        urls = server_manager.generate_url(str(update.effective_user.id),str(update.effective_user.username)) 
   
    print(f'Gave link to @{update.effective_user.username}')
    if urls:
        for url in urls:
            if url['url']:
                await context.bot.send_message(chat_id=update.effective_chat.id, text=url['desc'])
                await context.bot.send_message(chat_id=update.effective_chat.id, text="`"+url['url']+"`", parse_mode="MarkdownV2")
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Something went wrong. Please try again in few mintues. If it happened again, please contact our support.")
        await context.bot.send_message(chat_id=update.effective_chat.id, text="مشکلی در ارتباط با سرورها پیش آمده. لطفا مجدد تکرار کنید.")

async def is_maintenance(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    config = load_config(config_path)
    if config['maintenance']:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry. The bot is under maintanance right now.")
        await context.bot.send_message(chat_id=update.effective_chat.id, text=".در حال ارتقا ربات هستیم. ربات بصورت موقتی غیرفعال است.")
        await context.bot.send_message(chat_id=update.effective_chat.id, text="در حال حاضر سرور پر شده است. ")

    return config['maintenance']

    
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a message with three inline buttons attached."""
    maintenance = await is_maintenance(update, context)
    if maintenance:
        return
    
    if not await is_member(update,context):
        return
        
    keyboard = [[InlineKeyboardButton("دریافت لینک شخصی", callback_data="gen_link")],
                [InlineKeyboardButton("گزارش استفاده", callback_data="usage")],
                [InlineKeyboardButton("رو چه نرم افزاری کار میکنه؟", callback_data="instructions")],
                [InlineKeyboardButton("می خواهم کمک کنم",url="https://t.me/+0l8_7FaM-UkyNzIx", callback_data="contribute")],
                [InlineKeyboardButton("لینک کانال", url="https://t.me/WomanLifeFreedomVPN",callback_data="contact_support")],
                [InlineKeyboardButton("تست سرعت", web_app=WebAppInfo(url="https://pcmag.speedtestcustom.com"))]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("Please choose one of the following options:", reply_markup=reply_markup)
    
async def gen_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="هنوز این دکمه پیاده سازی نشده است.")

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query

    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    await query.answer()
    if query.data == "instructions":
        await instructions(update, context)
    elif query.data == "gen_link":
        await gen_link(update,context)
    elif query.data == "usage":
        await gen_report(update, context)  


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Displays info on how to use the bot."""
    await update.message.reply_text("Use /start to test this bot.")

async def is_member(update: Update, context: ContextTypes.DEFAULT_TYPE, send_thank_you=True):
    # Check if the client is a member of the specified channel
    channel_id = '@WomanLifeFreedomVPN'  # The first argument is the channel ID
    user_id = update.effective_user.id # update.message.from_user.id  # Get the client's user ID
    chat_member = await context.bot.get_chat_member(chat_id=channel_id, user_id=user_id)
    if chat_member.status in ["member", "creator"]:
        if send_thank_you:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Thank you for subscribing to our channel!")
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Please subscribe to our channel @WomanLifeFreedomVPN.")
        await context.bot.send_message(chat_id=update.effective_chat.id, text="لطفا ابتدا عضو کانال شوید. این وی پی ان محدود به اعضای کانال می باشد.")
    return chat_member.status in ["member", "creator"]

def main() -> None:
    # Parse the config file path from the command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--config_path', help='Path to the config file', default='config.yaml')
    args = parser.parse_args()
    global config_path
    config_path = args.config_path
    global server_manager
    server_manager = ServerManager(config_path=config_path)
    # Load the config file
    config = load_config(config_path)    
      
    
    """Run the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(config['telegram_bot_token']).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))

    # Run the bot until the user presses Ctrl-C
    application.run_polling()


if __name__ == "__main__":
    main()

