# A Discord bot that does typical dad things
# By Jason Saini and James Nguyen
# Created: January 31, 2021
# Modified: January 20, 2022

import discord
from os import getenv
from requests import get, Session
from dadjokes import Dadjoke
from pyowm import OWM
from dotenv import load_dotenv
import yfinance as yf

# setup client and tokens
load_dotenv('token.env')

client = discord.Client()
DISCORD_TOKEN = getenv('DISCORD_TOKEN')
WEATHER_TOKEN = getenv('WEATHER_TOKEN')
COIN_TOKEN = getenv('COIN_TOKEN')
OWNER_ID = getenv('OWNER_ID')
owm = OWM(WEATHER_TOKEN)
mgr = owm.weather_manager()
cmc = Session()
cmc.headers.update({'Accepts': 'application/json', 'X-CMC_PRO_API_KEY': COIN_TOKEN})
cmc_url = 'https://pro-api.coinmarketcap.com'

def get_quote():
  response = get('https://zenquotes.io/api/random')
  json_data = response.json()
  quote = 'You know, ' + json_data[0]['a'] + ' said "' + json_data[0]['q'] + '" I think that\'ll help.'

  return quote

def get_i_am_joke(message):
  words = message.content.split(' ')

  try:
    if 'i\'m' in message.content:
      while (words[0] != 'i\'m'): words.pop(0)
      words.pop(0)
    else:
      while (words[0] != 'i' and words[1] != 'am'): words.pop(0)
      words.pop(0)
      words.pop(0)
  except:
    words = message.author.name

  joke = ' '.join(words)
  return joke

def get_weather(message):
  location = ''
  words = message.content.split(' ')

  try:
    # parse for location in message
    location = words[words.index('in') + 1].capitalize()
    if location[-1] == '?': location = location[:-1]
    observation = mgr.weather_at_place(location)
  except:
    # if we have an invalid location, use Hollywood (real-life Dimmsdale)
    print('Invalid location : ' + location)
    observation = mgr.weather_at_place('Hollywood')

  # get weather
  w = observation.weather
  weather = w.detailed_status.capitalize()
  weather_dict = w.temperature('fahrenheit')
  temperature = weather_dict.get('temp')

  # return weather as dict
  return {'location': location,
    'temperature': temperature,
    'weather': weather}

def get_stock(message):
  words = message.content.split(' ')
  try:
    # ticker after the word 'stock'
    stock_ticker = words[words.index('stock') + 1].upper()
    stock = yf.Ticker(stock_ticker)
    
    # determine if the ticket exists in domestic US market
    stock.info['symbol']
  except:
    print('Invalid stock : ' + stock_ticker)
    stock = yf.Ticker('MSFT')

  # return dict of stock info
  return stock.info

def get_crypto(message):
  words = message.content.split(' ')
  try:
    crypto_symbol = words[words.index('crypto') + 1].upper()
  except:
    print('Invalid crypto :')
    [print(word) for word in words]
    crypto_symbol = 'BTC'
  
  response = cmc.get('https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest', params={'symbol': crypto_symbol})
  crypto_price = response.json()['data'][crypto_symbol]['quote']['USD']['price']
  return {'symbol': crypto_symbol,
    'price': crypto_price}


@client.event
async def on_ready():
  print('We have logged in as {0.user}!'.format(client))
  return

async def shutdown(self,ctx):
  if ctx.message.author.id == OWNER_ID: #replace OWNERID with your user id
    print("shutdown")
    try:
      await self.bot.logout()
    except:
      print("EnvironmentError")
      self.bot.clear()
  else:
    await ctx.send("You do not own this bot!")

@client.event
async def on_message(message):
  if message.author == client.user:
    return
  
  message.content = message.content.lower()

  #greets user
  if (message.content.startswith('hello') or message.content.startswith('hi')) and 'dad' in message.content:
    await message.channel.send('Hi, Timmy! Oh you\'re not my Timmy, sorry there, friend!')
    return
  
  #tells a random dad joke
  if 'joke' in message.content and 'dad' in message.content:
    dadjoke = Dadjoke()
    await message.channel.send(dadjoke.joke)
    return

  # tells 'hi [], i'm dad' joke
  if 'i\'m' in message.content or 'i am' in message.content:
    joke = get_i_am_joke(message)
    await message.channel.send(f'Hi, {joke.capitalize()}! I\'m Dad Bot!')
    return
  
  # tells weather
  if 'weather' in message.content:
    weather_dict = get_weather(message)
    await message.channel.send('In {0}, the weather\'s {1} and it\'s {2}\xb0F today!'.format(weather_dict['location'], weather_dict['weather'].lower(), weather_dict['temperature']))
    return

  # sends help information to user
  if 'help' in message.content:
    await message.channel.send('Say hi to Your Dad Bot by saying Hi or Hello Dad\n'
    'Ask for the weather. (Like \"How\'s the weather like in Orlando?\"\n'
    'Ask me to tell a joke!\n'
    'Ask me for quotes!\n'
    'Start a sentence with \'I\'m\'\n'
    'Ask me about stocks Like \"How\'s stock AAPL doing?\"')
    return

  # tells a random quote
  if 'quote' in message.content and 'dad' in message.content:
    quote = get_quote()
    await message.channel.send(quote)
    return

  # tells stock trading price
  if 'stock' in message.content:
    stock_dict = get_stock(message)
    await message.channel.send('Looks like {0} is trading for ${1:.2f}.'.format(stock_dict['symbol'], stock_dict['regularMarketOpen']))
    return

  # tells crypto trading price
  if 'crypto' in message.content:
    crypto_dict = get_crypto(message)
    await message.channel.send('Looks like {0} is trading for ${1:.6f}.'.format(crypto_dict['symbol'], crypto_dict['price']))
    return
  
  if ('thanks' in message.content or 'thank you' in message.content) and 'dad' in message.content:
    await message.channel.send('You\'re welcome, Timmy, even if you\'re not my Timmy.')
    return

  else:
    return

client.run(DISCORD_TOKEN)