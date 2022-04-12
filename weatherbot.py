import requests
import discord
from discord.ext import commands, pages
from discord.commands import Option
from discord.ui import Button, View
from datetime import datetime
import matplotlib.pyplot as plt
import random
import os


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
        embed = discord.Embed(title="This city cannot be found", color=discord.Color.red())
        await ctx.respond(embed=embed)


@client.slash_command(description="Forecast weather info for a given city ", guild_ids=[869177161012109322])
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


@client.slash_command(description="Global weather maps showing clouds, precipitation, temperature and pressure", guild_ids=[869177161012109322])
async def globalmaps(
    ctx: discord.ApplicationContext,
    type: Option(str, "Either: clouds, precipitation, temperature or pressure")
):
    global API_KEY

    #creating embed pages for each weather map type
    #API request result stored from url and assigned to embed as image.
    cloudurl = f"https://tile.openweathermap.org/map/clouds_new/1/1/1.png?appid={API_KEY}"
    cloudembed = discord.Embed(title="** Clouds  **", color=discord.Color.blue(), timestamp=datetime.utcnow(), url=cloudurl)
    cloudembed.set_image(url=cloudurl)
    cloudembed.set_footer(icon_url=ctx.author.avatar.url, text="Requested by " + ctx.author.name)

    rainurl = f"https://tile.openweathermap.org/map/precipitation_new/1/1/1.png?appid={API_KEY}"
    rainembed = discord.Embed(title="** Precipitation **", color=discord.Color.blue(), timestamp=datetime.utcnow(), url=rainurl)
    rainembed.set_image(url=rainurl)
    rainembed.set_footer(icon_url=ctx.author.avatar.url, text="Requested by " + ctx.author.name)

    tempurl = f"https://tile.openweathermap.org/map/temp_new/1/1/1.png?appid={API_KEY}"
    tempembed = discord.Embed(title="** Temperature **", color=discord.Color.blue(), timestamp=datetime.utcnow(), url=tempurl)
    tempembed.set_image(url=tempurl)
    tempembed.set_footer(icon_url=ctx.author.avatar.url, text="Requested by " + ctx.author.name)

    pressurl = f"https://tile.openweathermap.org/map/pressure_new/1/1/1.png?appid={API_KEY}"
    pressembed = discord.Embed(title="** Pressure **", color=discord.Color.blue(), timestamp=datetime.utcnow(), url=pressurl)
    pressembed.set_image(url=pressurl)
    pressembed.set_footer(icon_url=ctx.author.avatar.url, text="Requested by " + ctx.author.name)

    # creating buttons to switch between pages for each day using Discord Button class
    button2 = Button(label="Clouds", style=discord.ButtonStyle.secondary, emoji="☁")
    button3 = Button(label="Precipitation", style=discord.ButtonStyle.secondary, emoji="🌧")
    button4 = Button(label="Temperature", style=discord.ButtonStyle.secondary, emoji="🌡")
    button5 = Button(label="Pressure", style=discord.ButtonStyle.secondary, emoji="🌫")

    # functions that edit the bot response depending on the button pressed
    async def button2_callback(interaction):
        await interaction.response.edit_message(embed=cloudembed)

    async def button3_callback(interaction):
        await interaction.response.edit_message(embed=rainembed)

    async def button4_callback(interaction):
        await interaction.response.edit_message(embed=tempembed)

    async def button5_callback(interaction):
        await interaction.response.edit_message(embed=pressembed)

    # assigning each function to callback method of Button class - to edit the response with its respective page
    button2.callback = button2_callback
    button3.callback = button3_callback
    button4.callback = button4_callback
    button5.callback = button5_callback

    # View() is a class used to create UI objects for Discord such as buttons
    view = View()
    # iteratively adding buttons to Discord UI object
    buttons = [button2, button3, button4, button5]
    for b in buttons:
        view.add_item(b)

    # sending bot response within Discord passing the first page of map data and UI objects as parameters
    if type == "clouds":
        await ctx.respond(embed=cloudembed, view=view)
    elif type == "precipitation":
        await ctx.respond(embed=rainembed, view=view)
    elif type == "temperature":
        await ctx.respond(embed=rainembed, view=view)
    elif type == "pressure":
        await ctx.respond(embed=pressembed, view=view)
    else:
        embed = discord.Embed(title="Error!", description="This map type isn't available, please try again", color=discord.Color.red())
        await ctx.respond(embed=embed)


