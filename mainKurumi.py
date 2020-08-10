import discord
from discord import Status
from discord.utils import get
from discord.ext import commands

import sys
import asyncio

import dfunctions

from random import seed
from random import randint

client = commands.Bot(command_prefix='+', help_command=None)
client.remove_command('help')
seed()

commanddict = {
    "Info": [
        ["info"],
        ["help"]
    ],
    "Music": [
        ["play", "p"],
        ["skip", "s"],
        ["stop"]
    ],
    "FaceIt": [
        ["faceituser", "faceit"],
        ["faceitcsgouser", "csgo", "csgouser"],
        ["faceitcsgocompare", "csgocompare"],
        ["faceitcsgolatestmatch", "csgolatestmatch", "csgolatest"]
    ],
    "osu!":[
        ["osuuser", "osuplayer", "osu"],
        ["osubest"],
        ["osurecent"]
    ],
    "Currency Exchanges":[
        ["exchangerates", "rate", "rates", "ex"],
        ["supportedcountries", "supportedrates"]
    ],
    "Misc":[
        ["say"],
        ["hug"],
        ["secks"],
        ["randomkurumi"],
        ["rps"],
        ["eightball"],
        ["coinflip"],
        ["avatar", "av"],
        ["server", "sv"],
        ["userpic", "pfp"]
    ],
}

botstats = {
}

hourssession = 0.0
namefilter = []

async def changefilter(theid):
    global namefilter

    namefilter.append(theid)
    await asyncio.sleep(60)
    namefilter.remove(theid)

    return

async def savebotinfo(client):
    global botstats
    global hourssession

    while True:
        await asyncio.sleep(900) # every 15 mins
        await client.wait_until_ready()

        hourssession = round(hourssession + 0.25, 2)
        botstats["uptime"] = round(botstats["uptime"] + 0.25, 2)
        dfunctions.savejson(botstats, "botstats.json")
        print("saved")

    return

async def randomstatus(client):
    while True:
        x = randint(0,2)

        if x == 0:
            await client.change_presence(status=discord.Status.online, activity=discord.Game("basketball 🏀"))
        elif x == 1:
            await client.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.listening, name="music~~ 🎵"))
        elif x == 2:
            await client.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.watching, name="youtube videos 🎬"))

        print("changed status to {}".format(x))
        await asyncio.sleep(600)

    return

@client.command()
async def reload(ctx, ext=None):
    # so only i can do it
    if ctx.author.id != 208192812108349443:
        await ctx.send("nah")
        return

    if ext == None:
        client.reload_extension('osucog')
        #client.reload_extension('tictactoecog')
        client.reload_extension('funcog')
        client.reload_extension('musiccog')
        client.reload_extension('faceitcog')
        client.reload_extension('exchangescog')
    else:
        client.reload_extension(ext)

    # disconnect from all voice channels
    for vc in client.voice_clients:
        await vc.disconnect()

    await ctx.send("okay~~!")
    return

@client.command()
async def info(ctx):
    global botstats
    global hourssession

    text = ""
    text += "[GitHub Repository](https://github.com/iceCuube/kurumi-discord)"
    text += "\n[Discord Server](https://discord.gg/AH9Xgxq)"
    text += "\n[Add this bot to your server!](https://discord.com/api/oauth2/authorize?client_id=717713621756674048&permissions=70568960&scope=bot)"

    text += "\n\nI am in **{}** servers".format(len(client.guilds))
    text += "\n**{}** people have thanked me ❤️".format(botstats["thanked"])
    text += "\n\nI've been up for **{}** hours in this session\nand **{}** hours since I started counting!".format(hourssession, botstats["uptime"])

    embedinfo = dfunctions.generatesimpleembed("❤️ Kurumi-Chan ❤️", text, colour=discord.Colour.magenta())
    embedinfo.set_thumbnail(url="https://i.ibb.co/Z25Tg7Z/mushroomxpfp.png")
    embedinfo.set_image(url="https://i.ibb.co/SRhN35L/bannerkurumi2.jpg")

    await ctx.send(embed=embedinfo)
    return

@client.command()
async def help(ctx):
    text = ""

    text += "Here are the commands I can do!"
    text += "\n\nCommand Prefix: **+**\n"

    for groupname, itemgroup in commanddict.items():
        text += "\n**{}**".format(groupname)
        text += "\n```yaml"

        for item in itemgroup:
            text += "\n" + item[0]
            if len(item) > 1:
                iterable = iter(item)
                next(iterable)
                for x in iterable:
                    text += "\n    " + x

        text += "\n```"

    embedinfo = dfunctions.generatesimpleembed("❤️ Kurumi-Chan ❤️", text, colour=discord.Colour.magenta())
    embedinfo.set_thumbnail(url="https://i.ibb.co/Z25Tg7Z/mushroomxpfp.png")
    embedinfo.set_image(url="https://i.ibb.co/SRhN35L/bannerkurumi2.jpg")

    try:
        await ctx.author.send(embed=embedinfo)
    except discord.Forbidden:
        await ctx.send(embed=embedinfo)
        return
    except:
        return

    await ctx.send("i just sent u a dm!")
    return

@client.event
async def on_message(ctx):
    global botstats

    if ctx.author == client.user: # ignore own messages
        return

    if ctx.author.bot: # ignore bots
        return

    if "thanks kurumi" in ctx.content.lower():
        if ctx.author.id in namefilter:
            await ctx.channel.send("you have been doing that too fast! please wait a bit")
        else:
            client.loop.create_task(changefilter(ctx.author.id))
            await ctx.channel.send("no problem~~!")
            botstats["thanked"] += 1

    await client.process_commands(ctx)
    return

@client.event
async def on_ready():
    global botstats

    print("Kurumi Ready")

    # random status every 10 mins
    client.loop.create_task(randomstatus(client=client))
    client.loop.create_task(savebotinfo(client=client))

    # get bot stats
    botstats = dfunctions.loadjson("botstats.json")

    # load all extensions
    #client.load_extension('smokecog')
    client.osukey = sys.argv[2]
    client.faceitkey = sys.argv[3]
    client.exchangekey = sys.argv[4]

    client.load_extension('osucog')
    #client.load_extension('tictactoecog')
    client.load_extension('funcog')
    client.load_extension('musiccog')
    client.load_extension('faceitcog')
    client.load_extension('exchangescog')

    # disconnect from all voice channels
    for vc in client.voice_clients:
        await vc.disconnect()

    return

client.run(sys.argv[1])