import asyncio
import datetime
import logging
import os
from json import loads
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.enums.inline_query_result_type import InlineQueryResultType
from aiogram.types import Message, FSInputFile, ReplyKeyboardRemove, InlineQuery, InlineQueryResultPhoto, \
    InlineQueryResultArticle, InputTextMessageContent
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
import requests
from io import BytesIO
import imageio.v2 as imageio
from convertertoken import BOT_TOKEN, ADMIN_TAG, ADMIN_ID


class RGBForm(StatesGroup):
    count = State()


class HEXForm(StatesGroup):
    count = State()


class CMYKForm(StatesGroup):
    count = State()


storage = MemoryStorage()
logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=storage)
api_url = 'https://www.thecolorapi.com/id?'
api_pic = 'https://www.thecolorapi.com/id?format=svg&named=false&'
main_keyboard = types.ReplyKeyboardMarkup(keyboard=[
    [types.KeyboardButton(text='🎨 Из RGB'), types.KeyboardButton(text='🎨 Из CMYK'),
     types.KeyboardButton(text='🎨 Из HEX')],
    [types.KeyboardButton(text='🔙 Главное меню'), types.KeyboardButton(text='⚙️ Техподдержка'),
     types.KeyboardButton(text='🔽 Свернуть клавиатуру')]
], resize_keyboard=True)


@dp.message(Command(commands=['start', 'help']))
async def process_start_command(message: Message):
    await message.reply('Добро пожаловать в бота для конвертации цветов! 👋\n\n'
                        'Нажмите на кнопку снизу а затем введите значения⌨️\n'
                        'Или напишите / или @ColorConvertBot, цветовую модель, а затем значения✍️\n\n'
                        'Например: 🔍\n'
                        '/hex FFFFFF\n'
                        '/rgb 255 255 255\n'
                        '@ColorConvertBot cmyk 0 0 0 0',
                        reply_markup=main_keyboard
                        )


@dp.message(Command(commands=['hex']))
async def process_hex_command(message: Message):
    try:
        _, hex = message.text.split()
        if len(hex) == 6 or len(hex) == 3:
            response = requests.get(f'{api_url}hex={hex}').json()
            pic = requests.get(f'https://via.placeholder.com/500x500/{hex}/{hex}.png').content
            image = imageio.imread(BytesIO(pic))
            imageio.imwrite('output.png', image)

            await message.reply_photo(photo=FSInputFile('output.png'), caption=
            f'✨HEX: {response['hex']['value']}\n'
            f'✨RGB: {int(bool(response['rgb']['r'])) if response['rgb']['r'] is None else response['rgb']['r']} {int(bool(response['rgb']['g'])) if response['rgb']['g'] is None else response['rgb']['g']} {int(bool(response['rgb']['b'])) if response['rgb']['b'] is None else response['rgb']['b']}\n'
            f'✨CMYK: {int(bool(response['cmyk']['c'])) if response['cmyk']['c'] is None else response['cmyk']['c']} {int(bool(response['cmyk']['m'])) if response['cmyk']['m'] is None else response['cmyk']['m']} {int(bool(response['cmyk']['y'])) if response['cmyk']['y'] is None else response['cmyk']['y']} {int(bool(response['cmyk']['k'])) if response['cmyk']['k'] is None else response['cmyk']['k']}\n'
            f'✨https://get-color.ru/code/{response['hex']['clean']}', reply_markup=main_keyboard)
        else:
            await message.reply('Вы ввели недопустимое значение❌', reply_markup=main_keyboard)
    except:
        await message.reply('Вы ввели неверное количество значений❌', reply_markup=main_keyboard)


