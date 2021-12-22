import discord
import os
import requests
import json
from dadjokes import Dadjoke
from pyowm import OWM
from dotenv import load_dotenv
import yfinance as yf

load_dotenv('token.env')

client = discord.Client()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
WEATHER_TOKEN = os.getenv('WEATHER_TOKEN')
owm = OWM(WEATHER_TOKEN)
mgr = owm.weather_manager()

def get_quote():
  response = requests.get('https://zenquotes.io/api/random')
  json_data = json.loads(response.text)
  quote = json_data[0]['q'] + '-' + json_data[0]['a']
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
  
  # Parse for location in message
  location = words[words.index('in') + 1].capitalize()
  if location[-1] == '?': location = location[:-1]

  try:
    observation = mgr.weather_at_place(location)
  except:
    # If we have an invalid location, use Hollywood (real-life Dimmsdale)
    observation = mgr.weather_at_place('Hollywood')

  # Get weather
  w = observation.weather
  weather = w.detailed_status.capitalize()
  weather_dict = w.temperature('fahrenheit')
  temperature = weather_dict.get('temp')

  return {'location': location,
          'temperature': temperature,
          'weather': weather}

def get_stock(message):
  words = message.content.split(' ')
  try:
    # Ticker after the word 'stock'
    stock_ticker = words[words.index('stock') + 1].upper()
    stock = yf.Ticker(stock_ticker)
    
    # Determine if the ticket exists in domestic US market
    stock.info['symbol']
  except:
    stock = yf.Ticker('MSFT')

  # Return dictionary of stock info
  stock_info = stock.info
  return stock_info

@client.event
async def on_ready():
  print('We have logged in as {0.user}'.format(client))
  return

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
    await message.channel.send('Say hi to Your Dad Bot by saying Hi or Hello Dad\nAsk for the weather. (Like "How\'s the weather like in Orlando?"\nAsk me to tell a joke!\nAsk me for quotes!\nStart a sentence with \'I\'m\'\nAsk me about stocks Like "How\'s stock AAPL doing?"')
    return

  # tells a random quote
  if 'quote' in message.content and 'dad' in message.content:
    quote = get_quote()
    await message.channel.send(quote)
    return

  if 'stock' in message.content:
    stock_dict = get_stock(message)
    await message.channel.send('Looks like {0} is trading for ${1:.2f}.'.format(stock_dict['symbol'], stock_dict['regularMarketOpen']))
    return
  
  if ('thanks' in message.content or 'thank you' in message.content) and 'dad' in message.content:
    await message.channel.send('You\'re welcome, Timmy, even if you\'re not my Timmy.')

client.run(DISCORD_TOKEN)