import logging
import aiohttp
import prettytable as pt
from telegram.constants import ParseMode
from telegram.ext import Application, MessageHandler, filters, CommandHandler, ContextTypes, ConversationHandler
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Bot, KeyboardButton, Update, InputMediaPhoto
from data import db_session
from const import *
from data.save_info import SaveInfo
from config import API_KEY
import translators as ts


def is_float(string):
    try:
        float(string)
        return True
    except ValueError:
        return False
    except TypeError:
        return False


async def init(country_list):
    db_sess = db_session.create_session()
    for i in country_list:
        saveitem = db_sess.query(SaveInfo).filter(SaveInfo.country == i).first()
        if not saveitem:
            response = await get_response_json(base_country2 + i, params={"X-Api-Key": API_KEY})
            intinfo = ""
            print(response)
            for k, v in response[0].items():
                print(k, v)
                if is_float(v):
                    intinfo += str(k) + '=' + str(v) + ','
            intinfo = intinfo[:(len(intinfo) - 1)]
            saveitem = SaveInfo()
            saveitem.country = i
            saveitem.intinfo = intinfo
            db_sess.add(saveitem)
            db_sess.commit()
        saveitem = db_sess.query(SaveInfo).filter(SaveInfo.country == i).first()
        print(saveitem.country, saveitem.intinfo)


async def chars(update: Update, context: ContextTypes.DEFAULT_TYPE):
    country_list: list = context.user_data["clist"]
    try:
        idx = int(context.args[0]) - 1
    except IndexError:
        await update.message.reply_text("Не передан индекс.")
        return "compare"
    except TypeError:
        await update.message.reply_text("Нужен численный аргумент.")
        return "compare"
    except ValueError:
        await update.message.reply_text("Нужен численный аргумент.")
        return "compare"
    if idx < 0 or idx >= len(country_list):
        await update.message.reply_text("Передан несуществующий индекс.")
        return "compare"
    if len(context.args) > 1:
        await update.message.reply_text("Слишком много аргументов.")
        return "compare"
    db_sess = db_session.create_session()
    saveitem = db_sess.query(SaveInfo).filter(SaveInfo.country == country_list[idx]).first()
    item_list = saveitem.intinfo.split(',')
    ans = ""
    for i in item_list:
        k, v = i.split('=')
        ans += k + " = " + v + '\n'
    await context.bot.send_message(chat_id=update.effective_chat.id, text=ans)
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Возвращение в меню compare_list.")
    return "compare"


async def versus(update: Update, context: ContextTypes.DEFAULT_TYPE):
    country_list: list = context.user_data["clist"]
    new_list = []
    if len(context.args) == 0:
        await update.message.reply_text("Не переданы аргументы.")
        return "compare"
    for i in context.args:
        try:
            idx = int(i) - 1
        except TypeError:
            await update.message.reply_text("Нужен численный аргумент.")
            return "compare"
        except ValueError:
            await update.message.reply_text("Нужен численный аргумент.")
            return "compare"
        if idx < 0 or idx >= len(country_list):
            await update.message.reply_text("Передан несуществующий индекс.")
            return "compare"
        new_list.append(country_list[idx])
    new_list.insert(0, '')
    table = pt.PrettyTable(new_list)
    data = []
    for i in new_list:
        if not i:
            continue
        db_sess = db_session.create_session()
        saveitem = db_sess.query(SaveInfo).filter(SaveInfo.country == i).first()
        data.append(saveitem.intinfo.split(','))
    for i in range(len(data[0])):
        add = [data[0][i].split('=')[0]]
        maxi = -1
        for j in range(len(data)):
            maxi = max(float(data[j][i].split('=')[1]), maxi)
        for j in range(len(data)):
            cur = data[j][i].split('=')[1]
            if cur == maxi:
                add.append(f"<b>{data[j][i].split('=')[1]}</b>")
            else:
                add.append(data[j][i].split('=')[1])
        table.add_row(add)

    await context.bot.send_message(chat_id=update.effective_chat.id, text=f'<pre>{table}</pre>',
                                   parse_mode=ParseMode.HTML)


async def get_response_json(url, params):
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as resp:
            return await resp.json()
