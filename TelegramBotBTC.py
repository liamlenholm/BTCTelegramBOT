import asyncio
from distutils.log import info
from posixpath import split
from queue import Empty
from warnings import catch_warnings
import requests
import json
import pprint
import telebot
import config
import aiohttp
import re
from telebot.async_telebot import AsyncTeleBot

# REPLACE API_TOKEN WITH YOUR TELEGRAM API TOKEN
# You can get one by adding @BotFather on Telegram and typing /start
API_TOKEN = config.TELEGRAM_APIKEY
bot = AsyncTeleBot(API_TOKEN)

# VARIBLES
CONVERT_CURRENCY = ""
CONVERT_AMOUNT = ""

# APIS
FEE_URL = "https://bitcoinfees.earn.com/api/v1/fees/recommended"



PRICE_URL = "https://blockchain.info/ticker"

CONVERT_URL = "https://blockchain.info/tobtc?currency=" + CONVERT_CURRENCY + "&value=" + CONVERT_AMOUNT

FEE_RESPONSE = requests.get(FEE_URL)
PRICE_RESPONSE = requests.get(PRICE_URL)
CONVERT_RESPONSE = requests.get(CONVERT_URL)

FEE_DATA = json.loads(FEE_RESPONSE.text)
PRICE_DATA = json.loads(PRICE_RESPONSE.text)


def extract_arg(arg):
    return arg.split()[1:]


        
def infoMessage():
    infoText = """
    Telegram BTC Fee bot. 

You can control me by sending these commands:

/btc - Shows the current fees for fast transaction.

/price *** - Shows the current price per Bitcoin. Replace *** with desiered currency for exampel /price USD you can use the command:

/currencylist - To see all avaible currencies.

/convert2btc AMOUNT CURRENCY - Convert BTC AMOUNT to CURRENCY. For exampel /convert2btc 0.5 USD

/btc2usd AMOUNT - Converts BTCAMOUNT to USD.

"""
    return infoText

def defaultPrice():
    return(PRICE_DATA["USD"]["last"])


defaultPrice()

def getCurrentPrice(isAvailableinJson):
    # If currency is in avaible list then return current price
    if isAvailableinJson is not None:
        return(str(PRICE_DATA[isAvailableinJson]["last"]) +
               " " + str((PRICE_DATA[isAvailableinJson]["symbol"])))

    # If the currency is not avaible then return currencylist
    elif isAvailableinJson is None:
        return("Currency not available please use /currencylist to see all the available currencies")

# Check if the currency is available or not


def find_by_word(findWord):
    for obj in PRICE_DATA:
        if findWord in obj:
            return obj


def getCurrentFees():
    for key, value in FEE_DATA.items():
        fastestFee = ("The lowest fee that will currently result in the fastest transaction confirmations (usually 0 to 1 block delay)." + "\n" + str(value) + " Satoish per byte \n")
        halfHourFee = ("The lowest fee that will confirm transactions within half an hour (with 90% probability)." + "\n" + str(value) + " Satoish per byte \n")
        hourFee = ("The lowest fee that will confirm transactions within an hour (with 90% probability)." + "\n" + str(value) + " Satoish per byte \n")

        return(fastestFee + "\n" + halfHourFee + "\n" + hourFee)


def availableCurrencies():
    allCurrencies = []
    for keys in PRICE_DATA.items():
        allCurrencies.append(keys[0])

    return "\n".join(allCurrencies)




def convert(amount, currency):
    CONVERT_URL = "https://blockchain.info/tobtc?currency=" + currency + "&value=" + amount
    CONVERT_RESPONSE = requests.get(CONVERT_URL)
    print(CONVERT_RESPONSE)
    print(CONVERT_RESPONSE.text)
    return (CONVERT_RESPONSE.text)

# availableCurrencies()

# TELEGRAM BOT COMMANDS

@ bot.message_handler(commands=['start', 'Start', "help", "Help", "info", "Info"])
async def start(message):
    await bot.reply_to(message, infoMessage())

@ bot.message_handler(commands=['BTC', 'btc'])
async def btcFees(message):
    await bot.reply_to(message, getCurrentFees())

@ bot.message_handler(commands=['Currencylist', 'currencylist'])
async def currencyList(message):
    await bot.reply_to(message, availableCurrencies())


@ bot.message_handler(commands=['price', 'Price'])
async def currentPrice(message):
    currency_input = extract_arg(message.text)
    # It returns as a list so we use [0] to get the text only.
    # For example now it will return USD instead of ['USD']
    # We also convert it to a string so that it can be used in as an arg in the function
    choosenCurrency = str(currency_input[0])
    choosenCurrency = choosenCurrency.upper()

    isAvailableinJson = find_by_word(choosenCurrency)
    await bot.reply_to(message, getCurrentPrice(isAvailableinJson))

@ bot.message_handler(commands=['convert2btc', 'Convert2BTC'])
async def convertBTC(message):
    #Splitting the string to make a list so we can use [1] for the amount and [2] for the currency
    splitted = message.text.split()
    splitted_Amount = splitted[1]
    splitted_Currency = splitted[2]
    await bot.reply_to(message, convert(splitted_Amount, splitted_Currency))

@ bot.message_handler(commands=['btc2usd', 'btc2usd'])
async def convertFIAT(message):
    #Splitting the string to make a list so we can use [1] for the amount and [2] for the currency
    splitted = message.text.split()
    splitted_BTCAmount = splitted[1]
    

    #Get current price for 1 BTC in USD and mulitply that by user input
    def btc2usd():
        btcPrice = PRICE_DATA["USD"]["last"]
        return(float(splitted_BTCAmount) * float(btcPrice))


    await bot.reply_to(message, "$ " + str(btc2usd()))

    


asyncio.run(bot.polling())
