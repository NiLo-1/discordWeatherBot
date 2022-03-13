
import requests
import pprint
from pprint import pprint
import discord
from discord.ext import commands, pages
from discord.commands import Option
from datetime import datetime


# initialising bot with a custom status
client = commands.Bot(activity=discord.Activity(type=discord.ActivityType.watching, name="the sky"))

# accessing token securely from an external file
t_file = open("TOKEN.txt", "r")
TOKEN = t_file.readline()

# accessing api key securely from an external file
key_file = open("APIKEY.txt", "r")
API_KEY = key_file.readline()

# sends a message when bot is connected to Discord
@client.event
async def on_ready():
    print("Bot is ready")


# handles invalid user inputs
@client.event
async def on_command_error(ctx, error):
    # returns error message when user sends an unrecognised command
    if isinstance(error, commands.errors.CommandNotFound):
        embed = discord.Embed(title="Error!", description="Command not found.", color=discord.Color.red())
        await ctx.send(embed=embed)
    # returns error message when user sends a command with missing arguments
    elif isinstance(error, commands.errors.MissingRequiredArgument):
        embed = discord.Embed(title="Error!", description="Command missing city argument.", color=discord.Color.red())
        await ctx.send(embed=embed)



# current weather command
# adds slash command to bot's internal command list
@client.slash_command(description="Returns current weather info for a given city", guild_ids=[869177161012109322])
async def weather(
    # allows use of context data of the message
    ctx: discord.ApplicationContext,
    # declares an argument and states info about the slash command
    city: Option(str, "Enter a city/state"),
):
    global API_KEY
    # making request to API for current weather data about city
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&appid={API_KEY}"
    # returns json object of requested data
    res = requests.get(url)
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
        #
        embed = discord.Embed(title="This city cannot be found", color=discord.Color.red())
        await ctx.respond(embed=embed)


