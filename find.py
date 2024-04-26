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
import keyboards


class WrongPageException(Exception):
    "Raised when API has found a country because of translator addition but a page cannot be found in Wikipedia"
    pass


async def pre_find(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Введите название страны на русском или английском языке, в любом регистре. /back для выхода в меню.",
        reply_markup=ReplyKeyboardMarkup(keyboards.find, one_time_keyboard=False))
    return "find"


def capitalize_string(name):
    temp = []
    for i in name.split():
        if len(i) > 1:
            temp.append(i.capitalize())
        else:
            temp.append(i)

    return " ".join(temp)


async def with_threads(res_rus):
    wiki_request = "1"

    def make_request():
        global wiki_request
        wiki_wiki = wikipediaapi.Wikipedia(
            user_agent='TgCompareBot (test@example.com)',
            language='ru',
            extract_format=wikipediaapi.ExtractFormat.WIKI
        )
        wiki_request = str(wiki_wiki.page(res_rus).summary)
        print("IN ASYNC FUNCTION " + wiki_request)

    reqs = [asyncio.to_thread(make_request) for _ in range(1)]
    await asyncio.gather(*reqs)
    return wiki_request


async def find(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message.text.lower().capitalize()
    res_eng = ts.translate_text(message, from_language="ru", to_language="en")
    res_rus = ts.translate_text(message, from_language="en", to_language="ru")
    res_rus = capitalize_string(res_rus)
    context.user_data["last_country"] = res_eng
    response = await get_response_json(base_country1 + res_eng + "?fullText=true", params={})
    if len(response) > 1:
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text="Такая страна не найдена. Попробуйте ещё раз.",
                                       reply_markup=ReplyKeyboardMarkup(keyboards.find, one_time_keyboard=False))
        return "find"
    else:
        try:
            flag_url = response[0]["flags"]["png"]
        except KeyError:
            await context.bot.send_message(chat_id=update.effective_chat.id,
                                           text="Такая страна не найдена. Попробуйте ещё раз.",
                                           reply_markup=ReplyKeyboardMarkup(keyboards.find, one_time_keyboard=False))
            return "find"
        print(res_rus)
        wiki_wiki = wikipediaapi.Wikipedia(
            user_agent='TgCompareBot (test@example.com)',
            language='ru',
            extract_format=wikipediaapi.ExtractFormat.WIKI
        )
        wiki_response = str(wiki_wiki.page(res_rus).summary)
        print(wiki_response)
        try:
            check = False
            accept = ["государство", "страна", "регион", "автономия", "область", "район"]
            for i in accept:
                if i in wiki_response:
                    check = True
            if not check:
                raise WrongPageException
        except WrongPageException:
            await context.bot.send_message(chat_id=update.effective_chat.id,
                                           text="Такая страна не найдена. Попробуйте ещё раз.",
                                           reply_markup=ReplyKeyboardMarkup(keyboards.find, one_time_keyboard=False))
            return "find"
        wiki_text = ". ".join(wiki_response.split(". ")[:MAX_SENTENCES]) + '.'
        await context.bot.send_photo(chat_id=update.effective_chat.id, photo=flag_url, caption=message)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=wiki_text)
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text="/find - новый поиск, /add_info - добавить в info_list, /add_compare - добавить в compare_list, "
                                            "/back - обратно в меню",
                                       reply_markup=ReplyKeyboardMarkup(keyboards.rfind, one_time_keyboard=False))
        return "rfind"


async def get_response_json(url, params):
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as resp:
            return await resp.json()


async def get_response_text(url, params):
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as resp:
            return await resp.text()
