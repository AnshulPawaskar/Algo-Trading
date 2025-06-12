from os.path import abspath, join, dirname
from sys import path, exc_info

base_dir = abspath(join(dirname(__file__), "../"))
path.append(base_dir)

from telegram import send
from config import PROJECT_NAME, REDIS_PASSWORD, REDIS_HOSTNAME, REDIS_PORT, REDIS_USERNAME
from redis.asyncio import Redis

async def redis_connection():
    try:
        r = Redis(host=REDIS_HOSTNAME, 
                  port=REDIS_PORT, 
                  username=REDIS_USERNAME,
                  password=REDIS_PASSWORD,
                  decode_responses=True,)
        return r
    except Exception as err:
        exc_type, exc_obj, exc_tb = exc_info()
        await send(f'ERROR!\nProject: {PROJECT_NAME}\nFile: redis_con.py\nFunction: redis_connection()\nType: {exc_type.__name__}\nLine: {exc_tb.tb_lineno}\nError: {err}')
        raise Exception('Failed to connect to Redis')

async def publish_to_redis(r, channel, message):
    try:
        await r.publish(channel, message)  
    except Exception as err:    
        exc_type, exc_obj, exc_tb = exc_info()
        await send(f'ERROR!\nProject: {PROJECT_NAME}\nFile: redis_con.py\nFunction: publish_to_redis()\nType: {exc_type.__name__}\nLine: {exc_tb.tb_lineno}\nError: {err}')
        raise Exception('Failed to publish message to Redis')

async def subcribe_to_redis(r, channel):
    try:
        pubsub = r.pubsub()
        await pubsub.subscribe(channel)
        return pubsub
    except Exception as err:
        exc_type, exc_obj, exc_tb = exc_info()
        await send(f'ERROR!\nProject: {PROJECT_NAME}\nFile: redis_con.py\nFunction: subcribe_to_redis()\nType: {exc_type.__name__}\nLine: {exc_tb.tb_lineno}\nError: {err}')
        raise Exception('Failed to subscribe to Redis')

async def get_message(pubsub):
    try:
        message = await pubsub.get_message()
        return message  
    except Exception as err:
        exc_type, exc_obj, exc_tb = exc_info()
        await send(f'ERROR!\nProject: {PROJECT_NAME}\nFile: redis_con.py\nFunction: get_message()\nType: {exc_type.__name__}\nLine: {exc_tb.tb_lineno}\nError: {err}')
        raise Exception('Failed to get message from Redis')

