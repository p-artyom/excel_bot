import logging
import os
import sqlite3
import sys
from logging.handlers import RotatingFileHandler
from sqlite3 import Error
from typing import List, Union

import pandas
from dotenv import load_dotenv
from telegram.ext import (
    CallbackContext,
    CommandHandler,
    Filters,
    MessageHandler,
    Updater,
)

load_dotenv()


TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
DATEBASE_PATH = os.getenv('DATEBASE_PATH')
DATEBASE_NAME = os.getenv('DATEBASE_NAME')
TEMP_PATH = os.getenv('TEMP_PATH')


def run_query(query: str, data: List[Union[int, str]] = []) -> None:
    """Подключение и выполнение запросов к базе данных."""

    try:
        logging.debug(
            'Запущен процесс подключения и выполнения '
            'запроса к базе данных.',
        )
        with sqlite3.connect(
            os.path.join(DATEBASE_PATH, DATEBASE_NAME),
        ) as connect:
            cursor = connect.cursor()
            cursor.execute(query, data)
            connect.commit()
        logging.debug(
            'Удачное подключение и выполнение запроса к базе данных.',
        )
    except Error as error:
        logging.error(
            'Ошибка при подключении и выполнении запроса к базе данных: '
            f'{error}.',
        )


def create_table() -> None:
    """Создание базы данных."""

    run_query(
        '''
        CREATE TABLE IF NOT EXISTS site_data_parsing (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            url TEXT,
            xpath TEXT
        );
        ''',
    )


def uploading_data_to_database(
    update: Updater,
    context: CallbackContext,
    excel_data: pandas.DataFrame,
) -> None:
    """Сохранение содержимого в базу данных."""

    try:
        for row in excel_data.itertuples(index=False):
            run_query(
                '''
                INSERT INTO site_data_parsing (
                    title,
                    url,
                    xpath
                ) VALUES (?, ?, ?)
                ''',
                [
                    row.title,
                    row.url,
                    row.xpath,
                ],
            )
    except Exception as error:
        send_message(
            update,
            context,
            'Ошибка при сохранении содержимого. Проверьте корректность файла!',
        )
        logging.error(
            f'Сбой при сохранении содержимого в базу данных: {error}.',
        )


def check_tokens() -> bool:
    """Проверяет доступность переменных.

    Returns:
        Значение True, если все необходимые переменные окружения доступны,
        в противном случае False.
    """

    return all((TELEGRAM_TOKEN, DATEBASE_PATH, DATEBASE_NAME, TEMP_PATH))


def send_message(
    update: Updater,
    context: CallbackContext,
    message: str,
) -> None:
    """Отправляет сообщение в Telegram чат."""

    try:
        logging.debug(
            f'Запущен процесс отправки сообщения "{message}" в Telegram.',
        )
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=message,
        )
        logging.debug(f'Удачная отправка сообщения "{message}" в Telegram.')
    except Exception as error:
        logging.error(f'Сбой при отправке сообщения в Telegram: {error}.')


def wake_up(update: Updater, context: CallbackContext) -> None:
    """Обработка команды /start."""

    logging.debug('Запущен процесс обработки команды /start.')
    send_message(
        update,
        context,
        'Привет, я бот, который сохраняет данные сайта для парсинга из .xlsx '
        'файла в базу данных.',
    )


def text_message(update: Updater, context: CallbackContext) -> None:
    """Обработка текстового сообщения."""

    logging.debug('Запущен процесс обработки текстового сообщения.')
    send_message(update, context, 'Я могу обрабатывать только .xlsx файлы.')


def unknown_command(update: Updater, context: CallbackContext) -> None:
    """Обработка неизвестной команды."""

    logging.debug('Запущен процесс обработки неизвестной команды.')
    send_message(
        update,
        context,
        'Извините, я не понял эту команду. Я могу обрабатывать только '
        '.xlsx файлы.',
    )


def document_message(update: Updater, context: CallbackContext) -> None:
    """Обработка .xlsx файла."""

    try:
        logging.debug('Запущен процесс обработки .xlsx файла.')
        excel_data = pandas.read_excel(
            context.bot.get_file(update.message.document.file_id).download(
                custom_path=f'{TEMP_PATH}/file.xlsx',
            ),
        )
        send_message(update, context, 'Ваш файл содержит следующие данные:')
        send_message(
            update,
            context,
            excel_data.to_string(header=False, index=False),
        )
        uploading_data_to_database(update, context, excel_data)
    except Exception as error:
        logging.error(f'Сбой при обработки .xlsx файла: {error}.')


if __name__ == '__main__':
    if not os.path.exists(TEMP_PATH):
        os.makedirs(TEMP_PATH)
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s, %(levelname)s, %(message)s',
        handlers=[
            RotatingFileHandler(
                f'{TEMP_PATH}/main.log',
                maxBytes=100000,
                backupCount=5,
                encoding='utf-8',
            ),
        ],
    )
    if not os.path.exists(DATEBASE_PATH):
        os.makedirs(DATEBASE_PATH)
        logging.debug(f'Создана директория {DATEBASE_PATH} для базы данных.')
    if not os.path.exists(os.path.join(DATEBASE_PATH, DATEBASE_NAME)):
        create_table()
        logging.debug('База данных создана.')
    if not check_tokens():
        logging.critical('Отсутствуют обязательные переменные окружения.')
        sys.exit()
    logging.debug('Все обязательные переменные окружения присутствуют.')
    updater = Updater(token=TELEGRAM_TOKEN)
    updater.dispatcher.add_handler(CommandHandler('start', wake_up))
    updater.dispatcher.add_handler(
        MessageHandler(Filters.command, unknown_command),
    )
    updater.dispatcher.add_handler(MessageHandler(Filters.text, text_message))
    updater.dispatcher.add_handler(
        MessageHandler(
            Filters.document.file_extension('xlsx'),
            document_message,
        ),
    )
    updater.start_polling()
    updater.idle()
