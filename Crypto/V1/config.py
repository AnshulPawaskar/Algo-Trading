PROJECT_NAME = 'AlgoTrading(CRYPTO) - CEX'

#Redis Credentials
REDIS_PASSWORD = 'GuwoVlGp6I4Mv6zchofyF7fir1lFnlVR'
REDIS_HOSTNAME = 'redis-14995.crce206.ap-south-1-1.ec2.redns.redis-cloud.com'
REDIS_PORT = 14995
REDIS_USERNAME = 'default'

#Telegram Credentials
TELEGRAM_API_TOKEN = '6785107783:AAH9ZTyjiJiK3d3IiX5ZXiLgR7ttWeGXLvE'
TELEGRAM_API_BASE_URL = 'https://api.telegram.org/'
TELEGRAM_API_URL = f'{TELEGRAM_API_BASE_URL}bot{TELEGRAM_API_TOKEN}/sendMessage'
ALERT_GROUP_ID = '-4152124020'
ERROR_GROUP_ID = '-4911895242'

#Market Data Websocket
MARKET_DATA_URL = {
    'BINANCE': {
        "SPOT": {
            "URL": "wss://stream.binance.com:9443/ws/",
            "METHOD": ""
        },
        "UMFUTURES": {
            "URL": "wss://fstream.binance.com/stream?streams=",
            "METHOD": "@markPrice"
        }
    }
}

#User Data Websocket
BINANCE_SPOT_USER = ""
BINANCE_FUTURES_USER = ""
