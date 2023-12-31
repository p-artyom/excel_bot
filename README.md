# Бот-обработчик .xlsx файлов

## Описание

Проект представляет из себя Telegram-бота, который выполняет одну функцию -
обрабатывает .xlsx файл. Пользователь прикрепляет .xlsx файл в формате таблицы
с полями: title - название, url - ссылка на сайт источник, xpath - путь к
элементу с ценой. Бот получает файл, сохраняет в локальную базу данных и
открывает при помощи библиотеки pandas. Далее бот отправляет содержимое в
ответ пользователю.

## Технологии

- Python 3.9;
- SQLite3;
- python-telegram-bot 13.7;
- pandas 2.0.3.

## Запуск проекта

- Установите и активируйте виртуальное окружение

- Установите зависимости из файла requirements.txt

```text
pip install -r requirements.txt
```

- В корне проекта создайте .env файл и заполните следующими данными:

  - в переменную `TELEGRAM_TOKEN` сохраните токен вашего бота. Получить этот
  токен можно у телеграм-бота _@BotFather_;

  - в переменную `DATEBASE_PATH` укажите название папки, в которой будет
  храниться файлы базы данных;

  - в переменную `DATEBASE_NAME` укажите название файла базы данных;

  - в переменную `TEMP_PATH` укажите название папки, в которой будет
  храниться полученный .xlsx файл и лог-файлы.

- В корне проекта выполните команду:

```text
python excel_bot.py
```

- Или если установлен GNU Make (На MacOS и Linux он уже установлен), то из
папки проекта выполните команду:

```text
make run
```

## Автор

Пилипенко Артем