@dp.message(Command(commands=['rgb']))
async def process_rgb_command(message: Message):
    try:
        _, r, g, b = message.text.split()
        if 0 <= int(r) <= 255 and 0 <= int(g) <= 255 and 0 <= int(b) <= 255:
            response = requests.get(f'{api_url}rgb=rgb({r},{g},{b})').json()
            pic = requests.get(
                f'https://via.placeholder.com/500x500/{response['hex']['clean']}/{response['hex']['clean']}.png').content
            image = imageio.imread(BytesIO(pic))
            imageio.imwrite('output.png', image)

            await message.reply_photo(photo=FSInputFile('output.png'), caption=
            f'✨HEX: {response['hex']['value']}\n'
            f'✨RGB: {int(bool(response['rgb']['r'])) if response['rgb']['r'] is None else response['rgb']['r']} {int(bool(response['rgb']['g'])) if response['rgb']['g'] is None else response['rgb']['g']} {int(bool(response['rgb']['b'])) if response['rgb']['b'] is None else response['rgb']['b']}\n'
            f'✨CMYK: {int(bool(response['cmyk']['c'])) if response['cmyk']['c'] is None else response['cmyk']['c']} {int(bool(response['cmyk']['m'])) if response['cmyk']['m'] is None else response['cmyk']['m']} {int(bool(response['cmyk']['y'])) if response['cmyk']['y'] is None else response['cmyk']['y']} {int(bool(response['cmyk']['k'])) if response['cmyk']['k'] is None else response['cmyk']['k']}\n'
            f'✨https://get-color.ru/code/{response['hex']['clean']}', reply_markup=main_keyboard)
        else:
            await message.reply('Вы ввели недопустимое значение❌', reply_markup=main_keyboard)
    except:
        await message.reply('Вы ввели неверное количество значений❌', reply_markup=main_keyboard)


@dp.message(Command(commands=['cmyk']))
async def process_cmyk_command(message: Message):
    try:
        _, c, m, y, k = message.text.split()
        if 0 <= int(c) <= 100 and 0 <= int(m) <= 100 and 0 <= int(y) <= 100 and 0 <= int(k) <= 100:
            response = requests.get(f'{api_url}cmyk={c},{m},{y},{k}').json()
            pic = requests.get(
                f'https://via.placeholder.com/500x500/{response['hex']['clean']}/{response['hex']['clean']}.png').content
            image = imageio.imread(BytesIO(pic))
            imageio.imwrite('output.png', image)

            await message.reply_photo(photo=FSInputFile('output.png'), caption=
            f'✨HEX: {response['hex']['value']}\n'
            f'✨RGB: {int(bool(response['rgb']['r'])) if response['rgb']['r'] is None else response['rgb']['r']} {int(bool(response['rgb']['g'])) if response['rgb']['g'] is None else response['rgb']['g']} {int(bool(response['rgb']['b'])) if response['rgb']['b'] is None else response['rgb']['b']}\n'
            f'✨CMYK: {int(bool(response['cmyk']['c'])) if response['cmyk']['c'] is None else response['cmyk']['c']} {int(bool(response['cmyk']['m'])) if response['cmyk']['m'] is None else response['cmyk']['m']} {int(bool(response['cmyk']['y'])) if response['cmyk']['y'] is None else response['cmyk']['y']} {int(bool(response['cmyk']['k'])) if response['cmyk']['k'] is None else response['cmyk']['k']}\n'
            f'✨https://get-color.ru/code/{response['hex']['clean']}', reply_markup=main_keyboard)

        else:
            await message.reply('Вы ввели недопустимое значение❌', reply_markup=main_keyboard)
    except:
        await message.reply('Вы ввели неверное количество значений❌', reply_markup=main_keyboard)


@dp.message(F.text == '🎨 Из RGB')
async def button_rgb(message: Message, state: FSMContext):
    await message.reply("Введите значения R, G, B через пробел", reply_markup=ReplyKeyboardRemove())
    await state.set_state(RGBForm.count)