@client.slash_command(description="Statistical graphs for temperature, pressure, humidity and precipitation of a given city ", guild_ids=[869177161012109322])
async def graph(
    ctx: discord.ApplicationContext,
    type: Option(str, "Either: temperature, pressure, humidity or precipitation"),
    city: Option(str, "Enter a city/state")
):
    global API_KEY

    url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}"
    res = requests.get(url)
    data = res.json()
    # pprint(data)
    if data["cod"] != "404":

        # order of data item in each list: datetime, temp_max, temp_min, ground level pressure, humidity, probability of precipitation
        firstDay = [data["list"][0]["dt_txt"], data["list"][0]["main"]["temp_max"] - 273.15,
                    data["list"][0]["main"]["temp_min"] - 273.15,
                    data["list"][0]["main"]["grnd_level"], data["list"][0]["main"]["humidity"], data["list"][0]["pop"]]

        secondDay = [data["list"][7]["dt_txt"], data["list"][7]["main"]["temp_max"] - 273.15,
                     data["list"][7]["main"]["temp_min"] - 273.15,
                     data["list"][7]["main"]["grnd_level"], data["list"][7]["main"]["humidity"], data["list"][7]["pop"]]

        thirdDay = [data["list"][14]["dt_txt"], data["list"][14]["main"]["temp_max"] - 273.15,
                    data["list"][14]["main"]["temp_min"] - 273.15,
                    data["list"][14]["main"]["grnd_level"], data["list"][14]["main"]["humidity"],
                    data["list"][14]["pop"]]

        fourthDay = [data["list"][21]["dt_txt"], data["list"][21]["main"]["temp_max"] - 273.15,
                     data["list"][21]["main"]["temp_min"] - 273.15,
                     data["list"][21]["main"]["grnd_level"], data["list"][21]["main"]["humidity"],
                     data["list"][21]["pop"]]

        fifthDay = [data["list"][28]["dt_txt"], data["list"][28]["main"]["temp_max"] - 273.15,
                    data["list"][28]["main"]["temp_min"] - 273.15,
                    data["list"][28]["main"]["grnd_level"], data["list"][28]["main"]["humidity"],
                    data["list"][28]["pop"]]

        # storing date in mm/dd form for next 5 forecasted days
        daysX = [firstDay[0][5:10], secondDay[0][5:10], thirdDay[0][5:10], fourthDay[0][5:10], fifthDay[0][5:10]]

        # calculates mean temperature data for next 5 forecasted days
        def getMeanTempData():
            # stores max temperature and min temperature of each day
            tempData = []
            tempData = [firstDay[1], firstDay[2], secondDay[1], secondDay[2], thirdDay[1], thirdDay[2], fourthDay[1],
                        fourthDay[2], fifthDay[1], fifthDay[2]]


            meanTempData = []
            # calculates mean temperature for each day and stores in list
            for i in range(1, 10, 2):
                meanTempData.append(((tempData[i] + tempData[i - 1]) // 2))


            meanTempDataY = []
            # rounds mean temperature data for each day to 2dp and stores in list
            for meanTemp in meanTempData:
                meanTempDataY.append(round(meanTemp, 2))


            return meanTempDataY

        # calculates mean ground level pressure data for next 5 forecasted days and store in list to 2dp
        def getPressureData():
            pressureDataY = []
            pressureData = []
            pressureData = [firstDay[3], secondDay[3], thirdDay[3], fourthDay[3], fifthDay[3]]
            for pressure in pressureData:
                pressureDataY.append(round(pressure, 2))


            return pressureDataY

        # calculates humidity data for next 5 forecasted days and store in list to 2dp
        def getHumidityData():
            humidityDataY = []
            humidityData = []
            humidityData = [firstDay[4], secondDay[4], thirdDay[4], fourthDay[4], fifthDay[4]]
            # for humidity in humidityData:
            #    humidityDataY.append(round(humidity, 2))
            humidityDataY = humidityData

            return humidityDataY

        # calculates precipitation data for next 5 forecasted days and store in list to 2dp
        def getPrecipitationData():
            precipitationDataY = []
            precipitationData = []
            precipitationData = [firstDay[5], secondDay[5], thirdDay[5], fourthDay[5], fifthDay[5]]
            #for precipitation in precipitationData:
            #    precipitationDataY.append(round(precipitation, 2))
            precipitationDataY = precipitationData

            return precipitationDataY

        # function to generate matplotlib graphs of given weather data
        def genGraphs(days, getData, xlab, ylab, graph_title, image_type):
            plt.plot(days, getData)
            plt.xlabel(xlab)
            plt.ylabel(ylab)
            plt.title(graph_title)

            n = random.randint(1, 1000)   # lets say the function returns the random number 5, therefore n = 5
            # so the path will be C:\path\to\file\temperature-image5.png
            file_path = os.path.abspath(fr"C:\path\to\file\{image_type}-image{n}.png")

            # file is saved to current project directory
            plt.savefig(file_path)
            plt.clf()
            plt.cla()
            plt.close()

            # function returns file location in current project directory
            return file_path


        # a function to construct a base model discord embedded message for each generated graph
        def constructEmbed(embed_title, file_attachment):
            embed = discord.Embed(title=f"**{embed_title} for {city}**", colour=discord.Color.blue(), timestamp=datetime.utcnow())
            embed.set_image(url=f"attachment://{file_attachment}")
            embed.set_footer(icon_url=ctx.author.avatar.url, text="Requested by " + ctx.author.name)

            return embed

        types = ["temperature", "pressure", "humidity", "precipitation"]

        if type == "temperature":
            # constructs mean temperature graph
            file_path = genGraphs(daysX, getMeanTempData(), "Date", "Temperature (°C)", "Forecasted Average Temperature for the next 5 days", "temperature")
            # attachment is the graph file name taken from its file path e.g. "temperature-image457.png"
            attachment = file_path[65:]
            # an object for sending files within discord
            tempGraph = discord.File(file_path)
            await ctx.respond(embed=constructEmbed("Temperature Forecast Graph", attachment), file=tempGraph)

            # deletes file only if it is present in the project directory
            if os.path.exists(file_path):
                os.remove(file_path)

        elif type == "pressure":
            # constructs and sends pressure graph
            file_path = genGraphs(daysX, getPressureData(), "Date", "Pressure (hPa)", "Forecasted Average Pressure for the next 5 days", "pressure")
            attachment = file_path[65:]
            pressGraph = discord.File(file_path)
            await ctx.respond(embed=constructEmbed("Pressure Forecast Graph", attachment), file=pressGraph)

            if os.path.exists(file_path):
                os.remove(file_path)

        elif type == "humidity":
            # constructs and sends percentage of humidity graph
            file_path = genGraphs(daysX, getHumidityData(), "Date", "Humidity (%)", "Forecasted Average Humidity for the next 5 days", "humidity")
            attachment = file_path[65:]
            humidGraph = discord.File(file_path)
            await ctx.respond(embed=constructEmbed("Humidity Forecast Graph", attachment), file=humidGraph)

            if os.path.exists(file_path):
                os.remove(file_path)

        elif type == "precipitation":
            # constructs and sends probability of precipitation graph
            file_path = genGraphs(daysX, getPrecipitationData(), "Date", "Precipitation (%)", "Forecasted Probability of Precipitation for the next 5 days", "precipitation")
            attachment = file_path[65:]
            preciGraph = discord.File(file_path)
            await ctx.respond(embed=constructEmbed("Precipitation Forecast Graph", attachment), file=preciGraph)

            if os.path.exists(file_path):
                os.remove(file_path)

        # error checking for user inputting graph type incorrectly
        elif type not in types:
            embed = discord.Embed(title="Error!", description="Unrecognised type. Please check spelling and/or try again", color=discord.Color.red())
            await ctx.respond(embed=embed)

    # error checking for user inputting city incorrectly
    elif data["cod"] == "404":
        embed = discord.Embed(title="Error!", description="Unrecognised city. Please check spelling and/or try again", color=discord.Color.red())
        await ctx.respond(embed=embed)


@client.slash_command(description="Listed information about each command", guild_ids=[869177161012109322])
async def help(ctx: discord.ApplicationContext):

    embed = discord.Embed(title="**Commands(/)**", color=discord.Color.blue(), timestamp=datetime.utcnow())
    embed.add_field(name="name: weather", value="Current weather data of a given city", inline=False)
    embed.add_field(name="arguments: city", value="A city", inline=False)
    embed.add_field(name="name: forecast", value="Forecast data of a given city", inline=False)
    embed.add_field(name="arguments: city", value="A city", inline=False)
    embed.add_field(name="name: globalmaps", value="Different layers of global weather maps", inline=False)
    embed.add_field(name="arguments: type, city", value="Either clouds, precipitation, temperature or pressure, A city", inline=False)
    embed.add_field(name="name: graph", value="Different statistical 5 day forecast graphs", inline=False)
    embed.add_field(name="arguments: type", value="Either temperature, pressure, humidity and precipitation", inline=False)
    embed.add_field(name="name: help", value="returns this embed page", inline=False)
    embed.add_field(name="arguments:", value="none", inline=False)

    await ctx.respond(embed=embed)


# runs the program on the bot
client.run(TOKEN)
