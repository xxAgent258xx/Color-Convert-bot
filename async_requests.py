"""
До этого ты использовал синхронный requests, что негативно сказывалось на производительности бота
Я заменил это на aiohttp который позволяет делать запросы в асинк
"""

import logging
import aiohttp
from aiohttp.web_exceptions import HTTPError

api_url = 'https://www.thecolorapi.com/id?'
ans_url = 'https://whatcolor.ru/color/'
ans_pic = 'https://via.placeholder.com/500x500/'


async def get_by(url: str) -> dict:
    """
    Используйте в функциях начинающихся с get_by_...
    Вернет результат запроса на какой-то сервер куда раптор отправляет запросы
    :param url: url запроса
    :return: json
    :raise: HTTPError
    """

    try:
        # Собственно сам запрос
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                return await response.json()

    except HTTPError as e:  # см. документацию HTTPError
        logging.error(f"http request error: {e.text}")
        raise

async def get_by_hex(hex_) -> dict:
    """
    Конвертировать цвета по хексу
    :param hex_: hex цвета
    :return: json response
    """
    return await get_by(f'{api_url}hex={hex_}')


async def get_by_rgb(r, g, b) -> dict:
    """
    Конвертировать цвета по ргб
    :param r: r
    :param g: g
    :param b: b
    :return: resp
    """

    return await get_by(f'{api_url}rgb=rgb({r},{g},{b})')


async def get_by_cmyk(c, m, y, k) -> dict:
    """
    Конвертировать цвета из cmyk
    :param c: c
    :param m: m
    :param y: y
    :param k: k
    :return: resp
    """

    return await get_by(f'{api_url}cmyk={c},{m},{y},{k}')


async def get_photo_by_hex(hex_) -> bytes:
    """
    Получить байты картинки по хексу
    :param hex_: хекс по которому нужно что-то получить
    :return: байты картинки
    """

    async with aiohttp.ClientSession() as session:
        async with session.get(f'{ans_pic}{hex_}/{hex_}.png') as response:
            return await response.content.read()
