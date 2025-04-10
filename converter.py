import asyncio
import logging

import aiohttp
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, CommandObject, ChatMemberUpdatedFilter, JOIN_TRANSITION
from aiogram.exceptions import *
from aiogram.enums.inline_query_result_type import InlineQueryResultType
from aiogram.types import Message, BufferedInputFile, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InlineQuery, \
    InlineQueryResultPhoto, InlineQueryResultArticle, InputTextMessageContent, ChatMemberUpdated
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from convertertoken import BOT_TOKEN, ADMIN_ID


# Заготовки для машин состояний (используются при нажатии на верхние кнопки меню)
class RGBForm(StatesGroup):
    count = State()


class HEXForm(StatesGroup):
    count = State()


class CMYKForm(StatesGroup):
    count = State()


class YearForm(StatesGroup):
    count = State()


# Инициализация бота
storage = MemoryStorage()
logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=storage)
# Заготовки для ссылок
api_url = 'https://www.thecolorapi.com/id?'
ans_url = 'https://whatcolor.ru/color/'
ans_pic = 'https://dummyimage.com/500x500/'
# Значения цвета года от Pantone, меняются вручную каждый год
year_pantone = {
    2000: [['15-4020', '155 183 212', '9BB7D4', '27 14 0 17']],
    2001: [['17-2031', '199 67 117', 'C74375', '0 66 41 22']],
    2002: [['19-1664', '191 25 50', 'BF1932', '0 87 74 25']],
    2003: [['14-4811', '123 196 196', '7BC4C4', '37 0 0 23']],
    2004: [['17-1456', '226 88 62', 'E2583E', '0 61 73 11']],
    2005: [['15-5217', '83 176 174', '53B0AE', '53 0 1 31']],
    2006: [['13-1106', '222 205 190', 'DECDBE', '0 8 14 13']],
    2007: [['19-1557', '155 27 48', '9B1B30', '0 83 69 39']],
    2008: [['18-3943', '90 91 159', '5A5B9F', '43 43 0 38']],
    2009: [['14-0848', '235 191 87', 'EBBF57', '0 19 63 8']],
    2010: [['15-5519', '69 181 170', '45B5AA', '62 0 6 29']],
    2011: [['18-2120', '217 79 112', 'D94F70', '0 64 48 15']],
    2012: [['17-1463', '221 65 36', 'DD4124', '0 71 84 13']],
    2013: [['17-5641', '0 148 115', '009473', '100 0 22 42']],
    2014: [['18-3224', '173 94 153', 'AD5E99', '0 46 12 32']],
    2015: [['18-1438', '150 79 76', '964F4C', '0 47 49 41']],
    2016: [['13-1520', '247 202 202', 'F7CACA', '0 18 18 3'], ['15-3919', '147 169 209', '93A9D1', '30 19 0 18']],
    2017: [['15-0343', '136 176 75', '88B04B', '23 0 57 31']],
    2018: [['18-3838', '95 75 139', '5F4B8B', '32 46 0 45']],
    2019: [['16-1546', '255 111 97', 'FF6F61', '0 56 62 1']],
    2020: [['19-4052', '15 76 129', '0F4C81', '88 41 0 49']],
    2021: [['17-5104', '147 149 151', '939597', '3 1 0 41'], ['13-0647', '245 223 77', 'F5DF4D', '0 9 69 4']],
    2022: [['17-3938', '102 103 171', '6667AB', '40 40 0 33']],
    2023: [['18-1750', '187 38 73', 'BB2649', '0 80 61 27']],
    2024: [['13-1023', '255 190 152', 'FFBE98', '0 25 40 1']],
    2025: [['17-1230', '164 120 100', 'A47864', '0 27 39 36']]
}

# Меню бота
main_keyboard = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='🎨 Из RGB'), KeyboardButton(text='🎨 Из CMYK'),
     KeyboardButton(text='🎨 Из HEX')],
    [KeyboardButton(text='🔙 Главное меню'), KeyboardButton(text='🌈Цвет года'),
     KeyboardButton(text='🔽 Свернуть клавиатуру')]
], resize_keyboard=True)