@dp.message(RGBForm.count)
async def process_rgb_command(message: Message, state: FSMContext):
    try:
        form = await state.update_data(count=message.text)
        r, g, b = map(int, form['count'].split())
        if 0 <= int(r) <= 255 and 0 <= int(g) <= 255 and 0 <= int(b) <= 255:
            response = requests.get(f'{api_url}rgb=rgb({r},{g},{b})').json()
            pic = requests.get(
                f'https://via.placeholder.com/500x500/{response['hex']['clean']}/{response['hex']['clean']}.png').content
            image = imageio.imread(BytesIO(pic))
            imageio.imwrite('output.png', image)

            await message.reply_photo(photo=FSInputFile('output.png'), caption=
            f'✨HEX: {response['hex']['value']}\n'
            f'✨RGB: {int(bool(response['rgb']['r'])) if response['rgb']['r'] is None else response['rgb']['r']} {int(bool(response['rgb']['g'])) if response['rgb']['g'] is None else response['rgb']['g']} {int(bool(response['rgb']['b'])) if response['rgb']['b'] is None else response['rgb']['b']}\n'
            f'✨CMYK: {int(bool(response['cmyk']['c'])) if response['cmyk']['c'] is None else response['cmyk']['c']} {int(bool(response['cmyk']['m'])) if response['cmyk']['m'] is None else response['cmyk']['m']} {int(bool(response['cmyk']['y'])) if response['cmyk']['y'] is None else response['cmyk']['y']} {int(bool(response['cmyk']['k'])) if response['cmyk']['k'] is None else response['cmyk']['k']}\n'
            f'✨https://get-color.ru/code/{response['hex']['clean']}', reply_markup=main_keyboard)
            await state.clear()
        else:
            await message.reply('Вы ввели недопустимое значение❌', reply_markup=main_keyboard)
            await state.clear()
    except Exception as e:
        print(e)
        await message.reply('Вы ввели неверное количество значений❌', reply_markup=main_keyboard)
        await state.clear()


@dp.message(F.text == '🎨 Из HEX')
async def button_hex(message: Message, state: FSMContext):
    await message.reply("Введите значение HEX", reply_markup=ReplyKeyboardRemove())
    await state.set_state(HEXForm.count)


@dp.message(HEXForm.count)
async def process_hex_command(message: Message, state: FSMContext):
    try:
        form = await state.update_data(count=message.text)
        hex = form['count']
        if len(hex) == 6 or len(hex) == 3:
            response = requests.get(f'{api_url}hex={hex}').json()
            pic = requests.get(f'https://via.placeholder.com/500x500/{hex}/{hex}.png').content
            image = imageio.imread(BytesIO(pic))
            imageio.imwrite('output.png', image)

            await message.reply_photo(photo=FSInputFile('output.png'), caption=
            f'✨HEX: {response['hex']['value']}\n'
            f'✨RGB: {int(bool(response['rgb']['r'])) if response['rgb']['r'] is None else response['rgb']['r']} {int(bool(response['rgb']['g'])) if response['rgb']['g'] is None else response['rgb']['g']} {int(bool(response['rgb']['b'])) if response['rgb']['b'] is None else response['rgb']['b']}\n'
            f'✨CMYK: {int(bool(response['cmyk']['c'])) if response['cmyk']['c'] is None else response['cmyk']['c']} {int(bool(response['cmyk']['m'])) if response['cmyk']['m'] is None else response['cmyk']['m']} {int(bool(response['cmyk']['y'])) if response['cmyk']['y'] is None else response['cmyk']['y']} {int(bool(response['cmyk']['k'])) if response['cmyk']['k'] is None else response['cmyk']['k']}\n'
            f'✨https://get-color.ru/code/{response['hex']['clean']}', reply_markup=main_keyboard)
            await state.clear()
        else:
            await message.reply('Вы ввели недопустимое значение❌', reply_markup=main_keyboard)
            await state.clear()
    except:
        await message.reply('Вы ввели неверное количество значений❌', reply_markup=main_keyboard)
        await state.clear()


