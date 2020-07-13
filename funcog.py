import discord
from discord.ext import commands
from discord.utils import get

import random
import asyncio

import dfunctions
import calendar

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

    @commands.command(aliases=["av"])
    async def avatar(self, ctx, avmember: discord.Member = False):
        if avmember == None:
            await ctx.send("erm... i cant find that person")
            return

        if not avmember:
            avmember = ctx.author

        text = ""

        text += "\n✅ | **Bot**" if avmember.bot else "\n❌ | **Bot**"
        text += "\n✅ | **System**" if avmember.system else "\n❌ | **System**"

        text += "\n\n[This user is now streaming!]({})".format(avmember.activity.url) if type(avmember.activity) == discord.Streaming else "\n\n"

        embedinfo = dfunctions.generatesimpleembed(None, text, colour=discord.Colour.magenta())

        embedinfo.set_author(name="{}#{}".format(avmember.name, avmember.discriminator), url=str(avmember.avatar_url), icon_url=str(avmember.avatar_url))
        embedinfo.set_image(url=str(avmember.avatar_url))
        embedinfo.set_footer(text="user id: " + str(avmember.id))

        embedinfo.add_field(name="Server Nickname", value=avmember.nick)
        embedinfo.add_field(name="Highest Role", value=str(avmember.top_role))
        embedinfo.add_field(name="Joined At", value="{} {} {}".format(avmember.joined_at.day, calendar.month_name[avmember.joined_at.month], avmember.joined_at.year))
        if avmember.premium_since != None:
            embedinfo.add_field(name="Server Boosted At", value="{} {} {}".format(avmember.premium_since.day, calendar.month_name[avmember.premium_since.month], avmember.premium_since.year))
        else:
            embedinfo.add_field(name="Server Boosted At", value="Did Not Boost")

        await ctx.send(embed=embedinfo)
        return

    @commands.command(aliases=["pfp"])
    async def userpic(self, ctx, userid=None):
        if userid == None:
            user = ctx.author
        else: 
            try:
                userid = int(userid)
            except:
                await ctx.send("thats not a number!")
                return

            user = self.client.get_user(userid)

            if user == None:
                await ctx.send("i could find a user with that id")
                return

        await ctx.send(str(user.avatar_url_as(static_format="png", size=2048)))
        #await ctx.send(embed=embedinfo)
        return

    @commands.command(aliases=["sv"])
    async def server(self, ctx):
        text = None

        embedinfo = dfunctions.generatesimpleembed(None, text, colour=discord.Colour.magenta())

        embedinfo.set_author(name=str(ctx.guild), url=str(ctx.guild.icon_url), icon_url=str(ctx.guild.icon_url))
        embedinfo.set_thumbnail(url=str(ctx.guild.icon_url))
        embedinfo.set_image(url=str(ctx.guild.splash_url))
        embedinfo.set_footer(text="server id: " + str(ctx.guild.id))

        embedinfo.add_field(name="Member Count", value=str(ctx.guild.member_count))
        embedinfo.add_field(name="Boost Count", value=str(ctx.guild.premium_subscription_count))
        embedinfo.add_field(name="Boost Level", value="None" if ctx.guild.premium_tier == 0 else str(ctx.guild.premium_tier))

        embedinfo.add_field(name="Server Region", value=str(ctx.guild.region))
        embedinfo.add_field(name="AFK Channel", value="None" if ctx.guild.afk_channel == None else str(ctx.guild.afk_channel))
        embedinfo.add_field(name="AFK Timeout", value="{} minutes".format(int(ctx.guild.afk_timeout/60)))

        embedinfo.add_field(name="Owner", value=ctx.guild.owner.mention)
        embedinfo.add_field(name="Created At", value="{} {} {}".format(ctx.guild.created_at.day, calendar.month_name[ctx.guild.created_at.month], ctx.guild.created_at.year))
        embedinfo.add_field(name="Language", value=ctx.guild.preferred_locale)

        await ctx.send(embed=embedinfo)
        return

    @commands.command(aliases=["em", "emote"])
    async def emoji(self, ctx, emoji: discord.PartialEmoji = None):
        if emoji == None:
            await ctx.send("you need to specify an emoji!")
            return

        text = ""

        #text += "{}".format(str(emoji))

        text += "\n\n✅ | **Animated**" if emoji.animated else "\n\n❌ | **Animated**"

        embedinfo = dfunctions.generatesimpleembed(None, text, colour=discord.Colour.magenta())

        embedinfo.set_author(name=":{}:".format(emoji.name), icon_url=str(emoji.url), url=str(emoji.url))
        embedinfo.set_image(url=str(emoji.url))
        embedinfo.set_footer(text="id: {}".format(emoji.id))
        print("ajibdsas")
        #embedinfo.add_field(name="Created At", value="{} {} {}".format(emoji.created_at.day, calendar.month_name[emoji.created_at.month], emoji.created_at.year))

        await ctx.send(embed=embedinfo)
        return

    @emoji.error
    async def emoji_handler(self, ctx, error):
        # handle bad argument
        if isinstance(error, commands.BadArgument):
            await ctx.send("i couldnt get that emoji. it might not be a custom emoji!")
        return

def setup(client):
    client.add_cog(fun(client))