from os.path import abspath, join, dirname
from sys import path, exc_info

base_dir = abspath(join(dirname(__file__), "./"))
path.append(base_dir)

from aiohttp import ClientSession
from config import TELEGRAM_API_URL, ALERT_GROUP_ID, ERROR_GROUP_ID, PROJECT_NAME

async def send(message, error=True):
    if error:
        chatid = ERROR_GROUP_ID
    else:
        chatid = ALERT_GROUP_ID
    url = TELEGRAM_API_URL
    try:
        async with ClientSession() as session:
            payload = {'chat_id': chatid, 'text': message}
            async with session.post(url, json=payload) as resp:
                if resp.status == 200:
                    return await resp.json()
    except Exception as err:
        pass
