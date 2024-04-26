import logging
import asyncio
from telegram.ext import Application, MessageHandler, filters, CommandHandler, ContextTypes, ConversationHandler
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Bot, KeyboardButton, Update, InputMediaPhoto
from data import db_session
from data.info_list import InfoList
from data.compare_list import CompareList
from compare import init
import keyboards


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
        "Страна добавлена в info_list. /back для возвращения в меню, /find для нового поиска.",
        reply_markup=ReplyKeyboardMarkup(keyboards.endfind, one_time_keyboard=False))
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
        "Страна добавлена в compare_list. /back для возвращения в меню, /find для нового поиска.",
        reply_markup=ReplyKeyboardMarkup(keyboards.endfind, one_time_keyboard=False))
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
                                   /delete [номер страны] - удалить страну из спиcка.""",
                                   reply_markup=ReplyKeyboardMarkup(keyboards.info, one_time_keyboard=False))
    return "info"


async def compare_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    send_str = ""
    db_sess = db_session.create_session()
    comitem = db_sess.query(CompareList).filter(CompareList.id == update.effective_user.id).first()
    country_list = comitem.countries[:len(comitem.countries) - 1].split(',')
    context.user_data["clist"] = country_list
    for i in range(len(country_list)):
        send_str += str(i + 1) + '. ' + country_list[i] + '\n'
    await asyncio.gather(asyncio.create_task(init(country_list)))
    await update.message.reply_text("Вы можете выбрать какие-то страны для детального сравнения.")
    await context.bot.send_message(chat_id=update.effective_chat.id, text=send_str)
    await context.bot.send_message(chat_id=update.effective_chat.id, text="""/delete [id] - удалить страну под номером id из списка
/chars [id] - численные характеристики 
/versus [id1] [id2] ... - сравнение всех характеристик переданных стран и нахождение лучшей страны для каждой характеристики
/histplot [stat] - построение гистограммы в порядке сортировки статистики stat всех стран в compare_list.
/scatter [stat1] [stat2] - scatter график, ось абсцисс - stat1, ось ординат - stat2 """,
                                   reply_markup=ReplyKeyboardMarkup(keyboards.compare, one_time_keyboard=False))
    return "compare"


async def info_delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    country_list: list = context.user_data["clist"]
    try:
        idx = int(context.args[0]) - 1
    except IndexError:
        await update.message.reply_text("Не передан индекс.",
                                        reply_markup=ReplyKeyboardMarkup(keyboards.info, one_time_keyboard=False))
        return "info"
    except TypeError:
        await update.message.reply_text("Нужен численный аргумент.",
                                        reply_markup=ReplyKeyboardMarkup(keyboards.info, one_time_keyboard=False))
        return "info"
    except ValueError:
        await update.message.reply_text("Нужен численный аргумент.",
                                        reply_markup=ReplyKeyboardMarkup(keyboards.info, one_time_keyboard=False))
        return "info"
    if idx < 0 or idx >= len(country_list):
        await update.message.reply_text("Передан несуществующий индекс.",
                                        reply_markup=ReplyKeyboardMarkup(keyboards.info, one_time_keyboard=False))
        return "info"
    if len(context.args) > 1:
        await update.message.reply_text("Слишком много аргументов.",
                                        reply_markup=ReplyKeyboardMarkup(keyboards.info, one_time_keyboard=False))
        return "info"

    db_sess = db_session.create_session()
    infoitem = db_sess.query(InfoList).filter(InfoList.id == update.effective_user.id).first()
    country_list.remove(country_list[idx])
    final_str = ",".join(country_list) + ','
    print(final_str)
    infoitem.countries = final_str
    db_sess.commit()
    context.user_data["clist"] = country_list
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text="Страна была удалена. Возвращение в /info_list.",
                                   reply_markup=ReplyKeyboardMarkup(keyboards.info, one_time_keyboard=False))
    return "info"


async def comp_delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    country_list: list = context.user_data["clist"]
    try:
        idx = int(context.args[0]) - 1
    except IndexError:
        await update.message.reply_text("Не передан индекс.",
                                        reply_markup=ReplyKeyboardMarkup(keyboards.compare, one_time_keyboard=False))
        return "compare"
    except TypeError:
        await update.message.reply_text("Нужен численный аргумент.",
                                        reply_markup=ReplyKeyboardMarkup(keyboards.compare, one_time_keyboard=False))
        return "compare"
    except ValueError:
        await update.message.reply_text("Нужен численный аргумент.",
                                        reply_markup=ReplyKeyboardMarkup(keyboards.compare, one_time_keyboard=False))
        return "compare"
    if idx < 0 or idx >= len(country_list):
        await update.message.reply_text("Передан несуществующий индекс.",
                                        reply_markup=ReplyKeyboardMarkup(keyboards.compare, one_time_keyboard=False))
        return "compare"
    if len(context.args) > 1:
        await update.message.reply_text("Слишком много аргументов.")
        return "compare"

    db_sess = db_session.create_session()
    comitem = db_sess.query(CompareList).filter(CompareList.id == update.effective_user.id).first()
    country_list.remove(country_list[idx])
    final_str = ",".join(country_list) + ','
    print(final_str)
    comitem.countries = final_str
    db_sess.commit()
    context.user_data["clist"] = country_list
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text="Страна была удалена. Возвращение в compare_list.",
                                   reply_markup=ReplyKeyboardMarkup(keyboards.compare, one_time_keyboard=False))
    return "compare"
