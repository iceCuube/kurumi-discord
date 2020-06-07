import discord
from discord.ext import commands
import random

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
    "https://imgur.com/AQ8ZkBe.png",
    "https://imgur.com/EBmZedG.png",
    "https://imgur.com/GoE7KYJ.png",
    "https://imgur.com/qcGFYnX.png",
    "https://imgur.com/0cz7IFw.png",
    "https://imgur.com/RjFvx3s.png",
    "https://imgur.com/fxxNUwT.png",
    "https://imgur.com/7Ja9WAI.png",
    "https://imgur.com/kRuwkMz.png",
    "https://imgur.com/v1aNLBQ.jpg",
    "https://imgur.com/MMiyxIu.png",
    "https://imgur.com/pIL4TbL.png",
    "https://imgur.com/qc7wCxx.png",
    "https://imgur.com/036r5Os.jpg",
    "https://imgur.com/EFr5JVz.png",
    "https://imgur.com/uCBwkUk.png",
    "https://imgur.com/E1LwYIW.png",
    "https://imgur.com/whwudHp.jpg",
    "https://imgur.com/g4skISJ.png",
    "https://imgur.com/oMU5djI.png",
    "https://imgur.com/UHQX5rr.png",
    "https://imgur.com/IgkSG6Y.png",
    "https://imgur.com/i4NioYS.png",
    "https://imgur.com/YpatbEK.png",
    "https://imgur.com/L0cvL0T.png",
    "https://imgur.com/xhlgJax.png",
    "https://imgur.com/mptR772.png",
    "https://imgur.com/0ZNkaNE.png",
    "https://imgur.com/GM4CqFf.png",
    "https://imgur.com/JoOuVmA.png",
    "https://imgur.com/N2mPkcv.png",
    "https://imgur.com/ARqnBfu.png",
]

class fun(commands.Cog):
    def __init__(self,client):
        self.client = client
        return

    @commands.command()
    async def randomkurumi(self, ctx):
        rand = random.randint(0,len(kurumilinks)-1)

        embedinfo = dfunctions.generatesimpleembed(" ", " ", colour=discord.Colour.magenta())
        embedinfo.set_image(url=kurumilinks[rand])

        await ctx.send(embed=embedinfo)
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
            await ctx.send("i cant find that member")
            return

        embedinfo = dfunctions.generatesimpleembed(ctx.author.display_name + " has secksd " + receiver.display_name, " ", colour=discord.Colour.magenta())
        embedinfo.set_image(url="https://v.redd.it/y0b4muq5jlu41")

        await ctx.send(embed=embedinfo)

        return

def setup(client):
    client.add_cog(fun(client))