import json
import os
from zipfile import ZipFile

import requests
from texts import *
from lxml import html
from config import bot
from copy import deepcopy
from pyrogram import filters
from anonfile import AnonFile
from models import Session, Users
from datetime import datetime as dt
from pyrogram.types import Video, Photo, ReplyKeyboardRemove
from asyncio.exceptions import TimeoutError as AsyncioTimeoutError
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, ForceReply

Session = Session()
anon = AnonFile()

menu_keyboard = ReplyKeyboardMarkup([
    [
        KeyboardButton('آپلود پکیج عمومی'),
        KeyboardButton('آپلود پکیج خصوصی'),
        KeyboardButton('آپلود عکس/ویدئو'),
    ],
])


def login_required(func):
    async def wrapper(*args, **kwargs):
        message = args[1]
        user_chat_id = message.chat.id
        user = Session.query(Users).filter(Users.chat_id == str(user_chat_id)).first()
        if user and user.logged_in:
            await func(*args, **kwargs)
        else:
            await message.reply(LOGIN_REQUIRED)

    return wrapper


def file_parser(message, maximum_size=None):
    """
    :param message: message who has file object.
    :param maximum_size: defualt is 500MB.
    :return: Dict
    :raise: ValueError raised if file size high than maximum_size.
    """
    if maximum_size is True:
        maximum_size = 5 * (10 ** 8)

    file = None
    is_media = False

    files = [
        message.photo,
        message.video,
        message.document,
    ]
    for file in files:
        if file:
            if maximum_size:
                if file.file_size > maximum_size:
                    raise ValueError
                else:
                    is_media = True if type(file) == Photo or type(file) == Video else False
            break

    return {'file': file, 'is_media': is_media}


def extract_direct_link(file_link):
    req = requests.get(file_link)
    response = req.content
    tree = html.fromstring(response)
    link = tree.xpath('//a[@id="download-url"]/@href')[0]
    return link


@bot.on_message(filters.command('start', prefixes=['/', ]))
async def start_handler(_, message):
    user_chat_id = message.chat.id
    user = Session.query(Users).filter(Users.chat_id == str(user_chat_id)).first()
    if not user:
        user = Users(chat_id=str(user_chat_id), join_date=dt.now())
        Session.add(user)
        Session.commit()
    elif user and user.logged_in:
        await bot.send_message(user_chat_id, LOGGED_IN_STARTS)
        return

    keyboard = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton('ورود', callback_data='authentication')],
            [InlineKeyboardButton('ثبت نام در سایت', url='https://boomilia.com/accounts/signup/')],
        ]
    )
    await bot.send_message(user_chat_id, START_TEXT, reply_markup=keyboard, parse_mode='HTML')


@bot.on_callback_query(filters.regex('authentication'))
async def authenticate_user(_, callback):
    user_chat_id = callback.from_user.id
    user = Session.query(Users).filter(Users.chat_id == str(user_chat_id)).first()
    if user and user.logged_in:
        await bot.send_message(user_chat_id, LOGGED_IN_PAST)
    else:
        try:
            asked_username = await bot.ask(user_chat_id, text=ASK_USERNAME, timeout=20,
                                           parse_mode='Markdown', reply_markup=ForceReply())
            asked_password = await bot.ask(user_chat_id, text=ASK_PASSWROD, timeout=20,
                                           parse_mode='Markdown', reply_markup=ForceReply())
            await asked_password.delete()

            req = requests.post(
                url='https://boomilia.com/api/api-token-auth/',
                data={
                    'username': asked_username.text,
                    'password': asked_password.text,
                },
            )
            response = json.loads(req.content)
            try:
                token = response['token']
                user.token = token
                user.logged_in = True
                Session.commit()

                await bot.send_message(
                    chat_id=user_chat_id,
                    text=f'شما وارد حساب کاربری خود با نام کاربری {asked_username.text} شدید!',
                )
            except KeyError:
                await bot.send_message(user_chat_id, AUTH_FAIL)

        except AsyncioTimeoutError:
            await bot.send_message(user_chat_id, TIMEOUT)


@bot.on_message(filters.media & filters.private & ~filters.sticker & ~filters.animation)
@login_required
async def get_files(_, message):
    user_chat_id = message.chat.id

    _message = deepcopy(message)

    yes_no_question = ReplyKeyboardMarkup([
        [
            KeyboardButton('بله'),
            KeyboardButton('خیر'),
        ]
    ])

    try:
        are_sure = await bot.ask(chat_id=user_chat_id, text=UPLOAD_SURE, reply_markup=yes_no_question, timeout=60)
    except AsyncioTimeoutError:
        await message.reply('مهلت شما برای ارسال پاسخ به اتمام رسید, دوباره تلاش کنید.',
                            reply_markup=ReplyKeyboardRemove(selective=True))
        return

    if are_sure.text == 'بله':
        file = None
        try:
            file = file_parser(_message, maximum_size=True)
        except ValueError:
            await message.reply(FILE_SIZE_LIMIT, reply_markup=ReplyKeyboardRemove(selective=True))

        if file:
            should_zip = True
            if file['is_media']:
                try:
                    type_of_file = await bot.ask(chat_id=user_chat_id, text=UPLOAD_DESC,
                                                 reply_markup=yes_no_question, timeout=60)
                except AsyncioTimeoutError:
                    await message.reply('مهلت شما برای ارسال پاسخ به اتمام رسید, دوباره تلاش کنید.',
                                        reply_markup=ReplyKeyboardRemove(selective=True))
                    return

                if type_of_file.text == 'خیر':
                    should_zip = False

            delete_keyboard = await bot.send_message(user_chat_id, '_',
                                                     reply_markup=ReplyKeyboardRemove(selective=True))
            await delete_keyboard.delete()
            progress_message = await message.reply('فایل در حال دانلود توسط ربات می‌باشد, صبور باشید ...')

            async def progress(current_size, file_size):
                await progress_message.edit_text(f"در حال دانلود ... {current_size * 100 / file_size:.1f}%")

            downloaded_file = await bot.download_media(message=message, progress=progress)
            if downloaded_file:
                file = downloaded_file
                zip_file_name = None
                if should_zip:
                    zip_file_name = file.split('.')[0] + '.zip'
                    with ZipFile(zip_file_name, 'w') as zip_file:
                        zip_file.write(file, os.path.basename(file))
                        file = zip_file_name

                upload = anon.upload(file)
                uploaded_file_url = upload.url.geturl()
                uploaded_file_direct_url = extract_direct_link(uploaded_file_url)
                await progress_message.edit_text('لینک مستقیم فایل: %s' % uploaded_file_direct_url)
                os.remove(downloaded_file)

                if should_zip:
                    os.remove(zip_file_name)
    else:
        await bot.send_message(user_chat_id, 'عملیات لغو شد.', reply_markup=ReplyKeyboardRemove(selective=True))
        # type_of_file = bot.ask('در صورتی که میخواهید فایل را به عنوان پکیج آپلود کنید می‌بایست فایل')


@bot.on_message(filters.private)
async def wrong_messages(_, message):
    await message.reply(WRONG_COMMAND)


if __name__ == '__main__':
    bot.run()
