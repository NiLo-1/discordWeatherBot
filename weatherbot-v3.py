# v3 update - bot now sends rounded values of the weather data

import requests
import pprint
from pprint import pprint
import discord
from discord.ext import commands, tasks
from discord.ext.commands import CommandNotFound, MissingRequiredArgument
from itertools import cycle
from datetime import datetime
import time
import pytz

t_file = open("TOKEN.txt", "r")  # this change is made in this file for Github, AWS copy of this file not updated
TOKEN = t_file.readline()

client = commands.Bot(command_prefix="%")

@client.event
async def on_ready():
    print("Bot is ready")
    change_status.start()

status = cycle(["being overworked...", "enjoying life...", "running errands...",
                "skipping my break...", "barely staying afloat...", "wasting time", "fetching weather data"])

@tasks.loop(seconds=10)
async def change_status():
    await client.change_presence(activity=discord.Game(next(status)))

@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CommandNotFound):
        embed = discord.Embed(title="Error!", description="Command not found.", color=discord.Color.red())
        await ctx.send(embed=embed)
    elif isinstance(error, commands.errors.MissingRequiredArgument):
        embed = discord.Embed(title="Error!", description="Command missing city argument.", color=discord.Color.red())
        await ctx.send(embed=embed)


@client.command()  # discord.py command
async def weather(ctx, *city):
    if len(city) > 1:  # v2 update
        city_str = " ".join(city)
    else:
        city_str = city[0]
    URL = "http://api.openweathermap.org/data/2.5/weather?q={}&units=metric&appid=59b64c89ad5f1a4f3b30761d4554198c".format(city_str)
    res = requests.get(URL)
    data = res.json()
    pprint(data)
    if data["cod"] != "404":
        data_city = data["name"]  # storing relevant data from json file to use in bot response
        data_country = data["sys"]["country"]
        temp = data["main"]["temp"]
        temp_int = round(temp)   # v3 update
        feels_like = data["main"]["feels_like"]
        feels_like_int = round(feels_like)
        temp_max = data["main"]["temp_max"]
        temp_max_int = round(temp_max)
        temp_min = data["main"]["temp_min"]
        temp_min_int = round(temp_min)
        description = data["weather"][0]["description"]
        wind_speed = data["wind"]["speed"]
        icon = data["weather"][0]["icon"]
        embed = discord.Embed(title="**" + data_city + ", " + data_country + "**", color=discord.Color.blue(), timestamp=datetime.utcnow())  # formatting for bot response in discord
        embed.add_field(name="Description", value=description, inline=False)
        embed.add_field(name="Current", value=str(temp_int) + " °C", inline=False)  # v3 update
        embed.add_field(name="Max", value=str(temp_max_int) + " °C", inline=False)
        embed.add_field(name="Min", value=str(temp_min_int) + " °C", inline=False)
        embed.add_field(name="It feels like", value=str(feels_like_int) + " °C", inline=False)
        icon_url = f"http://openweathermap.org/img/wn/{icon}@2x.png"
        embed.set_thumbnail(url=icon_url)
        embed.set_footer(icon_url=ctx.author.avatar_url, text="Requested by " + ctx.author.name)
        await ctx.send(embed=embed)  # sending response from user sent command in discord

    else:
        embed = discord.Embed(title="This city cannot be found", color=discord.Color.red())
        await ctx.send(embed=embed)




















client.run(TOKEN)