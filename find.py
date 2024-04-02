import logging
import aiohttp
import pprint
import wikipedia
import wikipediaapi
import asyncio
from json import dump, dumps, load, loads
import translators as ts
from telegram.ext import Application, MessageHandler, filters, CommandHandler, ContextTypes, ConversationHandler
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Bot, KeyboardButton, Update, InputMediaPhoto
from config import BOT_TOKEN
from const import *


async def get_wiki(name):
    return await wikipedia.page("Austria")


async def pre_find(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Введите название страны на русском или английском языке, в любом регистре. /back для выхода в меню.")
    return "find"


async def find(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message.text.lower().capitalize()
    res = ts.translate_text(message, from_language="ru", to_language="en")
    response = await get_response_json(base_country1 + res, params={})
    if not response:
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text="Такая страна не найдена. Попробуйте ещё раз.")
        return "find"
    else:
        flag_url = response[0]["flags"]["png"]
        # wiki_response = await get_wiki(res)
        await context.bot.send_photo(chat_id=update.effective_chat.id, photo=flag_url, caption=message)
        return "find"


async def get_response_json(url, params):
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as resp:
            return await resp.json()


async def get_response_text(url, params):
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as resp:
            return await resp.text()