# Функция для запросов
async def request(mode: str, value: str | list | tuple | set):
    add = ''
    try:
        if mode.lower() == 'hex':
            if len(value) == 3:
                if 0 <= int(value[0], 16) <= 15 and 0 <= int(value[1], 16) <= 15 and 0 <= int(value[2], 16) <= 15:
                    add = f'hex={value}'
            elif len(value) == 6:
                if 0 <= int(value[:2], 16) <= 255 and 0 <= int(value[2:4], 16) <= 255 and 0 <= int(value[5:], 16) <= 255:
                    add = f'hex={value}'
    except ValueError:
        add = ''

    if mode.lower() == 'rgb':
        if len(value) == 3:
            if str(value[0]).isnumeric() and str(value[1]).isnumeric() and str(value[2]).isnumeric():
                if 0 <= int(value[0]) <= 255 and 0 <= int(value[1]) <= 255 and 0 <= int(value[2]) <= 255:
                    add = f'rgb=rgb({value[0]},{value[1]},{value[2]})'

    elif mode.lower() == 'cmyk':
        if len(value) == 4:
            if str(value[0]).isnumeric() and str(value[1]).isnumeric() and str(value[2]).isnumeric() and str(
                    value[3]).isnumeric():
                if 0 <= int(value[0]) <= 100 and 0 <= int(value[1]) <= 100 and 0 <= int(value[2]) <= 100 and 0 <= int(
                        value[3]) <= 100:
                    add = f'cmyk=cmyk({value[0]},{value[1]},{value[2]},{value[3]})'

    if add != '':
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f'{api_url}{add}') as response_:
                    response = await response_.json()
                async with session.get(
                        f'{ans_pic}{str(response['hex']['clean']).upper()}/{str(response['hex']['clean']).upper()}.png') as response_2:
                    photo = await response_2.content.read()
                response_hex = str(response['hex']['clean']).upper()
                response_r = 0 if response['rgb']['r'] is None else response['rgb']['r']
                response_g = 0 if response['rgb']['g'] is None else response['rgb']['g']
                response_b = 0 if response['rgb']['b'] is None else response['rgb']['b']
                response_c = 0 if response['cmyk']['c'] is None else response['cmyk']['c']
                response_m = 0 if response['cmyk']['m'] is None else response['cmyk']['m']
                response_y = 0 if response['cmyk']['y'] is None else response['cmyk']['y']
                response_k = 0 if response['cmyk']['k'] is None else response['cmyk']['k']

            return [response_hex, response_r, response_g, response_b, response_c, response_m, response_y, response_k], photo

        except Exception as e:
            await bot.send_message(ADMIN_ID, str(e))
            return 0, 0
    else:
        return 0, 0


# Приветственное сообщение
@dp.message(F.text == '🔙 Главное меню')
async def process_start_button(message: Message):
    bot_info = await bot.get_me()
    await message.reply('Добро пожаловать в бота для конвертации цветов! 👋\n\n'
                        'Нажмите на кнопку снизу, а затем введите значения⌨️\n'
                        f'Или напишите / или @{bot_info.username}, цветовую модель, а затем значения✍️\n\n'
                        'Например: 🔍\n'
                        '/hex FFFFFF\n'
                        '/rgb 255 255 255\n'
                        f'@{bot_info.username} cmyk 0 0 0 0',
                        reply_markup=main_keyboard
                        )


