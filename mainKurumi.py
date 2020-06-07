import discord
from discord import Status
from discord.utils import get
from discord.ext import commands

import sys
import asyncio

from random import seed
from random import randint

client = commands.Bot(command_prefix='u&')
seed()

async def randomstatus(client):
    while True:
        x = randint(0,2)

        if x == 0:
            await client.change_presence(status=discord.Status.online, activity=discord.Game("basketball 🏀"))
        elif x == 1:
            await client.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.listening, name="music~~ 🎵"))
        elif x == 2:
            await client.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.watching, name="youtube videos 🎬"))

        await asyncio.sleep(600)

    return

@client.command()
async def reload(ctx, ext=None):
    if ext == None:
        client.reload_extension('osucog')
        client.reload_extension('tictactoecog')
        client.reload_extension('funcog')
    else:
        client.reload_extension(ext)

    await ctx.send("okay~~!")
    return

@client.event
async def on_message(ctx):
    if ctx.author == client.user: # ignore own messages
        return

    if "thanks kurumi" in ctx.content.lower():
        await ctx.channel.send("no problem~~!")

    await client.process_commands(ctx)
    return

@client.event
async def on_ready():
    print("Kurumi Ready")

    # random status every 10 mins
    client.loop.create_task(randomstatus(client=client))

    # load all extensions
    #client.load_extension('smokecog')
    client.osukey = sys.argv[2]
    client.load_extension('osucog')
    client.load_extension('tictactoecog')
    client.load_extension('funcog')

    return

client.run(sys.argv[1])