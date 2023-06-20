from aiogram import types, executor, Dispatcher, Bot
import yfinance as yf
import seaborn as sns
import matplotlib.pyplot as plt
import requests
from datetime import datetime

BOT_TOKEN = "YOUR_TOKEN"
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

currencies = ['BTC', 'ETH', 'USDT', 'XRP', 'DOGE']

for currency in currencies:
    ticker = yf.Ticker(f"{currency}-USD")
    data = ticker.history(period="1mo")
    plt.figure(figsize=(12, 4))
    sns.lineplot(data=data[['High', 'Low']])
    plt.title(f"{currency}-USD")
    plt.savefig(f'{currency.lower()}_usd.png')


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await bot.send_message(message.chat.id,
                           "Nice to meet you! All commands from this bot are here:\n\n"
                           "/price - find out the prices of currencies\n\n"
                           "/help - all commands")


@dp.message_handler(commands=['help'])
async def help_message(message: types.Message):
    await bot.send_message(message.chat.id,
                           "/price - find out the prices of currencies\n\n"
                           "/help - all commands")


@dp.message_handler(commands=['price'])
async def price_menu(message):
    markup = types.InlineKeyboardMarkup(row_width=1)
    for cur in currencies:
        item = types.InlineKeyboardButton(cur, callback_data=cur.lower())
        markup.add(item)
    await bot.send_message(message.chat.id, "Choose the currency to find out its cost", reply_markup=markup)


@dp.callback_query_handler(lambda callback_query: True)
async def callback(call):
    if call.message:
        try:
            request = f"https://yobit.net/api/3/ticker/{call.data}_usd"
            req = requests.get(request)
            response = req.json()
            sell_price = response[f"{call.data}_usd"]["sell"]
            await bot.send_message(call.message.chat.id,
                                   f"{datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
                                   f"Sell {call.data.upper()} price: {sell_price}")
            photo = open(f'{call.data}_usd.png', 'rb')
            await bot.send_photo(call.message.chat.id, photo)
        except Exception as ex:
            print(ex)
            await bot.send_message(call.message.chat.id, "Oops! Something went wrong")
    else:
        await bot.send_message(call.message.chat.id, "Oops! Something went wrong")


@dp.message_handler(content_types=['text'])
async def text(message: types.Message):
    await bot.send_message(message.chat.id, "Oops! Something went wrong")


if __name__ == "__main__":
    executor.start_polling(dp)
