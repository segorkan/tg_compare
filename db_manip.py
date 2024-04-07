import logging
from telegram.ext import Application, MessageHandler, filters, CommandHandler, ContextTypes, ConversationHandler
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Bot, KeyboardButton, Update, InputMediaPhoto
from data import db_session
from data.info_list import InfoList
from data.compare_list import CompareList


async def add_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    add_country = context.user_data["last_country"]
    db_sess = db_session.create_session()
    infoitem = db_sess.query(InfoList).filter(InfoList.id == update.effective_user.id).first()
    if add_country not in infoitem.countries:
        infoitem.countries += add_country + ','
    db_sess.commit()
    infoitem = db_sess.query(InfoList).filter(InfoList.id == update.effective_user.id).first()
    print(infoitem.countries)
    await update.message.reply_text(
        "Страна добавлена в info_list. /back для возвращения в меню, /find для нового поиска.")
    return "endfind"


async def add_compare(update: Update, context: ContextTypes.DEFAULT_TYPE):
    add_country = context.user_data["last_country"]
    db_sess = db_session.create_session()
    comitem = db_sess.query(CompareList).filter(CompareList.id == update.effective_user.id).first()
    if add_country not in comitem.countries:
        comitem.countries += add_country + ','
    db_sess.commit()
    infoitem = db_sess.query(InfoList).filter(InfoList.id == update.effective_user.id).first()
    print(infoitem.countries)
    await update.message.reply_text(
        "Страна добавлена в compare_list. /back для возвращения в меню, /find для нового поиска.")
    return "endfind"


async def info_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    send_str = ""
    db_sess = db_session.create_session()
    infoitem = db_sess.query(InfoList).filter(InfoList.id == update.effective_user.id).first()
    country_list = infoitem.countries[:len(infoitem.countries) - 1].split(',')
    context.user_data["clist"] = country_list
    for i in range(len(country_list)):
        send_str += str(i + 1) + '. ' + country_list[i] + '\n'
    await update.message.reply_text("Вы можете получить какую-то информацию о странах из списка.")
    await context.bot.send_message(chat_id=update.effective_chat.id, text=send_str)
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text="""/check [номер страны] - посмотреть информацию о стране. 
                                   /delete [номер страны] - удалить страну из спиcка.""")
    return "info"


async def compare_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    send_str = ""
    db_sess = db_session.create_session()
    comitem = db_sess.query(CompareList).filter(CompareList.id == update.effective_user.id).first()
    country_list = comitem.countries[:len(comitem.countries) - 1].split(',')
    context.user_data["clist"] = country_list
    for i in range(len(country_list)):
        send_str += str(i + 1) + '. ' + country_list[i] + '\n'
    await update.message.reply_text("Вы можете выбрать какие-то страны для детального сравнения.")
    await context.bot.send_message(chat_id=update.effective_chat.id, text=send_str)
    return "compare"


async def info_delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    country_list: list = context.user_data["clist"]
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

    db_sess = db_session.create_session()
    infoitem = db_sess.query(InfoList).filter(InfoList.id == update.effective_user.id).first()
    country_list.remove(country_list[idx])
    final_str = ",".join(country_list) + ','
    print(final_str)
    infoitem.countries = final_str
    db_sess.commit()
    context.user_data["clist"] = country_list
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Страна была удалена.")
    return "info"


async def comp_delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    country_list: list = context.user_data["clist"]
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

    db_sess = db_session.create_session()
    comitem = db_sess.query(CompareList).filter(CompareList.id == update.effective_user.id).first()
    country_list.remove(country_list[idx])
    final_str = ",".join(country_list) + ','
    print(final_str)
    comitem.countries = final_str
    db_sess.commit()
    context.user_data["clist"] = country_list
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Страна была удалена.")
    return "info"
