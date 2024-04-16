import logging
import aiohttp
from telegram.ext import Application, MessageHandler, filters, CommandHandler, ContextTypes, ConversationHandler
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Bot, KeyboardButton, Update, InputMediaPhoto
from data import db_session
from data.info_list import InfoList
from data.compare_list import CompareList
from data.save_info import SaveInfo
from const import *
import matplotlib.pyplot as plt


async def histplot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        stat = context.args[0]
    except IndexError:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Аргумент не передан.")
        return "compare"
    db_sess = db_session.create_session()
    query = db_sess.query(SaveInfo).first()
    stat_list = []
    if stat not in query.intinfo:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Статистика не найдена.")
        return "compare"
    query = db_sess.query(CompareList).filter(CompareList.id == update.effective_user.id).first()
    for i in query.countries.split(','):
        if not i:
            continue
        query = db_sess.query(SaveInfo).filter(SaveInfo.country == i).first()
        l = query.intinfo.split(',')
        for j in l:
            if stat == j.split('=')[0]:
                stat_list.append(float(j.split('=')[1]))

    cs = db_sess.query(CompareList).filter(CompareList.id == update.effective_user.id).first().countries.split(',')
    cs = cs[:len(cs) - 1]
    fig = plt.figure(figsize=(10, 5))
    plt.bar(cs, stat_list, color="maroon", width=0.4)
    plt.xlabel("Страны")
    plt.ylabel(f"Значение характеристики {stat}")
    plt.title(f"Гистограмма характеристики {stat}")
    plt.savefig("./images/plot.png")

    await context.bot.send_photo(chat_id=update.effective_chat.id, photo=open("./images/plot.png", 'rb'),
                                 caption=f"{stat}")
    return "compare"


async def scatter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 2:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Неверное количество параметров.")
        return "compare"
    for i in context.args:
        pass

