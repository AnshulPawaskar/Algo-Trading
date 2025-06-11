PROJECT_NAME = 'AlgoTrading(CRYPTO) - CEX'

#MONGODB Credentials
MONGODB_URL = 'mongodb://mongodb10:56cdxPPmM9SM9Lswacdf@mongodb10.odecents.com:27017,mongodb10-rep1.odecents.com:27017,mongodb10-rep2.odecents.com:27017/'
DATABASE_NAME = 'AlgoTrading'

#Telegram Credentials
TELEGRAM_API_TOKEN = '6139489053:AAGtZULsS1WqQhf7tplIMoy1asHt0mMONm0'
TELEGRAM_API_BASE_URL = 'https://api.telegram.org/'
TELEGRAM_API_URL = f'{TELEGRAM_API_BASE_URL}bot{TELEGRAM_API_TOKEN}/sendMessage'
ALERT_GROUP_ID = '-4152124020'
ERROR_GROUP_ID = ''

#Market Data Websocket
MARKET_DATA_URL = {
    'BINANCE': {
        "SPOT": {
            "URL": "",
            "METHOD": ""
        },
        "UMFUTURES": {
            "URL": "",
            "METHOD": ""
        }
    }
}

#User Data Websocket
BINANCE_SPOT_USER = ""
BINANCE_FUTURES_USER = ""
