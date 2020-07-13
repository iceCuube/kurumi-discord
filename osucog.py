import discord
from discord.ext import commands

import requests
from osuapi import OsuApi, ReqConnector

import dfunctions

def calculateacc(count300, count100, count50, countmiss):
    return ((
    (6 * count300 + 2 * count100 + count50) /
    (6 * (count300 + count100 + count50 + countmiss)))*100)

class osu(commands.Cog):
    def __init__(self,client):
        self.client = client
        self.osuapi = OsuApi(self.client.osukey, connector=ReqConnector())
        self.osupink = int("0xFF66AA", 16)
        return

    @commands.command()
    async def osubest(self, ctx, osuusername=None, numberofscores=None):
        responsemessage = await ctx.send("okay~~!") # this will get edited / deleted later

        if osuusername == None:
            await responsemessage.edit(content="you need to specify a user!")
            return

        # try converting to int if its not None
        if numberofscores != None:
            try:
                numberofscores = int(numberofscores)
            except:
                await responsemessage.edit(content="your request for a '" + numberofscores + "' number of scores is not a number...")

        osuuser = self.osuapi.get_user(osuusername)[0]

        if numberofscores == None or numberofscores <= 1:
            osubestscore = self.osuapi.get_user_best(osuusername, limit=1)[0]
            beatmapinfo = self.osuapi.get_beatmaps(beatmap_id=osubestscore.beatmap_id)[0]

            embedinfo = discord.Embed(
                title = beatmapinfo.title + " [" + beatmapinfo.version + "]",
                description = beatmapinfo.artist,
                colour = discord.Colour(self.osupink)
            )

            playerinfo = "Played by: " + osuuser.username
            creatorinfo = "Beatmap by: " + beatmapinfo.creator
            dateinfo = "Played on: " + str(osubestscore.date)
            ppinfo = "PP Amount: " + str(osubestscore.pp)
            scoreinfo = "Score: " + str(osubestscore.score)

            acc = calculateacc(osubestscore.count300,osubestscore.count100,osubestscore.count50,osubestscore.countmiss)
            accinfo = "Accuracy: " + str('%.2f'%(acc)) + "%"

            if osubestscore.enabled_mods.shortname == "":
                modinfo = "Mods: None"
            else:
                modinfo = "Mods: " + str(osubestscore.enabled_mods.shortname)

            imgurl = "https://assets.ppy.sh/beatmaps/" + str(beatmapinfo.beatmapset_id) + "/covers/cover.jpg"
            pfpurl = "https://a.ppy.sh/" + str(osubestscore.user_id) + "?"
            embedinfo.set_image(url=imgurl)
            embedinfo.set_thumbnail(url=pfpurl)
            embedinfo.set_footer(text=dateinfo)
            embedinfo.set_author(name="osu!std",icon_url="https://upload.wikimedia.org/wikipedia/commons/d/d3/Osu%21Logo_%282015%29.png")
            embedinfo.add_field(name=creatorinfo, value=playerinfo, inline=False)
            embedinfo.add_field(name=scoreinfo, value=ppinfo, inline=True)
            embedinfo.add_field(name=accinfo, value=modinfo, inline=True)
            
            await responsemessage.edit(content="Here is " + osuuser.username + "'s top play", embed=embedinfo)
            return


        #
        # ------------------------------------------------------------------------------------------------------
        #


        if numberofscores > 30:
            numberofscores = 30

        osubestscore = self.osuapi.get_user_best(osuusername, limit=numberofscores)

        await ctx.send("Here are " + osuuser.username + "'s " + str(numberofscores) + " best plays")

        # print header
        header = "```css\n"
        header += "#" + "No." + " :: " + dfunctions.formatspaces("Song Title", maxlength=40) + " :: " + dfunctions.formatspaces("[Version", maxlength=20, endchar="]", addspace=True) + " :: @ Date" + (' ' * 15) + " :: Score     :: Acc    :: Mods      :: PP    ;\n"
        header += "```"
        await ctx.send(header)

        # every time x % 10 = 0, print the text
        x = 1
        text = "```css\n"

        for osuscore in osubestscore:
            beatmapinfo = self.osuapi.get_beatmaps(beatmap_id=osuscore.beatmap_id)[0]

            # get accuracy
            acc = calculateacc(osuscore.count300,osuscore.count100,osuscore.count50,osuscore.countmiss)
            if acc == 100:
                accinfo == "100.0%"
            else:
                accinfo = str('%.2f'%(acc)) + "%"

            versioninfo = "[" + beatmapinfo.version
            scoreinfo = str(osuscore.score).zfill(9)
            ppinfo = str(osuscore.pp).zfill(3)

            title = "#" + dfunctions.formatspaces(str(x), maxlength=2, addspace=True) + " :: " + dfunctions.formatspaces(beatmapinfo.title, maxlength=40) + " :: " + dfunctions.formatspaces(versioninfo, maxlength=20, endchar="]", addspace=True) + " :: @ " + str(osuscore.date) + " :: " + scoreinfo + " :: " + accinfo + " :: " + dfunctions.formatspaces(osuscore.enabled_mods.shortname, maxlength=8, addspace=True) + " :: "+ ppinfo + " ;\n"
            text += title

            if x % 10 == 0:
                text += "```"
                await ctx.send(text)
                text = "```css\n"
            
            x += 1

        # once the looping is done, send the text if it hasnt been sent yet
        if x % 10 != 0:
            text += "```"
            await ctx.send(text)
        return

    @commands.command()
    async def osurecent(self, ctx, osuusername=None, numberofscores=None):
        responsemessage = await ctx.send("okay~~!") # this will get edited / deleted later

        if osuusername == None:
            await responsemessage.edit(content="you need to specify a user!")
            return

        # try converting to int if its not None
        if numberofscores != None:
            try:
                numberofscores = int(numberofscores)
            except:
                await responsemessage.edit(content="your request for a '" + numberofscores + "' number of scores is not a number...")

        osuuser = self.osuapi.get_user(osuusername)[0]

        if numberofscores == None or numberofscores <= 1:
            osurecentscore = self.osuapi.get_user_recent(osuusername, limit=1)
            if len(osurecentscore) < 1:
                await responsemessage.edit(content="that user has not played any maps recently!")
                return

            osurecentscore = osurecentscore[0]
            beatmapinfo = self.osuapi.get_beatmaps(beatmap_id=osurecentscore.beatmap_id)[0]

            embedinfo = discord.Embed(
                title = beatmapinfo.title + " [" + beatmapinfo.version + "]",
                description = beatmapinfo.artist,
                colour = discord.Colour(self.osupink)
            )

            playerinfo = "Played by: " + osuuser.username
            creatorinfo = "Beatmap by: " + beatmapinfo.creator
            dateinfo = "Played on: " + str(osurecentscore.date)
            scoreinfo = "Score: " + str(osurecentscore.score)

            acc = calculateacc(osurecentscore.count300,osurecentscore.count100,osurecentscore.count50,osurecentscore.countmiss)
            accinfo = "Accuracy: " + str('%.2f'%(acc)) + "%"

            if osurecentscore.enabled_mods.shortname == "":
                modinfo = "Mods: None"
            else:
                modinfo = "Mods: " + str(osurecentscore.enabled_mods.shortname)

            imgurl = "https://assets.ppy.sh/beatmaps/" + str(beatmapinfo.beatmapset_id) + "/covers/cover.jpg"
            pfpurl = "https://a.ppy.sh/" + str(osurecentscore.user_id) + "?"
            embedinfo.set_image(url=imgurl)
            embedinfo.set_thumbnail(url=pfpurl)
            embedinfo.set_footer(text=dateinfo)
            embedinfo.set_author(name="osu!std",icon_url="https://upload.wikimedia.org/wikipedia/commons/d/d3/Osu%21Logo_%282015%29.png")
            embedinfo.add_field(name=creatorinfo, value=playerinfo, inline=False)
            embedinfo.add_field(name=scoreinfo, value=None, inline=True)
            embedinfo.add_field(name=accinfo, value=modinfo, inline=True)
            
            await responsemessage.edit(content="Here is " + osuuser.username + "'s most recent play\n", embed=embedinfo)
            return



        return

    @commands.command(aliases=["osu", "osuplayer"])
    async def osuuser(self, ctx, osuusername=None):
        responsemessage = await ctx.send("okay~~!") # this will get edited / deleted later

        if osuusername == None:
            await responsemessage.edit(content="you need to specify a user!")
            return

        osuuser = self.osuapi.get_user(osuusername)[0]

        #result = requests.get("https://osu.ppy.sh/api/v2/spotlights", headers=self.headers)

        #print(result)
        #print(result.content)

        embedinfo = discord.Embed(
            title = osuuser.username + "'s osu!std Stats",
            description = None,
            colour = discord.Colour(self.osupink)
        )

        pfpurl = "https://a.ppy.sh/" + str(osuuser.user_id) + "?"
        ppinfo = "PP: " + str(osuuser.pp_raw)
        rankinfo = "Rank: #" + str(osuuser.pp_rank) + " (Country: #" + str(osuuser.pp_country_rank) + ")"
        playtime = "Total play time: " + str('%.1f'%(osuuser.total_seconds_played / 3600)) + "h"
        accinfo = "Accuracy: " + str('%.2f'%(osuuser.accuracy)) + "%"

        embedinfo.set_author(name="osu!std",icon_url="https://upload.wikimedia.org/wikipedia/commons/d/d3/Osu%21Logo_%282015%29.png")
        embedinfo.set_thumbnail(url=pfpurl)
        embedinfo.add_field(name=ppinfo, value=rankinfo, inline=False)
        embedinfo.add_field(name=playtime, value=accinfo, inline=True)

        await responsemessage.edit(content="Here is " + osuuser.username + "'s stats\n", embed=embedinfo)

        return

def setup(client):
    client.add_cog(osu(client))