@dp.message(F.text == '🎨 Из CMYK')
async def button_cmyk(message: Message, state: FSMContext):
    await message.reply("Введите значения C, M, Y, K через пробел", reply_markup=ReplyKeyboardRemove())
    await state.set_state(CMYKForm.count)


@dp.message(CMYKForm.count)
async def process_cmyk_command(message: Message, state: FSMContext):
    try:
        form = await state.update_data(count=message.text)
        c, m, y, k = map(int, form['count'].split())
        if 0 <= int(c) <= 100 and 0 <= int(m) <= 100 and 0 <= int(y) <= 100 and 0 <= int(k) <= 100:
            response = requests.get(f'{api_url}cmyk={c},{m},{y},{k}').json()
            pic = requests.get(
                f'https://via.placeholder.com/500x500/{response['hex']['clean']}/{response['hex']['clean']}.png').content
            image = imageio.imread(BytesIO(pic))
            imageio.imwrite('output.png', image)

            await message.reply_photo(photo=FSInputFile('output.png'), caption=
            f'✨HEX: {response['hex']['value']}\n'
            f'✨RGB: {int(bool(response['rgb']['r'])) if response['rgb']['r'] is None else response['rgb']['r']} {int(bool(response['rgb']['g'])) if response['rgb']['g'] is None else response['rgb']['g']} {int(bool(response['rgb']['b'])) if response['rgb']['b'] is None else response['rgb']['b']}\n'
            f'✨CMYK: {int(bool(response['cmyk']['c'])) if response['cmyk']['c'] is None else response['cmyk']['c']} {int(bool(response['cmyk']['m'])) if response['cmyk']['m'] is None else response['cmyk']['m']} {int(bool(response['cmyk']['y'])) if response['cmyk']['y'] is None else response['cmyk']['y']} {int(bool(response['cmyk']['k'])) if response['cmyk']['k'] is None else response['cmyk']['k']}\n'
            f'✨https://get-color.ru/code/{response['hex']['clean']}', reply_markup=main_keyboard)
            await state.clear()
        else:
            await message.reply('Вы ввели недопустимое значение❌', reply_markup=main_keyboard)
            await state.clear()
    except:
        await message.reply('Вы ввели неверное количество значений❌', reply_markup=main_keyboard)
        await state.clear()


@dp.message(F.text == '⚙️ Техподдержка')
async def support(message: Message):
    await message.reply(f'{ADMIN_TAG}', reply_markup=main_keyboard)


@dp.message(F.text == '🔽 Свернуть клавиатуру')
async def support(message: Message):
    await message.reply('Клавиатура скрыта. \nДля повторного открытия воспользуйтесь командой /start или /help',
                        reply_markup=ReplyKeyboardRemove())


@dp.message(F.text == '🔙 Главное меню')
async def process_start_command(message: Message):
    await message.reply('Добро пожаловать в бота для конвертации цветов! 👋\n\n'
                        'Нажмите на кнопку снизу а затем введите значения⌨️\n'
                        'Или напишите / или @ColorConvertBot, цветовую модель, а затем значения✍️\n\n'
                        'Например: 🔍\n'
                        '/hex FFFFFF\n'
                        '/rgb 255 255 255\n'
                        '@ColorConvertBot cmyk 0 0 0 0',
                        reply_markup=main_keyboard
                        )


