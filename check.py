import logging
import aiohttp
from telegram.ext import Application, MessageHandler, filters, CommandHandler, ContextTypes, ConversationHandler
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Bot, KeyboardButton, Update, InputMediaPhoto
from data import db_session
from data.info_list import InfoList
from const import *


async def check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    country_list: list = context.user_data["clist"]
    print(country_list)
    try:
        idx = int(context.args[0]) - 1
    except IndexError:
        await update.message.reply_text("Не передан индекс.")
        return "info"
    except TypeError:
        await update.message.reply_text("Нужен численный аргумент.")
        return "info"
    except ValueError:
        await update.message.reply_text("Нужен численный аргумент.")
        return "info"
    if idx < 0 or idx >= len(country_list):
        await update.message.reply_text("Передан несуществующий индекс.")
        return "info"
    if len(context.args) > 1:
        await update.message.reply_text("Слишком много аргументов.")
        return "info"
    print(idx)
    country = country_list[idx]
    print(country)
    response = await get_response_json(base_country1 + country, params={})
    info = response[0]
    info_dict = {"Название": info["name"]["common"], "Официальное название": info["name"]["official"],
                 "Валюта": info["currencies"], "Телефонный код": info["idd"], "Столица": info["capital"],
                 "Регион": info["region"], "Субрегион": info["subregion"], "Язык": info["languages"],
                 "Площадь": info["area"], "Демонимы": info["demonyms"]["eng"], "Карта": info["maps"]["googleMaps"],
                 "Население": info["population"], "Часовые пояса": info["timezones"], "Континент": info["continents"],
                 "Флаг": info["flags"]["png"]}
    context.user_data["info"] = info_dict
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text="Напишите характеристику страны. Список доступных характеристик /chlist")
    return "check"


async def handleCheck(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message.text
    info_dict: dict = context.user_data["info"]
    if message not in info_dict.keys():
        await update.message.reply_text("Такой характеристики не найдено. Попробуйте снова.")
        return "check"
    if message == "Флаг":
        await context.bot.send_photo(chat_id=update.effective_chat.id, photo=info_dict[message])
        return "check"
    elif message == "Валюта":
        ans = ""
        print(info_dict[message])
        for i in info_dict[message].values():
            ans += i["name"] + ' ' + i["symbol"] + '\n'
        await context.bot.send_message(chat_id=update.effective_chat.id, text=ans)
        return "check"
    elif message == "Телефонный код":
        ans = ""
        for i in info_dict[message]["suffixes"]:
            ans += info_dict[message]["root"] + i + '\n'
        await context.bot.send_message(chat_id=update.effective_chat.id, text=ans)
        return "check"
    elif message == "Язык":
        await context.bot.send_message(chat_id=update.effective_chat.id, text=", ".join(info_dict[message].values()))
        return "check"
    elif message == "Демонимы":
        ans = f'Female: {info_dict[message]["f"]}, Male: {info_dict[message]["m"]}'
        await context.bot.send_message(chat_id=update.effective_chat.id, text=ans)
        return "check"
    elif type(info_dict[message]) == list:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=", ".join(info_dict[message]))
        return "check"
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=str(info_dict[message]))
        return "check"


async def command_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    info_dict: dict = context.user_data["info"]
    await context.bot.send_message(chat_id=update.effective_chat.id, text=", ".join(info_dict.keys()))


async def get_response_json(url, params):
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as resp:
            return await resp.json()
