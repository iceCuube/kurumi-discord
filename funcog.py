import discord
from discord.ext import commands
from discord.utils import get
import random
import asyncio

import dfunctions

eightballresponse = [
    "Ask again later",
    "Concentrate and ask again",
    "Reply hazy, try again later",
    "Can't predict now",
    "It is quite possible",
    "It is decidedly so",
    "It is certain",
    "Without a doubt",
    "You may rely on it",
    "Don't count on it",
    "Most likely not",
    "Likely not",
    "My reply is no"
]

kurumilinks = [
    "https://i.ibb.co/S67FnGT/menhera6x4.png",
    "https://i.ibb.co/rcmRFfr/menhera4x4.png",
    "https://i.ibb.co/0DB15SK/okx4.png",
    "https://i.ibb.co/LgzfYyV/nicex4.png",
    "https://i.ibb.co/7RcSzJJ/sitx4.png",
    "https://i.ibb.co/93x5k6g/glassx4.png",
    "https://i.ibb.co/3mW3dTJ/menhera2x4.png",
    "https://i.ibb.co/B4pDHVD/f.png",
    "https://i.ibb.co/JRwfML9/dabx4.png",
    "https://i.ibb.co/GknHr4p/waterx4.png",
    "https://i.ibb.co/TqHG76x/cringex4.png",
    "https://i.ibb.co/3p9t8n6/prayx4.png",
    "https://i.ibb.co/9vD9zdY/headphonesx4.png",
    "https://i.ibb.co/3MhXnbh/dogx4.png",
    "https://i.ibb.co/yYWNy8X/angelx4.png",
    "https://i.ibb.co/ypTqGVr/dogangryx4.png",
    "https://i.ibb.co/N1hG8s7/wavex4.png",
    "https://i.ibb.co/kS83mz1/flickx4.png",
    "https://i.ibb.co/c6Qqrd7/potatox4.png",
    "https://i.ibb.co/9N0sYnX/lightx4.png",
    "https://i.ibb.co/ZzbxtVs/cry2x4.png",
    "https://i.ibb.co/dDD4Kgk/hatx4.png",
    "https://i.ibb.co/dJsrr1L/bedx4.png",
    "https://i.ibb.co/yFfpf6h/menhera3x4.png",
]

rpsdict = {
    "rock": ["scissors", "🗿"],
    "scissors": ["paper", "✂️"],
    "paper": ["rock", "🧻"]
}

async def slapfunc(member, slaprole):
    await asyncio.sleep(10)
    await member.remove_roles(slaprole)

    return

class fun(commands.Cog):
    def __init__(self,client):
        self.client = client
        return

    @commands.command()
    async def say(self, ctx, *, text):
        await ctx.send(text)
        return

    @commands.command()
    async def hug(self, ctx, receiver: discord.Member):
        if receiver == None:
            await ctx.send("erm... i cant find that person")
            return

        embedinfo = dfunctions.generatesimpleembed(ctx.author.display_name + " hugs " + receiver.display_name, " ", colour=discord.Colour.magenta())
        embedinfo.set_image(url="https://v.redd.it/y0b4muq5jlu41")

        if receiver == ctx.guild.me:
            await ctx.send(":heart:")
            
        return

    @commands.command()
    async def randomkurumi(self, ctx):
        rand = random.randint(0,len(kurumilinks)-1)

        embedinfo = dfunctions.generatesimpleembed(" ", " ", colour=discord.Colour.magenta())
        embedinfo.set_image(url=kurumilinks[rand])

        await ctx.send(embed=embedinfo)
        return

    @commands.command()
    async def rps(self, ctx, item=None):
        if item == None:
            await ctx.send("you need to state if you're using rock, paper or scissors...")
            return

        if item != "rock" and item != "paper" and item != "scissors":
            await ctx.send("i dont think that item exists in rock, paper, scissors...")
            return

        # pick random item
        clientitem = ["rock", "paper", "scissors"][random.randint(0,2)]

        if item == clientitem:
            await ctx.send("i picked " + clientitem + " " + rpsdict[clientitem][1] + " looks like it's a tie 😅")
        elif rpsdict[clientitem][0] == item: # if bot wins
            await ctx.send("i picked " + clientitem + " " + rpsdict[clientitem][1] + " i win!")
        else: # bot loses lol
            await ctx.send("i picked " + clientitem + " " + rpsdict[clientitem][1] + " looks like i lost...")

        return

    @commands.command()
    async def eightball(self, ctx, message=None):
        if message == None:
            await ctx.send("erm... u need to ask a question...")
            return

        rand = random.randint(0,len(eightballresponse)-1)
        await ctx.send("okayy~! the 8ball says \"" + eightballresponse[rand] + "\"")
        return

    @commands.command()
    async def coinflip(self, ctx):
        rand = random.randint(0,1)
        if rand == 0:
            coin = "**heads**"
        else:
            coin = "**tails**"

        await ctx.send("okayy~! i got " + coin)
        return

    @commands.command()
    async def secks(self, ctx, receiver: discord.Member):
        if receiver == None:
            await ctx.send("erm... i cant find that person")
            return

        embedinfo = dfunctions.generatesimpleembed(ctx.author.display_name + " secksd " + receiver.display_name, " ", colour=discord.Colour.magenta())
        embedinfo.set_image(url="https://v.redd.it/y0b4muq5jlu41")

        await ctx.send(embed=embedinfo)

        if receiver == ctx.guild.me:
            await ctx.send(":flushed:")

        return

def setup(client):
    client.add_cog(fun(client))