@dp.inline_query()
async def inline_mode(inline_query: InlineQuery):
    try:
        jsonquery = inline_query.json()
        query: str = loads(jsonquery)['query']
        query_id: str = loads(jsonquery)['id']
        scheme: list[str] = query.split(' ')
        if scheme[0].lower() == 'rgb':
            r, g, b = scheme[1], scheme[2], scheme[3]
            if 0 <= int(r) <= 255 and 0 <= int(g) <= 255 and 0 <= int(b) <= 255:
                response = requests.get(f'{api_url}rgb=rgb({r},{g},{b})').json()
                pic = requests.get(
                    f'https://via.placeholder.com/500x500/{response['hex']['clean']}/{response['hex']['clean']}.jpeg').content
                await bot.answer_inline_query(query_id,
                                              [InlineQueryResultPhoto(
                                                  type=InlineQueryResultType.PHOTO,
                                                  id=str(int(query_id) + 1),
                                                  photo_url=f'https://via.placeholder.com/500x500/{response['hex']['clean']}/{response['hex']['clean']}.jpeg',
                                                  thumbnail_url=f'https://via.placeholder.com/500x500/{response['hex']['clean']}/{response['hex']['clean']}.jpeg',
                                                  caption=f'✨HEX: {response['hex']['value']}\n'
                                                          f'✨RGB: {int(bool(response['rgb']['r'])) if response['rgb']['r'] is None else response['rgb']['r']} {int(bool(response['rgb']['g'])) if response['rgb']['g'] is None else response['rgb']['g']} {int(bool(response['rgb']['b'])) if response['rgb']['b'] is None else response['rgb']['b']}\n'
                                                          f'✨CMYK: {int(bool(response['cmyk']['c'])) if response['cmyk']['c'] is None else response['cmyk']['c']} {int(bool(response['cmyk']['m'])) if response['cmyk']['m'] is None else response['cmyk']['m']} {int(bool(response['cmyk']['y'])) if response['cmyk']['y'] is None else response['cmyk']['y']} {int(bool(response['cmyk']['k'])) if response['cmyk']['k'] is None else response['cmyk']['k']}\n'
                                                          f'✨https://get-color.ru/code/{response['hex']['clean']}',
                                                  title=f'С фото',
                                                  description=f'HEX: {response['hex']['value']}\n'
                                                              f'RGB: {int(bool(response['rgb']['r'])) if response['rgb']['r'] is None else response['rgb']['r']} {int(bool(response['rgb']['g'])) if response['rgb']['g'] is None else response['rgb']['g']} {int(bool(response['rgb']['b'])) if response['rgb']['b'] is None else response['rgb']['b']}\n'
                                                              f'CMYK: {int(bool(response['cmyk']['c'])) if response['cmyk']['c'] is None else response['cmyk']['c']} {int(bool(response['cmyk']['m'])) if response['cmyk']['m'] is None else response['cmyk']['m']} {int(bool(response['cmyk']['y'])) if response['cmyk']['y'] is None else response['cmyk']['y']} {int(bool(response['cmyk']['k'])) if response['cmyk']['k'] is None else response['cmyk']['k']}'
                                              ),
                                                  InlineQueryResultArticle(
                                                                           id=str(int(query_id) + 2),
                                                                           type=InlineQueryResultType.ARTICLE,
                                                                           title=f'Без фото',
                                                                           input_message_content=InputTextMessageContent(
                                                                               message_text=f'✨HEX: {response['hex']['value']}\n'
                                                                                            f'✨RGB: {int(bool(response['rgb']['r'])) if response['rgb']['r'] is None else response['rgb']['r']} {int(bool(response['rgb']['g'])) if response['rgb']['g'] is None else response['rgb']['g']} {int(bool(response['rgb']['b'])) if response['rgb']['b'] is None else response['rgb']['b']}\n'
                                                                                            f'✨CMYK: {int(bool(response['cmyk']['c'])) if response['cmyk']['c'] is None else response['cmyk']['c']} {int(bool(response['cmyk']['m'])) if response['cmyk']['m'] is None else response['cmyk']['m']} {int(bool(response['cmyk']['y'])) if response['cmyk']['y'] is None else response['cmyk']['y']} {int(bool(response['cmyk']['k'])) if response['cmyk']['k'] is None else response['cmyk']['k']}\n'
                                                                                            f'✨https://get-color.ru/code/{response['hex']['clean']}'),
                                                                           # thumbnail_url=f'https://via.placeholder.com/500x500/{response['hex']['clean']}/{response['hex']['clean']}.jpeg',
                                                                           hide_url=True,
                                                                           description=f'HEX: {response['hex']['value']}\n'
                                                                                       f'RGB: {int(bool(response['rgb']['r'])) if response['rgb']['r'] is None else response['rgb']['r']} {int(bool(response['rgb']['g'])) if response['rgb']['g'] is None else response['rgb']['g']} {int(bool(response['rgb']['b'])) if response['rgb']['b'] is None else response['rgb']['b']}\n'
                                                                                       f'CMYK: {int(bool(response['cmyk']['c'])) if response['cmyk']['c'] is None else response['cmyk']['c']} {int(bool(response['cmyk']['m'])) if response['cmyk']['m'] is None else response['cmyk']['m']} {int(bool(response['cmyk']['y'])) if response['cmyk']['y'] is None else response['cmyk']['y']} {int(bool(response['cmyk']['k'])) if response['cmyk']['k'] is None else response['cmyk']['k']}',
                                                                           )])

        if scheme[0].lower() == 'hex':
            hex = scheme[1]
            if len(hex) == 6 or len(hex) == 3:
                response = requests.get(f'{api_url}hex={hex}').json()
                pic = requests.get(
                    f'https://via.placeholder.com/500x500/{response['hex']['clean']}/{response['hex']['clean']}.jpeg').content
                await bot.answer_inline_query(query_id,
                                              [InlineQueryResultPhoto(
                                                  type=InlineQueryResultType.PHOTO,
                                                  id=str(int(query_id) + 1),
                                                  photo_url=f'https://via.placeholder.com/500x500/{response['hex']['clean']}/{response['hex']['clean']}.jpeg',
                                                  thumbnail_url=f'https://via.placeholder.com/500x500/{response['hex']['clean']}/{response['hex']['clean']}.jpeg',
                                                  caption=f'✨HEX: {response['hex']['value']}\n'
                                                          f'✨RGB: {int(bool(response['rgb']['r'])) if response['rgb']['r'] is None else response['rgb']['r']} {int(bool(response['rgb']['g'])) if response['rgb']['g'] is None else response['rgb']['g']} {int(bool(response['rgb']['b'])) if response['rgb']['b'] is None else response['rgb']['b']}\n'
                                                          f'✨CMYK: {int(bool(response['cmyk']['c'])) if response['cmyk']['c'] is None else response['cmyk']['c']} {int(bool(response['cmyk']['m'])) if response['cmyk']['m'] is None else response['cmyk']['m']} {int(bool(response['cmyk']['y'])) if response['cmyk']['y'] is None else response['cmyk']['y']} {int(bool(response['cmyk']['k'])) if response['cmyk']['k'] is None else response['cmyk']['k']}\n'
                                                          f'✨https://get-color.ru/code/{response['hex']['clean']}',
                                                  title=f'С фото',
                                                  description=f'HEX: {response['hex']['value']}\n'
                                                              f'RGB: {int(bool(response['rgb']['r'])) if response['rgb']['r'] is None else response['rgb']['r']} {int(bool(response['rgb']['g'])) if response['rgb']['g'] is None else response['rgb']['g']} {int(bool(response['rgb']['b'])) if response['rgb']['b'] is None else response['rgb']['b']}\n'
                                                              f'CMYK: {int(bool(response['cmyk']['c'])) if response['cmyk']['c'] is None else response['cmyk']['c']} {int(bool(response['cmyk']['m'])) if response['cmyk']['m'] is None else response['cmyk']['m']} {int(bool(response['cmyk']['y'])) if response['cmyk']['y'] is None else response['cmyk']['y']} {int(bool(response['cmyk']['k'])) if response['cmyk']['k'] is None else response['cmyk']['k']}'
                                              ),
                                                  InlineQueryResultArticle(
                                                      id=str(int(query_id) + 2),
                                                      type=InlineQueryResultType.ARTICLE,
                                                      title=f'Без фото',
                                                      input_message_content=InputTextMessageContent(
                                                          message_text=f'✨HEX: {response['hex']['value']}\n'
                                                                       f'✨RGB: {int(bool(response['rgb']['r'])) if response['rgb']['r'] is None else response['rgb']['r']} {int(bool(response['rgb']['g'])) if response['rgb']['g'] is None else response['rgb']['g']} {int(bool(response['rgb']['b'])) if response['rgb']['b'] is None else response['rgb']['b']}\n'
                                                                       f'✨CMYK: {int(bool(response['cmyk']['c'])) if response['cmyk']['c'] is None else response['cmyk']['c']} {int(bool(response['cmyk']['m'])) if response['cmyk']['m'] is None else response['cmyk']['m']} {int(bool(response['cmyk']['y'])) if response['cmyk']['y'] is None else response['cmyk']['y']} {int(bool(response['cmyk']['k'])) if response['cmyk']['k'] is None else response['cmyk']['k']}\n'
                                                                       f'✨https://get-color.ru/code/{response['hex']['clean']}'),
                                                      # thumbnail_url=f'https://via.placeholder.com/500x500/{response['hex']['clean']}/{response['hex']['clean']}.jpeg',
                                                      hide_url=True,
                                                      description=f'HEX: {response['hex']['value']}\n'
                                                                  f'RGB: {int(bool(response['rgb']['r'])) if response['rgb']['r'] is None else response['rgb']['r']} {int(bool(response['rgb']['g'])) if response['rgb']['g'] is None else response['rgb']['g']} {int(bool(response['rgb']['b'])) if response['rgb']['b'] is None else response['rgb']['b']}\n'
                                                                  f'CMYK: {int(bool(response['cmyk']['c'])) if response['cmyk']['c'] is None else response['cmyk']['c']} {int(bool(response['cmyk']['m'])) if response['cmyk']['m'] is None else response['cmyk']['m']} {int(bool(response['cmyk']['y'])) if response['cmyk']['y'] is None else response['cmyk']['y']} {int(bool(response['cmyk']['k'])) if response['cmyk']['k'] is None else response['cmyk']['k']}',
                                                  )])

        if scheme[0].lower() == 'cmyk':
            c, m, y, k = scheme[1], scheme[2], scheme[3], scheme[4]
            if 0 <= int(c) <= 100 and 0 <= int(m) <= 100 and 0 <= int(y) <= 100 and 0 <= int(k) <= 100:
                response = requests.get(f'{api_url}cmyk={c},{m},{y},{k}').json()
                pic = requests.get(
                    f'https://via.placeholder.com/500x500/{response['hex']['clean']}/{response['hex']['clean']}.jpeg').content
                await bot.answer_inline_query(query_id,
                                              [InlineQueryResultPhoto(
                                                  type=InlineQueryResultType.PHOTO,
                                                  id=str(int(query_id) + 1),
                                                  photo_url=f'https://via.placeholder.com/500x500/{response['hex']['clean']}/{response['hex']['clean']}.jpeg',
                                                  thumbnail_url=f'https://via.placeholder.com/500x500/{response['hex']['clean']}/{response['hex']['clean']}.jpeg',
                                                  caption=f'✨HEX: {response['hex']['value']}\n'
                                                          f'✨RGB: {int(bool(response['rgb']['r'])) if response['rgb']['r'] is None else response['rgb']['r']} {int(bool(response['rgb']['g'])) if response['rgb']['g'] is None else response['rgb']['g']} {int(bool(response['rgb']['b'])) if response['rgb']['b'] is None else response['rgb']['b']}\n'
                                                          f'✨CMYK: {int(bool(response['cmyk']['c'])) if response['cmyk']['c'] is None else response['cmyk']['c']} {int(bool(response['cmyk']['m'])) if response['cmyk']['m'] is None else response['cmyk']['m']} {int(bool(response['cmyk']['y'])) if response['cmyk']['y'] is None else response['cmyk']['y']} {int(bool(response['cmyk']['k'])) if response['cmyk']['k'] is None else response['cmyk']['k']}\n'
                                                          f'✨https://get-color.ru/code/{response['hex']['clean']}',
                                                  title=f'С фото',
                                                  description=f'HEX: {response['hex']['value']}\n'
                                                              f'RGB: {int(bool(response['rgb']['r'])) if response['rgb']['r'] is None else response['rgb']['r']} {int(bool(response['rgb']['g'])) if response['rgb']['g'] is None else response['rgb']['g']} {int(bool(response['rgb']['b'])) if response['rgb']['b'] is None else response['rgb']['b']}\n'
                                                              f'CMYK: {int(bool(response['cmyk']['c'])) if response['cmyk']['c'] is None else response['cmyk']['c']} {int(bool(response['cmyk']['m'])) if response['cmyk']['m'] is None else response['cmyk']['m']} {int(bool(response['cmyk']['y'])) if response['cmyk']['y'] is None else response['cmyk']['y']} {int(bool(response['cmyk']['k'])) if response['cmyk']['k'] is None else response['cmyk']['k']}'
                                              ),
                                                  InlineQueryResultArticle(
                                                      id=str(int(query_id) + 2),
                                                      type=InlineQueryResultType.ARTICLE,
                                                      title=f'Без фото',
                                                      input_message_content=InputTextMessageContent(
                                                          message_text=f'✨HEX: {response['hex']['value']}\n'
                                                                       f'✨RGB: {int(bool(response['rgb']['r'])) if response['rgb']['r'] is None else response['rgb']['r']} {int(bool(response['rgb']['g'])) if response['rgb']['g'] is None else response['rgb']['g']} {int(bool(response['rgb']['b'])) if response['rgb']['b'] is None else response['rgb']['b']}\n'
                                                                       f'✨CMYK: {int(bool(response['cmyk']['c'])) if response['cmyk']['c'] is None else response['cmyk']['c']} {int(bool(response['cmyk']['m'])) if response['cmyk']['m'] is None else response['cmyk']['m']} {int(bool(response['cmyk']['y'])) if response['cmyk']['y'] is None else response['cmyk']['y']} {int(bool(response['cmyk']['k'])) if response['cmyk']['k'] is None else response['cmyk']['k']}\n'
                                                                       f'✨https://get-color.ru/code/{response['hex']['clean']}'),
                                                      # thumbnail_url=f'https://via.placeholder.com/500x500/{response['hex']['clean']}/{response['hex']['clean']}.jpeg',
                                                      hide_url=True,
                                                      description=f'HEX: {response['hex']['value']}\n'
                                                                  f'RGB: {int(bool(response['rgb']['r'])) if response['rgb']['r'] is None else response['rgb']['r']} {int(bool(response['rgb']['g'])) if response['rgb']['g'] is None else response['rgb']['g']} {int(bool(response['rgb']['b'])) if response['rgb']['b'] is None else response['rgb']['b']}\n'
                                                                  f'CMYK: {int(bool(response['cmyk']['c'])) if response['cmyk']['c'] is None else response['cmyk']['c']} {int(bool(response['cmyk']['m'])) if response['cmyk']['m'] is None else response['cmyk']['m']} {int(bool(response['cmyk']['y'])) if response['cmyk']['y'] is None else response['cmyk']['y']} {int(bool(response['cmyk']['k'])) if response['cmyk']['k'] is None else response['cmyk']['k']}',
                                                  )])

    except IndexError as IndexE:
        pass

    except Exception as e:
        print(e)


@dp.message()
async def send_echo(message: Message):
    await message.reply('Я вас не понимаю😔')


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
