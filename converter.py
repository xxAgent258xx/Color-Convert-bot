import asyncio
import logging

import aiohttp
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, CommandObject
from aiogram.exceptions import *
from aiogram.enums.inline_query_result_type import InlineQueryResultType
from aiogram.types import Message, FSInputFile, BufferedInputFile, ReplyKeyboardMarkup, KeyboardButton, \
    ReplyKeyboardRemove, InlineQuery, \
    InlineQueryResultPhoto, InlineQueryResultArticle, InputTextMessageContent
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
year_pantone = '17-1230'
year_rgb = '164 120 100'
year_hex = 'A47864'
year_cmyk = '0 27 39 36'
# Меню бота
main_keyboard = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='🎨 Из RGB'), KeyboardButton(text='🎨 Из CMYK'),
     KeyboardButton(text='🎨 Из HEX')],
    [KeyboardButton(text='🔙 Главное меню'), KeyboardButton(text='🌈Цвет 2025 года'),
     KeyboardButton(text='🔽 Свернуть клавиатуру')]
], resize_keyboard=True)


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
            await message.reply_photo(photo=FSInputFile('year.png'),
                                      caption=f'✨ Pantone: {year_pantone}\n'
                                              f'✨ HEX: #{year_hex}\n'
                                              f'✨ RGB: {year_rgb}\n'
                                              f'✨ CMYK: {year_cmyk}\n\n'
                                              f'🔗 {ans_url}{year_hex}\n'
                                              f'📤 t.me/share/url?url=t.me/{bot_info.username}/?start=year',
                                      reply_markup=main_keyboard)
        else:
            if args[0].lower() == 'rgb':
                r, g, b = args[1], args[2], args[3]
                if 0 <= int(r) <= 255 and 0 <= int(g) <= 255 and 0 <= int(b) <= 255:
                    async with aiohttp.ClientSession() as session:
                        async with session.get(f'{api_url}rgb=rgb({r},{g},{b})') as response_:
                            response = await response_.json()
                        async with session.get(
                                f'{ans_pic}{str(response['hex']['clean']).upper()}/{str(response['hex']['clean']).upper()}.png') as response_2:
                            photo = await response_2.content.read()

            elif args[0].lower() == 'hex':
                hex = args[1]
                if len(hex) == 6 or len(hex) == 3:
                    async with aiohttp.ClientSession() as session:
                        async with session.get(f'{api_url}hex={hex}') as response_:
                            response = await response_.json()
                        async with session.get(
                                f'{ans_pic}{str(response['hex']['clean']).upper()}/{str(response['hex']['clean']).upper()}.png') as response_2:
                            photo = await response_2.content.read()

            elif args[0].lower() == 'cmyk':
                c, m, y, k = args[1], args[2], args[3], args[4]
                if 0 <= int(c) <= 100 and 0 <= int(m) <= 100 and 0 <= int(y) <= 100 and 0 <= int(k) <= 100:
                    async with aiohttp.ClientSession() as session:
                        async with session.get(f'{api_url}cmyk=cmyk({c},{m},{y},{k})') as response_:
                            response = await response_.json()
                        async with session.get(
                                f'{ans_pic}{str(response['hex']['clean']).upper()}/{str(response['hex']['clean']).upper()}.png') as response_2:
                            photo = await response_2.content.read()

            try:
                response_hex = str(response['hex']['clean']).upper()
                response_r = 0 if response['rgb']['r'] is None else response['rgb']['r']
                response_g = 0 if response['rgb']['g'] is None else response['rgb']['g']
                response_b = 0 if response['rgb']['b'] is None else response['rgb']['b']
                response_c = 0 if response['cmyk']['c'] is None else response['cmyk']['c']
                response_m = 0 if response['cmyk']['m'] is None else response['cmyk']['m']
                response_y = 0 if response['cmyk']['y'] is None else response['cmyk']['y']
                response_k = 0 if response['cmyk']['k'] is None else response['cmyk']['k']

                await message.reply_photo(photo=BufferedInputFile(photo, 'output.png'),
                                          caption=
                                          f'✨ HEX: #{response_hex}\n'
                                          f'✨ RGB: {response_r} {response_g} {response_b}\n'
                                          f'✨ CMYK: {response_c} {response_m} {response_y} {response_k}\n\n'
                                          f'🔗 {ans_url}{response_hex}\n'
                                          f'📤 t.me/share/url?url=t.me/{bot_info.username}/?start=hex_{response_hex}',
                                          reply_markup=main_keyboard)
            except ValueError:
                await message.reply('Добро пожаловать в бота для конвертации цветов! 👋\n\n'
                                    'Нажмите на кнопку снизу, а затем введите значения⌨️\n'
                                    f'Или напишите / или @{bot_info.username}, цветовую модель, а затем значения✍️\n\n'
                                    'Например: 🔍\n'
                                    '/hex FFFFFF\n'
                                    '/rgb 255 255 255\n'
                                    f'@{bot_info.username} cmyk 0 0 0 0',
                                    reply_markup=main_keyboard
                                    )
            except IndexError:
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
    await message.reply(f'📋Полный список команд:\n'
                        f'/start, /help;\n\n'
                        f'/hex HEX или @{bot_info.username} hex HEX,\n'
                        f'где HEX - 3 или 6 символов от 0 до 9 и от A до F;\n\n'
                        f'/rgb R G B или @{bot_info.username} rgb R G B,\n'
                        f'где R, G, B - числа от 0 до до 255;\n\n'
                        f'/cmyk C M Y K или @{bot_info.username} cmyk C M Y K,\n'
                        f'где C, M, Y, K - числа от 0 до 100;\n\n'
                        f'/year или @{bot_info.username} year;',
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
        if len(hex) == 6 or len(hex) == 3:
            # Создание сессии для запросов
            async with aiohttp.ClientSession() as session:
                # Получение значений hex, r,g,b, c,m,y,k
                async with session.get(f'{api_url}hex={hex}') as response_:
                    response = await response_.json()
                # Получение фото
                async with session.get(
                        f'{ans_pic}{str(response['hex']['clean']).upper()}/{str(response['hex']['clean']).upper()}.png') as response_2:
                    photo = await response_2.content.read()
            response_hex = str(response['hex']['clean']).upper()
            # Запись в переменные, проверка на непустое значение
            response_r = 0 if response['rgb']['r'] is None else response['rgb']['r']
            response_g = 0 if response['rgb']['g'] is None else response['rgb']['g']
            response_b = 0 if response['rgb']['b'] is None else response['rgb']['b']
            response_c = 0 if response['cmyk']['c'] is None else response['cmyk']['c']
            response_m = 0 if response['cmyk']['m'] is None else response['cmyk']['m']
            response_y = 0 if response['cmyk']['y'] is None else response['cmyk']['y']
            response_k = 0 if response['cmyk']['k'] is None else response['cmyk']['k']
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
        if 0 <= int(r) <= 255 and 0 <= int(g) <= 255 and 0 <= int(b) <= 255:
            async with aiohttp.ClientSession() as session:
                async with session.get(f'{api_url}rgb=rgb({r},{g},{b})') as response_:
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
        if 0 <= int(c) <= 100 and 0 <= int(m) <= 100 and 0 <= int(y) <= 100 and 0 <= int(k) <= 100:
            async with aiohttp.ClientSession() as session:
                async with session.get(f'{api_url}cmyk={c},{m},{y},{k}') as response_:
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


# Команда "/year" или аналогичная кнопка
@dp.message(F.text == '🌈Цвет 2025 года')
@dp.message(Command(commands=['year']))
async def process_year_command(message: Message):
    bot_info = await bot.get_me()
    try:
        await message.reply_photo(photo=FSInputFile('year.png'),
                                  caption=f'✨ Pantone: {year_pantone}\n'
                                          f'✨ HEX: #{year_hex}\n'
                                          f'✨ RGB: {year_rgb}\n'
                                          f'✨ CMYK: {year_cmyk}\n\n'
                                          f'🔗 {ans_url}{year_hex}\n'
                                          f'📤 t.me/share/url?url=t.me/{bot_info.username}/?start=year',
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
    r, g, b = False, False, False
    try:
        # Теперь значения читаются не из сообщения, а из машины состояний
        form = await state.update_data(count=message.text)
        r, g, b = map(int, form['count'].split())
    except ValueError:
        await message.reply('Вы ввели неверное количество значений❌\nRGB-значение состоит из 3 чисел от 0 до 255.',
                            reply_markup=main_keyboard)
        await state.clear()
    if r != False and g != False and b != False:
        if 0 <= int(r) <= 255 and 0 <= int(g) <= 255 and 0 <= int(b) <= 255:
            async with aiohttp.ClientSession() as session:
                async with session.get(f'{api_url}rgb=rgb({r},{g},{b})') as response_:
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
    hex = False
    try:
        form = await state.update_data(count=message.text)
        hex = form['count']
    except ValueError:
        await message.reply(
            'Вы ввели неверное количество значений❌\nHEX-значение состоит из 3 или 6 символов от 0 до 9 и от A до F.',
            reply_markup=main_keyboard)
        await state.clear()
    if hex != False:
        if len(hex) == 6 or len(hex) == 3:
            async with aiohttp.ClientSession() as session:
                async with session.get(f'{api_url}hex={hex}') as response_:
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
    c, m, y, k = False, False, False, False
    try:
        form = await state.update_data(count=message.text)
        c, m, y, k = map(int, form['count'].split())
    except ValueError:
        await message.reply('Вы ввели неверное количество значений❌\nCMYK-значение состоит из 4 чисел от 0 до 100.',
                            reply_markup=main_keyboard)
        await state.clear()
    if c != False and m != False and y != False and k != False:
        if 0 <= int(c) <= 100 and 0 <= int(m) <= 100 and 0 <= int(y) <= 100 and 0 <= int(k) <= 100:
            async with aiohttp.ClientSession() as session:
                async with session.get(f'{api_url}cmyk={c},{m},{y},{k}') as response_:
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
            if scheme[0].lower() == 'rgb':
                r, g, b = scheme[1], scheme[2], scheme[3]
                if 0 <= int(r) <= 255 and 0 <= int(g) <= 255 and 0 <= int(b) <= 255:
                    async with aiohttp.ClientSession() as session:
                        async with session.get(f'{api_url}rgb=rgb({r},{g},{b})') as response_:
                            response = await response_.json()

            elif scheme[0].lower() == 'hex':
                hex = scheme[1]
                if len(hex) == 6 or len(hex) == 3:
                    async with aiohttp.ClientSession() as session:
                        async with session.get(f'{api_url}hex={hex}') as response_:
                            response = await response_.json()

            elif scheme[0].lower() == 'cmyk':
                c, m, y, k = scheme[1], scheme[2], scheme[3], scheme[4]
                if 0 <= int(c) <= 100 and 0 <= int(m) <= 100 and 0 <= int(y) <= 100 and 0 <= int(k) <= 100:
                    async with aiohttp.ClientSession() as session:
                        async with session.get(f'{api_url}cmyk=cmyk({c},{m},{y},{k})') as response_:
                            response = await response_.json()

            elif scheme[0].lower() == 'year':
                pass

            else:
                check = False

            if check and scheme[0].lower() != 'year':
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
                await inline_query.answer(
                    [InlineQueryResultPhoto(
                        type=InlineQueryResultType.PHOTO,
                        id=str(int(query_id) + 1),
                        photo_url=f'{ans_pic}{year_hex}/{year_hex}.jpeg',
                        thumbnail_url=f'{ans_pic}{year_hex}/{year_hex}.jpeg',
                        caption=f'✨ Pantone: {year_pantone}\n'
                                f'✨ HEX: #{year_hex}\n'
                                f'✨ RGB: {year_rgb}\n'
                                f'✨ CMYK: {year_cmyk}\n\n'
                                f'🔗 {ans_url}{year_hex}\n'
                                f'📤 t.me/{bot_info.username}/?start=year',
                        title=f'С фото',
                        description=f'Pantone: {year_pantone}\n'
                                    f'HEX: #{year_hex}\n'
                                    f'RGB: {year_rgb}\n'
                                    f'CMYK: {year_cmyk}'
                    ),
                        InlineQueryResultArticle(
                            id=str(int(query_id) + 2),
                            type=InlineQueryResultType.ARTICLE,
                            title=f'Без фото',
                            input_message_content=InputTextMessageContent(
                                message_text=f'✨ Pantone: {year_pantone}\n'
                                             f'✨ HEX: #{year_hex}\n'
                                             f'✨ RGB: {year_rgb}\n'
                                             f'✨ CMYK: {year_cmyk}\n\n'
                                             f'🔗 {ans_url}{year_hex}\n'
                                             f'📤 t.me/{bot_info.username}/?start=year'),
                            hide_url=True,
                            description=f'Pantone: {year_pantone}\n'
                                        f'HEX: #{year_hex}\n'
                                        f'RGB: {year_rgb}\n'
                                        f'CMYK: {year_cmyk}'
                        )])

        except UnboundLocalError:
            pass
        except ValueError:
            pass
        except IndexError:
            pass
        except Exception as e:
            await bot.send_message(ADMIN_ID,
                                   f'{'@' + inline_query.from_user.username if inline_query.from_user.username else 'tg://openmessage?user_id=' + str(inline_query.from_user.id)}\n{e}')


@dp.message()
async def send_echo(message: Message):
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
