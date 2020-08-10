import discord
from discord.ext import commands

import requests
import json
import time
import datetime
import re

import dfunctions

class exchanges(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.baseurl = "https://prime.exchangerate-api.com/v5/{}/latest/USD".format(self.client.exchangekey)

        self.setexchangeauthor = lambda x: x.set_author(name="Currency Conversion")
        self.moneygold = int("0xFFE014", 16)
        self.getfloats = lambda x: re.findall(r"[-+]?\d*\.\d+|\d+", x)
        return

    @commands.command(aliases=["supportedrates"])
    async def supportedcountries(self, ctx):
        data = dfunctions.loadjson("rates.json")

        if data == None or data["time_next_update"] < time.time(): # request for new data
            print("requesting for new rates")

            response = requests.get(self.baseurl)

            if response.status_code != 200:
                print("error requesting rates{}".format(response.status_code))
                return

            data = response.json()

            dfunctions.savejson(data, "rates.json")

        text = "here are all supported countries\n```\n"
        l = sorted(data["conversion_rates"].keys())

        for i in range(len(l)):
            text += l[i] + " "
            if i % 5 == 4:
                text += "\n"

        text += "```"

        await ctx.send(text)
        return

    @commands.command(aliases=["exchange", "rate", "rates", "ex"])
    async def exhangerates(self, ctx, country1=None, country2=None, valuelist: commands.Greedy[float] = None):
        if country1 == None or country2 == None:
            await ctx.send("you need to specify the country!")
            return

        country1 = country1.upper()
        country2 = country2.upper()

        data = dfunctions.loadjson("rates.json")

        if data == None or data["time_next_update"] < time.time(): # request for new data
            print("requesting for new rates")

            response = requests.get(self.baseurl)

            if response.status_code != 200:
                print("error requesting rates{}".format(response.status_code))
                return

            data = response.json()

            if data["result"] != "success":
                await ctx.send("an error occurred gettin results from the api server!")
                return

            dfunctions.savejson(data, "rates.json")

        if valuelist == None:
            messagehistory = await ctx.channel.history(limit=10).flatten()
            valuelist = None

            for message in messagehistory:
                valuelist = self.getfloats(message.content)
                if len(valuelist) > 0:
                    break
            else:
                await ctx.send("i couldnt find any values from the last 10 messages!")
                return

        if country1 not in data["conversion_rates"] or country2 not in data["conversion_rates"]:
            await ctx.send("that country does not exist!")
            return

        updatedate = datetime.datetime.fromtimestamp(data["time_last_update"]).strftime("%Y-%m-%d %H:%M:%S")
        nextupdate = datetime.timedelta(seconds=data["time_next_update"]-int(time.time()))

        text = "`{} {} = 1 USD`".format(data["conversion_rates"][country1], country1)
        text += "\n`1 USD = {} {}`\n".format(data["conversion_rates"][country2], country2)

        title = "{} to {}".format(country1, country2)
        for value in valuelist:
            converted = round(float(value) / data["conversion_rates"][country1] * data["conversion_rates"][country2], 5)
            text += "\n`{} {} ≈ {} {}`".format(value, country1, converted, country2)

        text += "\n\nLast Updated: **UTC {}**\nNext Update In **{}**\n".format(updatedate, str(nextupdate))

        embedinfo = dfunctions.generatesimpleembed(title, text, colour=discord.Colour(self.moneygold))
        self.setexchangeauthor(embedinfo)
        embedinfo.set_footer(text="i cant guarantee these values are accurate >.<\nPowered By exchangerate-api.com")

        await ctx.send(embed=embedinfo)
        return

def setup(client):
    client.add_cog(exchanges(client))