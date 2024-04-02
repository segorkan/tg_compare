import logging
from telegram.ext import Application, MessageHandler, filters, CommandHandler, ContextTypes, ConversationHandler
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Bot, KeyboardButton, Update, InputMediaPhoto
from config import BOT_TOKEN
from find import pre_find, find
import time

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)

logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_photo(chat_id=update.effective_chat.id, photo=open("./images/all_countries.png", "rb"),
                                 caption="Приветствуем вас! Этого бота можно использовать для быстрого получения краткой информации о странах, "
                                         "просмотра интересующих деталей страны и сравнения характеристик стран между собой. "
                                         "/help для получения информации об использовании.")
    return "menu"


async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("""/stop для остановки пользования ботом.
                                    /help для информации о командах.
                                    /find - перейти к поиску стран. Далее страну можно добавить в список к просмотру информации или список к сравнению.
                                    /info_list - просмотр информации и интересующих деталей о странах в списке.
                                    /compare_list - перейти к сравнению стран из списка.""")
    return "menu"


async def back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Возвращаемся в меню.")
    return "menu"


async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Закончил работу. /start для возобновления работы.")
    return ConversationHandler.END


def main():
    application = Application.builder().token(BOT_TOKEN).build()
    global_conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            "menu": [CommandHandler('help', help), CommandHandler('find', pre_find)],
            "find": [MessageHandler(filters.TEXT & ~filters.COMMAND, find)]
        },
        fallbacks=[CommandHandler('stop', stop)]
    )
    application.add_handler(global_conv_handler)
    application.run_polling()


if __name__ == '__main__':
    main()
