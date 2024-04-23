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
import numpy as np
import keyboards


async def histplot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        stat = context.args[0]
    except IndexError:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Аргумент не передан.",
                                       reply_markup=ReplyKeyboardMarkup(keyboards.compare, one_time_keyboard=False))
        return "compare"
    db_sess = db_session.create_session()
    query = db_sess.query(SaveInfo).first()
    stat_list = []
    if stat not in query.intinfo:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Статистика не найдена.",
                                       reply_markup=ReplyKeyboardMarkup(keyboards.compare, one_time_keyboard=False))
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
    plt.savefig("./images/histplot.png")

    await context.bot.send_photo(chat_id=update.effective_chat.id, photo=open("./images/histplot.png", 'rb'),
                                 caption=f"{stat}",
                                 reply_markup=ReplyKeyboardMarkup(keyboards.compare, one_time_keyboard=False))
    return "compare"


async def scatter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 2:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Неверное количество параметров.")
        return "compare"
    stats = []
    for i in context.args:
        db_sess = db_session.create_session()
        query = db_sess.query(SaveInfo).first()
        hj = query.intinfo.split(',')
        check = []
        for j in hj:
            check.append(j.split('=')[0])
        if i not in check:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Статистика не найдена.",
                                           reply_markup=ReplyKeyboardMarkup(keyboards.compare, one_time_keyboard=False))
            return "compare"
        stats.append(i)
    stat1 = []
    stat2 = []
    n = []
    db_sess = db_session.create_session()
    query = db_sess.query(CompareList).filter(CompareList.id == update.effective_user.id).first()
    for i in query.countries.split(','):
        if not i:
            continue
        n.append(i)
        query = db_sess.query(SaveInfo).filter(SaveInfo.country == i).first()
        l = query.intinfo.split(',')
        for j in l:
            if stats[0] == j.split('=')[0]:
                stat1.append(float(j.split('=')[1]))
            elif stats[1] == j.split('=')[0]:
                stat2.append(float(j.split('=')[1]))

    x = np.array(stat1)
    y = np.array(stat2)
    plt.xlabel(stats[0])
    plt.ylabel(stats[1])
    plt.scatter(x, y)
    for i, t in enumerate(n):
        plt.annotate(t, (x[i], y[i]))
    plt.savefig("./images/scatter.png")
    plt.clf()
    plt.cla()
    await context.bot.send_photo(chat_id=update.effective_chat.id, photo=open("./images/scatter.png", 'rb'),
                                 caption=f"{stats[0], stats[1]}",
                                 reply_markup=ReplyKeyboardMarkup(keyboards.compare, one_time_keyboard=False))
    return "compare"
