# v4 update - TOKEN is now stored in external file


import requests
import pprint
from pprint import pprint
import typing
import discord
from discord.ext import commands, tasks
from discord.ext.commands import CommandNotFound, MissingRequiredArgument
from discord.commands import Option
from itertools import cycle
from datetime import datetime
import time
import pytz

# initialising bot
client = commands.Bot()

# Accessing token securely from an external file
t_file = open("TOKEN.txt", "r")
TOKEN = t_file.readline()

# Accessing api key securely from an external file
key_file = open("APIKEY.txt", "r")
API_KEY = key_file.readline()


@client.event
async def on_ready():
    print("Bot is ready")
    change_status.start()

status = cycle(["being overworked...", "enjoying life...", "running errands...",
                "skipping my break...", "barely staying afloat...", "wasting time", "fetching weather data"])


@tasks.loop(seconds=10)
async def change_status():
    await client.change_presence(activity=discord.Game(next(status)))  # displays bot status inside Discord


@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CommandNotFound):
        embed = discord.Embed(title="Error!", description="Command not found.", color=discord.Color.red())
        await ctx.send(embed=embed)
    elif isinstance(error, commands.errors.MissingRequiredArgument):
        embed = discord.Embed(title="Error!", description="Command missing city argument.", color=discord.Color.red())
        await ctx.send(embed=embed)


@client.slash_command(description="Returns current weather data", guild_ids=[869177161012109322])
async def weather(
    ctx: discord.ApplicationContext,
    city: Option(str, "Enter a city/state"),
):
    global API_KEY
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&appid={API_KEY}"
    # making request to API for current weather data about city
    res = requests.get(url)
    # returns json object of requested data
    data = res.json()
    # checking if access to API is working
    if data["cod"] != "404":
        # storing relevant data from json
        data_city = data["name"]
        data_country = data["sys"]["country"]
        temp = data["main"]["temp"]
        temp_int = round(temp)
        temp_max = data["main"]["temp_max"]
        temp_max_int = round(temp_max)
        temp_min = data["main"]["temp_min"]
        temp_min_int = round(temp_min)
        description = data["weather"][0]["description"]
        wind_speed = data["wind"]["speed"]
        wind_speed_int = round(wind_speed)
        icon = data["weather"][0]["icon"]
        # constructing discord message using embed class - formatting for bot response
        embed = discord.Embed(title="**" + data_city + ", " + data_country + "**", color=discord.Color.blue(), timestamp=datetime.utcnow())
        embed.add_field(name="Description", value=description, inline=False)
        embed.add_field(name="Current", value=str(temp_int) + " °C", inline=False)
        embed.add_field(name="Max", value=str(temp_max_int) + " °C", inline=False)
        embed.add_field(name="Min", value=str(temp_min_int) + " °C", inline=False)
        embed.add_field(name="Wind Speed", value=str(wind_speed_int) + " m/s", inline=False)
        icon_url = f"http://openweathermap.org/img/wn/{icon}@2x.png"
        embed.set_thumbnail(url=icon_url)
        embed.set_footer(icon_url=ctx.author.avatar.url, text="Requested by " + ctx.author.name)
        # sending response from user sent command in discord
        await ctx.respond(embed=embed)

    else:
        embed = discord.Embed(title="This city cannot be found", color=discord.Color.red())
        await ctx.respond(embed=embed)
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
# runs the program on the bot        
client.run(TOKEN)
