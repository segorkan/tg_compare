import logging
from telegram.ext import Application, MessageHandler, filters, CommandHandler, ContextTypes, ConversationHandler, \
    StringRegexHandler
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Bot, KeyboardButton, Update, InputMediaPhoto
from telegram.constants import ParseMode
from config import BOT_TOKEN
from find import pre_find, find
from db_manip import add_info, add_compare, compare_list, info_list, info_delete, comp_delete
import time
from data import db_session
from data.info_list import InfoList
from data.compare_list import CompareList
from check import check, handleCheck, command_list
from compare import chars, versus
from graphs import histplot, scatter
import keyboards

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)

logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db_sess = db_session.create_session()
    infoitem = db_sess.query(InfoList).filter(InfoList.id == update.effective_user.id).first()
    comitem = db_sess.query(CompareList).filter(CompareList.id == update.effective_user.id).first()
    if not infoitem:
        infoitem = InfoList()
        infoitem.id = update.effective_user.id
        infoitem.countries = ""
        db_sess.add(infoitem)
        db_sess.commit()
    if not comitem:
        infoitem = CompareList()
        infoitem.id = update.effective_user.id
        infoitem.countries = ""
        db_sess.add(infoitem)
        db_sess.commit()
    markup = ReplyKeyboardMarkup(keyboards.menu, one_time_keyboard=False)
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text="<b>Приветствуем вас! Этого бота можно использовать для быстрого получения краткой информации о странах, "
                                        "просмотра интересующих деталей страны и сравнения характеристик стран между собой. "
                                        "/help для получения информации об использовании.</b>",
                                   parse_mode=ParseMode.HTML, reply_markup=markup)
    return "menu"


async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("""/stop для остановки пользования ботом.
                                    /help для информации о командах.
                                    /find - перейти к поиску стран. Далее страну можно добавить в список к просмотру информации или список к сравнению.
                                    /info_list - просмотр информации и интересующих деталей о странах в списке.
                                    /compare_list - перейти к сравнению стран из списка.""",
                                    reply_markup=ReplyKeyboardMarkup(keyboards.menu, one_time_keyboard=False))
    return "menu"


async def back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Возвращаемся в меню.",
                                    reply_markup=ReplyKeyboardMarkup(keyboards.menu, one_time_keyboard=False))
    return "menu"


async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Закончил работу. /start для возобновления работы.",
                                    reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


async def secret(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_sticker(chat_id=update.effective_chat.id, sticker=open("./images/sticker.webp", "rb"))


def main():
    application = Application.builder().token(BOT_TOKEN).build()
    db_session.global_init("db/blogs.db")
    global_conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            "menu": [CommandHandler('help', help), CommandHandler('find', pre_find),
                     CommandHandler('info_list', info_list), CommandHandler('compare_list', compare_list)],
            "find": [MessageHandler(filters.TEXT & ~filters.COMMAND, find), CommandHandler('back', back)],
            "rfind": [CommandHandler('find', pre_find), CommandHandler('add_info', add_info),
                      CommandHandler('add_compare', add_compare), CommandHandler('back', back)],
            "endfind": [CommandHandler('find', pre_find), CommandHandler('back', back)],
            "info": [CommandHandler('back', back), CommandHandler('delete', info_delete),
                     CommandHandler('info_list', info_list), CommandHandler('check', check)],
            "check": [CommandHandler('back', back), MessageHandler(filters.TEXT & ~filters.COMMAND, handleCheck),
                      CommandHandler('chlist', command_list)],
            "compare": [CommandHandler('back', back), CommandHandler('delete', comp_delete),
                        CommandHandler('compare_list', compare_list), CommandHandler('chars', chars),
                        CommandHandler('versus', versus), CommandHandler('histplot', histplot),
                        CommandHandler('scatter', scatter)]
        },
        fallbacks=[CommandHandler('stop', stop)]
    )
    test = CommandHandler('secret', secret)
    application.add_handler(global_conv_handler)
    application.add_handler(test)
    application.run_polling()


if __name__ == '__main__':
    main()