@client.slash_command(description="Returns forecast weather info for a given city ", guild_ids=[869177161012109322])
async def forecast(
    ctx: discord.ApplicationContext,
    city: Option(str, "Enter a city/state"),
):
    global API_KEY
    url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}"
    res = requests.get(url)
    data = res.json()
    if data["cod"] != "404":
        # storing relevant forecast data from each day
        country = data["city"]["country"]
        city = data["city"]["name"]

        # order of data item in each list: datetime, temp_max, temp_min, description, weather icon
        firstDay = [data["list"][0]["dt_txt"], data["list"][0]["main"]["temp_max"] - 273.15,
                    data["list"][0]["main"]["temp_min"] - 273.15,
                    data["list"][0]["weather"][0]["description"], data["list"][0]["weather"][0]["icon"]]
        firstDayDate = firstDay[0][:10]

        secondDay = [data["list"][7]["dt_txt"], data["list"][7]["main"]["temp_max"] - 273.15,
                     data["list"][7]["main"]["temp_min"] - 273.15,
                     data["list"][7]["weather"][0]["description"], data["list"][7]["weather"][0]["icon"]]
        secondDayDate = secondDay[0][:10]


        thirdDay = [data["list"][14]["dt_txt"], data["list"][14]["main"]["temp_max"] - 273.15,
                    data["list"][14]["main"]["temp_min"] - 273.15,
                    data["list"][14]["weather"][0]["description"], data["list"][14]["weather"][0]["icon"]]
        thirdDayDate = thirdDay[0][:10]

        fourthDay = [data["list"][21]["dt_txt"], data["list"][21]["main"]["temp_max"] - 273.15,
                     data["list"][21]["main"]["temp_min"] - 273.15,
                     data["list"][21]["weather"][0]["description"], data["list"][21]["weather"][0]["icon"]]
        fourthDayDate = fourthDay[0][:10]

        fifthDay = [data["list"][28]["dt_txt"], data["list"][28]["main"]["temp_max"] - 273.15,
                    data["list"][28]["main"]["temp_min"] - 273.15,
                    data["list"][28]["weather"][0]["description"], data["list"][28]["weather"][0]["icon"]]
        fifthDayDate = fifthDay[0][:10]

        # constructing discord embed messages to act as a page showing weather forecast for each day
        page1 = discord.Embed(title="**" + city + ", " + country + "**", color=discord.Color.blue(), timestamp=datetime.utcnow())
        page1.add_field(name=firstDayDate, value="--------------", inline=False)
        page1.add_field(name="Description", value=str(firstDay[3]), inline=False)
        page1.add_field(name="Max", value=str(int(firstDay[1])) + " °C", inline=False)
        page1.add_field(name="Min", value=str(int(firstDay[2])) + " °C", inline=False)
        icon_url = f"http://openweathermap.org/img/wn/{str(firstDay[4])}@2x.png"
        page1.set_thumbnail(url=icon_url)
        page1.set_footer(icon_url=ctx.author.avatar.url, text="Requested by " + ctx.author.name)

        page2 = discord.Embed(title="**" + city + ", " + country + "**", color=discord.Color.blue(), timestamp=datetime.utcnow())
        page2.add_field(name=secondDayDate, value="--------------", inline=False)
        page2.add_field(name="Description", value=str(secondDay[3]), inline=False)
        page2.add_field(name="Max", value=str(int(secondDay[1])) + " °C", inline=False)
        page2.add_field(name="Min", value=str(int(secondDay[2])) + " °C", inline=False)
        icon_url = f"http://openweathermap.org/img/wn/{str(secondDay[4])}@2x.png"
        page2.set_thumbnail(url=icon_url)
        page2.set_footer(icon_url=ctx.author.avatar.url, text="Requested by " + ctx.author.name)

        page3 = discord.Embed(title="**" + city + ", " + country + "**", color=discord.Color.blue(), timestamp=datetime.utcnow())
        page3.add_field(name=thirdDayDate, value="--------------", inline=False)
        page3.add_field(name="Description", value=str(thirdDay[3]), inline=False)
        page3.add_field(name="Max", value=str(int(thirdDay[1])) + " °C", inline=False)
        page3.add_field(name="Min", value=str(int(thirdDay[2])) + " °C", inline=False)
        icon_url = f"http://openweathermap.org/img/wn/{str(thirdDay[4])}@2x.png"
        page3.set_thumbnail(url=icon_url)
        page3.set_footer(icon_url=ctx.author.avatar.url, text="Requested by " + ctx.author.name)

        page4 = discord.Embed(title="**" + city + ", " + country + "**", color=discord.Color.blue(), timestamp=datetime.utcnow())
        page4.add_field(name=fourthDayDate, value="--------------", inline=False)
        page4.add_field(name="Description", value=str(fourthDay[3]), inline=False)
        page4.add_field(name="Max", value=str(int(fourthDay[1])) + " °C", inline=False)
        page4.add_field(name="Min", value=str(int(fourthDay[2])) + " °C", inline=False)
        icon_url = f"http://openweathermap.org/img/wn/{str(fourthDay[4])}@2x.png"
        page4.set_thumbnail(url=icon_url)
        page4.set_footer(icon_url=ctx.author.avatar.url, text="Requested by " + ctx.author.name)

        page5 = discord.Embed(title="**" + city + ", " + country + "**", color=discord.Color.blue(), timestamp=datetime.utcnow())
        page5.add_field(name=fifthDayDate, value="--------------", inline=False)
        page5.add_field(name="Description", value=str(fifthDay[3]), inline=False)
        page5.add_field(name="Max", value=str(int(fifthDay[1])) + " °C", inline=False)
        page5.add_field(name="Min", value=str(int(fifthDay[2])) + " °C", inline=False)
        icon_url = f"http://openweathermap.org/img/wn/{str(fifthDay[4])}@2x.png"
        page5.set_thumbnail(url=icon_url)
        page5.set_footer(icon_url=ctx.author.avatar.url, text="Requested by " + ctx.author.name)

        # creating a list of pages for paginator to cycle through
        allpages = [page1, page2, page3, page4, page5]

        # using paginator class to create a message with buttons to navigate through pages
        paginator = pages.Paginator(allpages, use_default_buttons=True, timeout=180.0)
        await paginator.respond(ctx.interaction)

    else:
        embed = discord.Embed(title="Error!", description="Unrecognised argument/s.", color=discord.Color.red())
        await ctx.respond(embed=embed)
                          
                          
                          
                          
                          
                          
                          
                          
                          
                          
 # runs the program on the bot
client.run(TOKEN)