@dp.message(Command(commands=['start']))
async def process_start_command(message: Message, command: CommandObject):
    bot_info = await bot.get_me()
    check = True
    if command.args:
        args = command.args.split('_')
    else:
        args = False
    if not args:
        await message.reply('Добро пожаловать в бота для конвертации цветов! 👋\n\n'
                            'Нажмите на кнопку снизу, а затем введите значения⌨️\n'
                            f'Или напишите / или @{bot_info.username}, цветовую модель, а затем значения✍️\n\n'
                            'Например: 🔍\n'
                            '/hex FFFFFF\n'
                            '/rgb 255 255 255\n'
                            f'@{bot_info.username} cmyk 0 0 0 0',
                            reply_markup=main_keyboard
                            )
    else:
        if args[0].lower() == 'year':
            year = args[1]
            now = list(year_pantone.keys())[-1]
            if year.isnumeric():
                if 2000 <= int(year) <= now:
                    for i in year_pantone[int(year)]:
                        _, photo = await request('hex', i[2])
                        await message.reply_photo(photo=BufferedInputFile(photo, 'output.png'),
                                                  caption=f'✨ Pantone: {i[0]}\n'
                                                          f'✨ HEX: #{i[2]}\n'
                                                          f'✨ RGB: {i[1]}\n'
                                                          f'✨ CMYK: {i[3]}\n\n'
                                                          f'🔗 {ans_url}{i[2]}\n'
                                                          f'📤 t.me/share/url?url=t.me/{bot_info.username}/?start=year_{year}',
                                                  reply_markup=main_keyboard)
            check = False
        else:
            if args[0].lower() == 'hex':
                response, photo = await request(args[0], args[1])
            else:
                response, photo = await request(args[0], args[1:])
            if response != 0:
                try:
                    if check:
                        response_hex = response[0]
                        response_r = response[1]
                        response_g = response[2]
                        response_b = response[3]
                        response_c = response[4]
                        response_m = response[5]
                        response_y = response[6]
                        response_k = response[7]

                        await message.reply_photo(photo=BufferedInputFile(photo, 'output.png'),
                                                  caption=
                                                  f'✨ HEX: #{response_hex}\n'
                                                  f'✨ RGB: {response_r} {response_g} {response_b}\n'
                                                  f'✨ CMYK: {response_c} {response_m} {response_y} {response_k}\n\n'
                                                  f'🔗 {ans_url}{response_hex}\n'
                                                  f'📤 t.me/share/url?url=t.me/{bot_info.username}/?start=hex_{response_hex}',
                                                  reply_markup=main_keyboard)
                    else:
                        await message.reply('Добро пожаловать в бота для конвертации цветов! 👋\n\n'
                                            'Нажмите на кнопку снизу, а затем введите значения⌨️\n'
                                            f'Или напишите / или @{bot_info.username}, цветовую модель, а затем значения✍️\n\n'
                                            'Например: 🔍\n'
                                            '/hex FFFFFF\n'
                                            '/rgb 255 255 255\n'
                                            f'@{bot_info.username} cmyk 0 0 0 0',
                                            reply_markup=main_keyboard
                                            )
                except Exception as e:
                    await bot.send_message(ADMIN_ID,
                                           f'{'@' + message.from_user.username if message.from_user.username else 'tg://openmessage?user_id=' + str(message.from_user.id)}\n{e}')
                    await message.reply('Непредвиденная ошибка❌', reply_markup=main_keyboard)


# Полный список команд
@dp.message(Command(commands=['help']))
async def process_help_command(message: Message):
    bot_info = await bot.get_me()
    now = list(year_pantone.keys())[-1]
    await message.reply(f'📋Полный список команд:\n'
                        f'/start, /help;\n\n'
                        f'/hex HEX или @{bot_info.username} hex HEX,\n'
                        f'где HEX - 3 или 6 символов от 0 до 9 и от A до F;\n\n'
                        f'/rgb R G B или @{bot_info.username} rgb R G B,\n'
                        f'где R, G, B - числа от 0 до до 255;\n\n'
                        f'/cmyk C M Y K или @{bot_info.username} cmyk C M Y K,\n'
                        f'где C, M, Y, K - числа от 0 до 100;\n\n'
                        f'/year YYYY или @{bot_info.username} year YYY,\n'
                        f'где YYYY - год от 2000 до {now};',
                        reply_markup=main_keyboard
                        )


# Команда "/hex hex", где hex - 3 или 6 символов от 0 до 9 и от A до F
@dp.message(Command(commands=['hex']))
async def process_hex_command(message: Message):
    bot_info = await bot.get_me()
    hex = None
    try:
        # Чтение сообщения
        _, hex = message.text.split()
    except ValueError:
        await message.reply(
            'Вы ввели неверное количество значений❌\nHEX-значение состоит из 3 или 6 символов от 0 до 9 и от A до F.',
            reply_markup=main_keyboard)
    # Если сообщение считано успешно
    if hex:
        response, photo = await request('hex', hex)
        if response != 0:
            # Запись в переменные
            response_hex = response[0]
            response_r = response[1]
            response_g = response[2]
            response_b = response[3]
            response_c = response[4]
            response_m = response[5]
            response_y = response[6]
            response_k = response[7]
            try:
                # Отправка сообщения с фото
                await message.reply_photo(photo=BufferedInputFile(photo, 'output.png'),
                                          caption=
                                          f'✨ HEX: #{response_hex}\n'
                                          f'✨ RGB: {response_r} {response_g} {response_b}\n'
                                          f'✨ CMYK: {response_c} {response_m} {response_y} {response_k}\n\n'
                                          f'🔗 {ans_url}{response_hex}\n'
                                          f'📤 t.me/share/url?url=t.me/{bot_info.username}/?start=hex_{response_hex}',
                                          reply_markup=main_keyboard)
            except TelegramBadRequest as e:
                await bot.send_message(ADMIN_ID,
                                       f'{'@' + message.from_user.username if message.from_user.username else 'tg://openmessage?user_id=' + str(message.from_user.id)}\n{e}')
                await message.reply(
                    'Telegram не смог отправить изображение❌\nПопробуйте выполнить другой запрос, а затем повторить этот или выполните запрос позже.',
                    reply_markup=main_keyboard)
                # Отправка сообщения без фото, если изображение не было удачно сохранено(зависит от API фото)
                await message.reply(
                    f'✨ HEX: #{response_hex}\n'
                    f'✨ RGB: {response_r} {response_g} {response_b}\n'
                    f'✨ CMYK: {response_c} {response_m} {response_y} {response_k}\n\n'
                    f'🔗 {ans_url}{response_hex}\n'
                    f'📤 t.me/share/url?url=t.me/{bot_info.username}/?start=hex_{response_hex}',
                    reply_markup=main_keyboard)

            except Exception as e:
                # Владелец узнаёт у кого произошла ошибка и какая
                await bot.send_message(ADMIN_ID,
                                       f'{'@' + message.from_user.username if message.from_user.username else 'tg://openmessage?user_id=' + str(message.from_user.id)}\n{e}')
                await message.reply('Непредвиденная ошибка❌', reply_markup=main_keyboard)
        else:
            await message.reply(
                'Вы ввели недопустимое значение❌\nHEX-значение состоит из 3 или 6 символов от 0 до 9 и от A до F.',
                reply_markup=main_keyboard)
    else:
        await message.reply(
            'Вы ввели недопустимое значение❌\nHEX-значение состоит из 3 или 6 символов от 0 до 9 и от A до F.',
            reply_markup=main_keyboard)


# Команда "/rgb r g b", где r,g,b - числа от 0 до 255
@dp.message(Command(commands=['rgb']))
# Структура каждой функции одинакова, см. комментарии сверху
async def process_rgb_command(message: Message):
    bot_info = await bot.get_me()
    r, g, b = None, None, None
    try:
        _, r, g, b = message.text.split()
    except ValueError:
        await message.reply('Вы ввели неверное количество значений❌\nRGB-значение состоит из 3 чисел от 0 до 255.',
                            reply_markup=main_keyboard)
    # "!= None" т.к. значение может быть равно 0, (if 0) = False, (if 0 != None) = True
    if r != None and g != None and b != None:
        response, photo = await request('rgb', (r, g, b))
        if response != 0:
            response_hex = response[0]
            response_r = response[1]
            response_g = response[2]
            response_b = response[3]
            response_c = response[4]
            response_m = response[5]
            response_y = response[6]
            response_k = response[7]
            try:
                await message.reply_photo(photo=BufferedInputFile(photo, 'output.png'),
                                          caption=
                                          f'✨ HEX: #{response_hex}\n'
                                          f'✨ RGB: {response_r} {response_g} {response_b}\n'
                                          f'✨ CMYK: {response_c} {response_m} {response_y} {response_k}\n\n'
                                          f'🔗 {ans_url}{response_hex}\n'
                                          f'📤 t.me/share/url?url=t.me/{bot_info.username}/?start=hex_{response_hex}',
                                          reply_markup=main_keyboard)
            except TelegramBadRequest as e:
                await bot.send_message(ADMIN_ID,
                                       f'{'@' + message.from_user.username if message.from_user.username else 'tg://openmessage?user_id=' + str(message.from_user.id)}\n{e}')

                await message.reply(
                    'Telegram не смог отправить изображение❌\nПопробуйте выполнить другой запрос, а затем повторить этот или выполните запрос позже.',
                    reply_markup=main_keyboard)
                await message.reply(
                    f'✨ HEX: #{response_hex}\n'
                    f'✨ RGB: {response_r} {response_g} {response_b}\n'
                    f'✨ CMYK: {response_c} {response_m} {response_y} {response_k}\n\n'
                    f'🔗 {ans_url}{response_hex}\n'
                    f'📤 t.me/share/url?url=t.me/{bot_info.username}/?start=hex_{response_hex}',
                    reply_markup=main_keyboard)

            except Exception as e:
                await bot.send_message(ADMIN_ID,
                                       f'{'@' + message.from_user.username if message.from_user.username else 'tg://openmessage?user_id=' + str(message.from_user.id)}\n{e}')
                await message.reply('Непредвиденная ошибка❌', reply_markup=main_keyboard)

        else:
            await message.reply('Вы ввели недопустимое значение❌\nRGB-значение состоит из 3 чисел от 0 до 255.',
                                reply_markup=main_keyboard)
    else:
        await message.reply('Вы ввели недопустимое значение❌\nRGB-значение состоит из 3 чисел от 0 до 255.',
                            reply_markup=main_keyboard)


# Команда "/cmyk c m y k", где c,m,y,k - числа от 0 до 100
@dp.message(Command(commands=['cmyk']))
async def process_cmyk_command(message: Message):
    bot_info = await bot.get_me()
    c, m, y, k = None, None, None, None
    try:
        _, c, m, y, k = message.text.split()
    except ValueError:
        await message.reply('Вы ввели неверное количество значений❌\nCMYK-значение состоит из 4 чисел от 0 до 100.',
                            reply_markup=main_keyboard)
    if c != None and m != None and y != None and k != None:
        response, photo = await request('cmyk', (c, m, y, k))
        if response != 0:
            response_hex = response[0]
            response_r = response[1]
            response_g = response[2]
            response_b = response[3]
            response_c = response[4]
            response_m = response[5]
            response_y = response[6]
            response_k = response[7]
            try:
                await message.reply_photo(photo=BufferedInputFile(photo, 'output.png'),
                                          caption=
                                          f'✨ HEX: #{response_hex}\n'
                                          f'✨ RGB: {response_r} {response_g} {response_b}\n'
                                          f'✨ CMYK: {response_c} {response_m} {response_y} {response_k}\n\n'
                                          f'🔗 {ans_url}{response_hex}\n'
                                          f'📤 t.me/share/url?url=t.me/{bot_info.username}/?start=hex_{response_hex}',
                                          reply_markup=main_keyboard)
            except TelegramBadRequest as e:
                await bot.send_message(ADMIN_ID,
                                       f'{'@' + message.from_user.username if message.from_user.username else 'tg://openmessage?user_id=' + str(message.from_user.id)}\n{e}')
                await message.reply(
                    'Telegram не смог отправить изображение❌\nПопробуйте выполнить другой запрос, а затем повторить этот или выполните запрос позже.',
                    reply_markup=main_keyboard)
                await message.reply(
                    f'✨ HEX: #{response_hex}\n'
                    f'✨ RGB: {response_r} {response_g} {response_b}\n'
                    f'✨ CMYK: {response_c} {response_m} {response_y} {response_k}\n\n'
                    f'🔗 {ans_url}{response_hex}\n'
                    f'📤 t.me/share/url?url=t.me/{bot_info.username}/?start=hex_{response_hex}',
                    reply_markup=main_keyboard)

            except Exception as e:
                await bot.send_message(ADMIN_ID,
                                       f'{'@' + message.from_user.username if message.from_user.username else 'tg://openmessage?user_id=' + str(message.from_user.id)}\n{e}')
                await message.reply('Непредвиденная ошибка❌', reply_markup=main_keyboard)

        else:
            await message.reply('Вы ввели недопустимое значение❌\nCMYK-значение состоит из 4 чисел от 0 до 100.',
                                reply_markup=main_keyboard)
    else:
        await message.reply('Вы ввели недопустимое значение❌\nCMYK-значение состоит из 4 чисел от 0 до 100.',
                            reply_markup=main_keyboard)


# Цвета года от Pantone
@dp.message(F.text == '🌈Цвет года')
async def button_year(message: Message, state: FSMContext):
    now = list(year_pantone.keys())[-1]
    await message.reply(f"Введите год от 2000 до {now}.", reply_markup=ReplyKeyboardRemove())
    await state.set_state(YearForm.count)


@dp.message(YearForm.count)
async def process_year_command(message: Message, state: FSMContext):
    bot_info = await bot.get_me()
    try:
        form = await state.update_data(count=message.text)
        year = form['count']
        now = list(year_pantone.keys())[-1]
        if year.isnumeric():
            if 2000 <= int(year) <= now:
                for i in year_pantone[int(year)]:
                    _, photo = await request('hex', i[2])
                    await message.reply_photo(photo=BufferedInputFile(photo, 'output.png'),
                                              caption=f'✨ Pantone: {i[0]}\n'
                                                      f'✨ HEX: #{i[2]}\n'
                                                      f'✨ RGB: {i[1]}\n'
                                                      f'✨ CMYK: {i[3]}\n\n'
                                                      f'🔗 {ans_url}{i[2]}\n'
                                                      f'📤 t.me/share/url?url=t.me/{bot_info.username}/?start=year_{year}',
                                              reply_markup=main_keyboard)

    except ValueError:
        await message.reply('Вы ввели неверное количество значений❌',
                            reply_markup=main_keyboard)

    except Exception as e:
        await message.reply('Непредвиденная ошибка❌', reply_markup=main_keyboard)
        await bot.send_message(ADMIN_ID,
                               f'{'@' + message.chat.username if message.chat.username else 'tg://openmessage?user_id=' + str(message.chat.id)}\n{e}')


@dp.message(Command(commands=['year']))
async def process_year_command(message: Message):
    bot_info = await bot.get_me()
    try:
        _, year = message.text.split()
        now = list(year_pantone.keys())[-1]
        if year.isnumeric():
            if 2000 <= int(year) <= now:
                for i in year_pantone[int(year)]:
                    _, photo = await request('hex', i[2])
                    await message.reply_photo(photo=BufferedInputFile(photo, 'output.png'),
                                              caption=f'✨ Pantone: {i[0]}\n'
                                                      f'✨ HEX: #{i[2]}\n'
                                                      f'✨ RGB: {i[1]}\n'
                                                      f'✨ CMYK: {i[3]}\n\n'
                                                      f'🔗 {ans_url}{i[2]}\n'
                                                      f'📤 t.me/share/url?url=t.me/{bot_info.username}/?start=year_{year}',
                                              reply_markup=main_keyboard)

    except ValueError:
        await message.reply('Вы ввели неверное количество значений❌',
                            reply_markup=main_keyboard)

    except Exception as e:
        await message.reply('Непредвиденная ошибка❌', reply_markup=main_keyboard)
        await bot.send_message(ADMIN_ID,
                               f'{'@' + message.chat.username if message.chat.username else 'tg://openmessage?user_id=' + str(message.chat.id)}\n{e}')


@dp.message(F.text == '🎨 Из RGB')
async def button_rgb(message: Message, state: FSMContext):
    await message.reply("Введите значения R, G, B через пробел", reply_markup=ReplyKeyboardRemove())
    await state.set_state(RGBForm.count)


@dp.message(RGBForm.count)
async def process_rgb_command(message: Message, state: FSMContext):
    bot_info = await bot.get_me()
    r, g, b = None, None, None
    try:
        # Теперь значения читаются не из сообщения, а из машины состояний
        form = await state.update_data(count=message.text)
        r, g, b = map(int, form['count'].split())
    except ValueError:
        await message.reply('Вы ввели неверное количество значений❌\nRGB-значение состоит из 3 чисел от 0 до 255.',
                            reply_markup=main_keyboard)
        await state.clear()
    if r != None and g != None and b != None:
        response, photo = await request('rgb', (r, g, b))
        if response != 0:
            response_hex = response[0]
            response_r = response[1]
            response_g = response[2]
            response_b = response[3]
            response_c = response[4]
            response_m = response[5]
            response_y = response[6]
            response_k = response[7]
            try:
                await message.reply_photo(photo=BufferedInputFile(photo, 'output.png'),
                                          caption=
                                          f'✨ HEX: #{response_hex}\n'
                                          f'✨ RGB: {response_r} {response_g} {response_b}\n'
                                          f'✨ CMYK: {response_c} {response_m} {response_y} {response_k}\n\n'
                                          f'🔗 {ans_url}{response_hex}\n'
                                          f'📤 t.me/share/url?url=t.me/{bot_info.username}/?start=hex_{response_hex}',
                                          reply_markup=main_keyboard)
                await state.clear()
            except TelegramBadRequest as e:
                await bot.send_message(ADMIN_ID,
                                       f'{'@' + message.from_user.username if message.from_user.username else 'tg://openmessage?user_id=' + str(message.from_user.id)}\n{e}')
                await message.reply(
                    'Telegram не смог отправить изображение❌\nПопробуйте выполнить другой запрос, а затем повторить этот или выполните запрос позже.',
                    reply_markup=main_keyboard)
                await message.reply(
                    f'✨ HEX: #{response_hex}\n'
                    f'✨ RGB: {response_r} {response_g} {response_b}\n'
                    f'✨ CMYK: {response_c} {response_m} {response_y} {response_k}\n\n'
                    f'🔗 {ans_url}{response_hex}\n'
                    f'📤 t.me/share/url?url=t.me/{bot_info.username}/?start=hex_{response_hex}',
                    reply_markup=main_keyboard)
                await state.clear()

            except Exception as e:
                await bot.send_message(ADMIN_ID,
                                       f'{'@' + message.from_user.username if message.from_user.username else 'tg://openmessage?user_id=' + str(message.from_user.id)}\n{e}')
                await message.reply('Непредвиденная ошибка❌', reply_markup=main_keyboard)
                await state.clear()
        else:
            await message.reply('Вы ввели недопустимое значение❌\nRGB-значение состоит из 3 чисел от 0 до 255.',
                                reply_markup=main_keyboard)
            await state.clear()


@dp.message(F.text == '🎨 Из HEX')
async def button_hex(message: Message, state: FSMContext):
    await message.reply("Введите значение HEX", reply_markup=ReplyKeyboardRemove())
    await state.set_state(HEXForm.count)


@dp.message(HEXForm.count)
async def process_hex_command(message: Message, state: FSMContext):
    bot_info = await bot.get_me()
    hex = None
    try:
        form = await state.update_data(count=message.text)
        hex = form['count']
    except ValueError:
        await message.reply(
            'Вы ввели неверное количество значений❌\nHEX-значение состоит из 3 или 6 символов от 0 до 9 и от A до F.',
            reply_markup=main_keyboard)
        await state.clear()
    if hex != None:
        response, photo = await request('hex', hex)
        if response != 0:
            response_hex = response[0]
            response_r = response[1]
            response_g = response[2]
            response_b = response[3]
            response_c = response[4]
            response_m = response[5]
            response_y = response[6]
            response_k = response[7]
            try:
                await message.reply_photo(photo=BufferedInputFile(photo, 'output.png'),
                                          caption=
                                          f'✨ HEX: #{response_hex}\n'
                                          f'✨ RGB: {response_r} {response_g} {response_b}\n'
                                          f'✨ CMYK: {response_c} {response_m} {response_y} {response_k}\n\n'
                                          f'🔗 {ans_url}{response_hex}\n'
                                          f'📤 t.me/share/url?url=t.me/{bot_info.username}/?start=hex_{response_hex}',
                                          reply_markup=main_keyboard)
                await state.clear()
            except TelegramBadRequest as e:
                await bot.send_message(ADMIN_ID,
                                       f'{'@' + message.from_user.username if message.from_user.username else 'tg://openmessage?user_id=' + str(message.from_user.id)}\n{e}')
                await message.reply(
                    'Telegram не смог отправить изображение❌\nПопробуйте выполнить другой запрос, а затем повторить этот или выполните запрос позже.',
                    reply_markup=main_keyboard)
                await message.reply(
                    f'✨ HEX: #{response_hex}\n'
                    f'✨ RGB: {response_r} {response_g} {response_b}\n'
                    f'✨ CMYK: {response_c} {response_m} {response_y} {response_k}\n\n'
                    f'🔗 {ans_url}{response_hex}\n'
                    f'📤 t.me/share/url?url=t.me/{bot_info.username}/?start=hex_{response_hex}',
                    reply_markup=main_keyboard)
                await state.clear()

            except Exception as e:
                await bot.send_message(ADMIN_ID,
                                       f'{'@' + message.from_user.username if message.from_user.username else 'tg://openmessage?user_id=' + str(message.from_user.id)}\n{e}')
                await message.reply('Непредвиденная ошибка❌', reply_markup=main_keyboard)
                await state.clear()
        else:
            await message.reply(
                'Вы ввели недопустимое значение❌\nHEX-значение состоит из 3 или 6 символов от 0 до 9 и от A до F.',
                reply_markup=main_keyboard)
            await state.clear()


@dp.message(F.text == '🎨 Из CMYK')
async def button_cmyk(message: Message, state: FSMContext):
    await message.reply("Введите значения C, M, Y, K через пробел", reply_markup=ReplyKeyboardRemove())
    await state.set_state(CMYKForm.count)


@dp.message(CMYKForm.count)
async def process_cmyk_command(message: Message, state: FSMContext):
    bot_info = await bot.get_me()
    c, m, y, k = None, None, None, None
    try:
        form = await state.update_data(count=message.text)
        c, m, y, k = map(int, form['count'].split())
    except ValueError:
        await message.reply('Вы ввели неверное количество значений❌\nCMYK-значение состоит из 4 чисел от 0 до 100.',
                            reply_markup=main_keyboard)
        await state.clear()
    if c != None and m != None and y != None and k != None:
        response, photo = await request('cmyk', (c, m, y, k))
        if response != 0:
            response_hex = response[0]
            response_r = response[1]
            response_g = response[2]
            response_b = response[3]
            response_c = response[4]
            response_m = response[5]
            response_y = response[6]
            response_k = response[7]
            try:
                await message.reply_photo(photo=BufferedInputFile(photo, 'output.png'),
                                          caption=
                                          f'✨ HEX: #{response_hex}\n'
                                          f'✨ RGB: {response_r} {response_g} {response_b}\n'
                                          f'✨ CMYK: {response_c} {response_m} {response_y} {response_k}\n\n'
                                          f'🔗 {ans_url}{response_hex}\n'
                                          f'📤 t.me/share/url?url=t.me/{bot_info.username}/?start=hex_{response_hex}',
                                          reply_markup=main_keyboard)
                await state.clear()
            except TelegramBadRequest as e:
                await bot.send_message(ADMIN_ID,
                                       f'{'@' + message.from_user.username if message.from_user.username else 'tg://openmessage?user_id=' + str(message.from_user.id)}\n{e}')
                await message.reply(
                    'Telegram не смог отправить изображение❌\nПопробуйте выполнить другой запрос, а затем повторить этот или выполните запрос позже.',
                    reply_markup=main_keyboard)
                await message.reply(
                    f'✨ HEX: #{response_hex}\n'
                    f'✨ RGB: {response_r} {response_g} {response_b}\n'
                    f'✨ CMYK: {response_c} {response_m} {response_y} {response_k}\n\n'
                    f'🔗 {ans_url}{response_hex}\n'
                    f'📤 t.me/share/url?url=t.me/{bot_info.username}/?start=hex_{response_hex}',
                    reply_markup=main_keyboard)
                await state.clear()

            except Exception as e:
                await bot.send_message(ADMIN_ID,
                                       f'{'@' + message.from_user.username if message.from_user.username else 'tg://openmessage?user_id=' + str(message.from_user.id)}\n{e}')
                await message.reply('Непредвиденная ошибка❌', reply_markup=main_keyboard)
                await state.clear()
        else:
            await message.reply('Вы ввели недопустимое значение❌\nCMYK-значение состоит из 4 чисел от 0 до 100.',
                                reply_markup=main_keyboard)
            await state.clear()


@dp.message(F.text == '🔽 Свернуть клавиатуру')
async def hide_keyboard(message: Message):
    await message.reply('Клавиатура скрыта. \nДля повторного открытия воспользуйтесь командой /start или /help',
                        reply_markup=ReplyKeyboardRemove())


# Неотправленное сообщение вида "@botusername_bot system values", где system - rgb, hex, cmyk или year, values - r,g,b, hex или c,m,y,k в зависимости от system
@dp.inline_query()
async def inline_mode(inline_query: InlineQuery):
    response = 0
    bot_info = await bot.get_me()
    check = True
    scheme = []
    query_id = ''
    try:
        query = inline_query.query
        query_id = inline_query.id
        scheme = query.split()
    except ValueError:
        pass
    except Exception as e:
        await bot.send_message(ADMIN_ID,
                               f'{'@' + inline_query.from_user.username if inline_query.from_user.username else 'tg://openmessage?user_id=' + str(inline_query.from_user.id)}\n{e}')
    if bool(scheme) and bool(query_id):
        try:
            if scheme[0].lower() == 'hex' and len(scheme) >= 2:
                response, _ = await request(scheme[0], scheme[1])
            elif (scheme[0].lower() == 'rgb' and len(scheme) >= 3 or (scheme[0].lower() == 'cmyk' and len(scheme) >= 4)):
                response, _ = await request(scheme[0], scheme[1:])
            elif scheme[0].lower() == 'year' and len(scheme) >= 2:
                pass
            else:
                check = False

            if check and scheme[0].lower() != 'year' and response != 0:
                response_hex = str(response['hex']['clean']).upper()
                response_r = 0 if response['rgb']['r'] is None else response['rgb']['r']
                response_g = 0 if response['rgb']['g'] is None else response['rgb']['g']
                response_b = 0 if response['rgb']['b'] is None else response['rgb']['b']
                response_c = 0 if response['cmyk']['c'] is None else response['cmyk']['c']
                response_m = 0 if response['cmyk']['m'] is None else response['cmyk']['m']
                response_y = 0 if response['cmyk']['y'] is None else response['cmyk']['y']
                response_k = 0 if response['cmyk']['k'] is None else response['cmyk']['k']
                await inline_query.answer(
                    # Ответы в inline-режиме состоят из отправляемого сообщения и их вида на предпросмотре
                    [InlineQueryResultPhoto(
                        type=InlineQueryResultType.PHOTO,
                        # id для каждого ответа должен быть уникальным (для конкретного бота, необязательно для всех), для этого удобно использовать id запроса, т.к. он изначально уникальный
                        id=str(int(query_id) + 1),
                        photo_url=f'{ans_pic}{response_hex}/{response_hex}.jpeg',
                        thumbnail_url=f'{ans_pic}{response_hex}/{response_hex}.jpeg',
                        caption=f'✨ HEX: #{response_hex}\n'
                                f'✨ RGB: {response_r} {response_g} {response_b}\n'
                                f'✨ CMYK: {response_c} {response_m} {response_y} {response_k}\n\n'
                                f'🔗 {ans_url}{response_hex}\n'
                                f'📤 t.me/{bot_info.username}/?start=hex_{response_hex}',
                        title=f'С фото',
                        description=f'HEX: #{response_hex}\n'
                                    f'RGB: {response_r} {response_g} {response_b}\n'
                                    f'CMYK: {response_c} {response_m} {response_y} {response_k}'
                    ),
                        InlineQueryResultArticle(
                            id=str(int(query_id) + 2),
                            type=InlineQueryResultType.ARTICLE,
                            title=f'Без фото',
                            input_message_content=InputTextMessageContent(
                                message_text=f'✨ HEX: #{response_hex}\n'
                                             f'✨ RGB: {response_r} {response_g} {response_b}\n'
                                             f'✨ CMYK: {response_c} {response_m} {response_y} {response_k}\n\n'
                                             f'🔗 {ans_url}{response_hex}\n'
                                             f'📤 t.me/{bot_info.username}/?start=hex_{response_hex}'),
                            hide_url=True,
                            description=f'HEX: #{response_hex}\n'
                                        f'RGB: {response_r} {response_g} {response_b}\n'
                                        f'CMYK: {response_c} {response_m} {response_y} {response_k}',
                        )])
            elif scheme[0].lower() == 'year':
                ans = []
                year = ''
                try:
                    year = scheme[1]
                except ValueError:
                    pass
                now = list(year_pantone.keys())[-1]
                if year.isnumeric():
                    if 2000 <= int(year) <= now:
                        for i in range(len(year_pantone[int(year)])):
                            ans.append(InlineQueryResultPhoto(
                    type=InlineQueryResultType.PHOTO,
                    id=str(int(query_id) + 2 * i + 1),
                    photo_url=f'{ans_pic}{year_pantone[int(year)][i][2]}/{year_pantone[int(year)][i][2]}.jpeg',
                    thumbnail_url=f'{ans_pic}{year_pantone[int(year)][i][2]}/{year_pantone[int(year)][i][2]}.jpeg',
                    caption=f'✨ Pantone: {year_pantone[int(year)][i][0]}\n'
                            f'✨ HEX: #{year_pantone[int(year)][i][2]}\n'
                            f'✨ RGB: {year_pantone[int(year)][i][1]}\n'
                            f'✨ CMYK: {year_pantone[int(year)][i][3]}\n\n'
                            f'🔗 {ans_url}{year_pantone[int(year)][i][2]}\n'
                            f'📤 t.me/{bot_info.username}/?start=year_{year}',
                    title=f'С фото',
                    description=f'Pantone: {year_pantone[int(year)][i][0]}\n'
                                f'HEX: #{year_pantone[int(year)][i][2]}\n'
                                f'RGB: {year_pantone[int(year)][i][1]}\n'
                                f'CMYK: {year_pantone[int(year)][i][3]}'
                ))
                            ans.append(InlineQueryResultArticle(
                        id=str(int(query_id) + 2 * i + 2),
                        type=InlineQueryResultType.ARTICLE,
                        title=f'Без фото',
                        input_message_content=InputTextMessageContent(
                            message_text=f'✨ Pantone: {year_pantone[int(year)][i][0]}\n'
                                         f'✨ HEX: #{year_pantone[int(year)][i][2]}\n'
                                         f'✨ RGB: {year_pantone[int(year)][i][1]}\n'
                                         f'✨ CMYK: {year_pantone[int(year)][i][3]}\n\n'
                                         f'🔗 {ans_url}{year_pantone[int(year)][i][2]}\n'
                                         f'📤 t.me/{bot_info.username}/?start=year_{year}'),
                        hide_url=True,
                        description=f'Pantone: {year_pantone[int(year)][i][0]}\n'
                                    f'HEX: #{year_pantone[int(year)][i][2]}\n'
                                    f'RGB: {year_pantone[int(year)][i][1]}\n'
                                    f'CMYK: {year_pantone[int(year)][i][3]}'
                    ))
                await inline_query.answer(ans)

        except UnboundLocalError:
            pass
        except ValueError:
            pass
        except IndexError:
            pass
        except Exception as e:
            await bot.send_message(ADMIN_ID,
                                   f'{'@' + inline_query.from_user.username if inline_query.from_user.username else 'tg://openmessage?user_id=' + str(inline_query.from_user.id)}\n{e}')


@dp.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=JOIN_TRANSITION))
async def add_to_chat(chat: ChatMemberUpdated):
    await bot.send_message(chat.chat.id,
                           'Спасибо, что добавили меня в чат! ☺️\nЧтобы я реагировал на кнопки и значения после них без прав администратора, отвечайте на мои сообщения.')


@dp.message()
async def send_echo(message: Message):
    if message.chat.id == message.from_user.id:
        await message.reply('Я вас не понимаю😔\nВведите или нажмите /start или /help, чтобы получить информацию.')


async def on_startup():
    bot_info = await bot.get_me()
    await bot.send_message(ADMIN_ID, f'Бот @{bot_info.username} включён')


async def on_shutdown():
    bot_info = await bot.get_me()
    await bot.send_message(ADMIN_ID, f'Бот @{bot_info.username} выключен')


async def main():
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
