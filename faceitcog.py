
# https://github.com/LaughingLove/faceit_api.py
# ^ ^ ^ ^ ^
# python wrapper for faceit api

import discord
from discord import Status
from discord.ext import commands

import asyncio
import requests
import json
from PIL import Image
import urllib.request
from faceit_data import FaceitData

import dfunctions

class faceit(commands.Cog):
    def __init__(self,client):
        self.client = client
        self.faceit = FaceitData(self.client.faceitkey)

        self.headers = {
            'accept': 'application/json',
            'Authorization': 'Bearer {}'.format(self.client.faceitkey)
        }

        self.faceitorange = int("0xFF5500", 16)
        self.pttocomma = lambda x: x.replace(".", ",")
        self.setfaceitauthor = lambda x: x.set_author(name="FaceIt", icon_url="https://cdn.discordapp.com/attachments/719469199243870212/728174274841411616/faceit.png")

        self.bannerlinks = {
            "de_cache": "https://i.ibb.co/3CDTn0n/de-cache.jpgV",
            "de_dust2": "https://i.ibb.co/Fgt4Hsb/de-dust2.jpg",
            "de_inferno": "https://i.ibb.co/f4btLm2/de-inferno.jpg",
            "de_mirage": "https://i.ibb.co/DKNwNc5/de-mirage.jpg",
            "de_nuke": "https://i.ibb.co/By8kDHC/de-nuke.jpg",
            "de_overpass": "https://i.ibb.co/p4L58dm/de-overpass.jpg",
            "de_train": "https://i.ibb.co/sQ79M18/de-train.jpg",
            "de_vertigo": "https://i.ibb.co/PxGk8t6/de-vertigo.jpg"
        }

        return

    # function to manually request with url for debugging
    def manualrequest(self, url):
        res = requests.get("https://open.faceit.com/data/v4" + url, headers=self.headers)
        if res.status_code is 200:
            return json.loads(res.content.decode('utf-8'))

        return res.status_code

    def getaveragestats(self, allsegments):
        stats = {}

        for segment in allsegments:
            for statname, value in segment["stats"].items():
                if statname in stats:
                    stats[statname] += float(value)
                else:
                    stats[statname] = float(value)

        numbermaps = len(allsegments)
        for x in stats.keys():
            stats[x] = round(stats[x] / numbermaps, 2)

        return stats

    # function to print stats
    def statstoline(self, statname, stat1, stat2):
        if float(stat1) > float(stat2):
            stat1 = dfunctions.formatspaces("[{}]".format(stat1), 10)
            stat2 = dfunctions.formatspaces(str(stat2), 10)
        elif float(stat1) < float(stat2):
            stat2 = dfunctions.formatspaces("[{}]".format(stat2), 10)
            stat1 = dfunctions.formatspaces(str(stat1), 10)
        else:
            stat1 = dfunctions.formatspaces(str(stat1), 10)
            stat2 = dfunctions.formatspaces(str(stat2), 10)

        stat1 = stat1.replace(".", ",")
        stat2 = stat2.replace(".", ",")

        return ".{} :: {} :: {}".format(dfunctions.formatspaces(statname, 9), stat1, stat2)

    @commands.command(aliases=["faceit"])
    async def faceituser(self, ctx, profile):
        info = self.faceit.player_details(nickname=profile)
        if info == None:
            await ctx.send("i couldnt find that faceit profile!")
            return

        url = info["faceit_url"].replace("{lang}", "en")

        text = "[profile link]({})\n\n".format(url)

        for game in info["games"].keys():
            gameinfo = info["games"][game]

            text += "**{}**:\nName: {}\nElo: {} (Lvl {})\nRegion: {}\n\n".format(str(game).upper(), gameinfo["game_player_name"], gameinfo["faceit_elo"], gameinfo["skill_level"], gameinfo["region"])

        embedinfo = dfunctions.generatesimpleembed("{}'s Faceit Profile".format(profile), text, footer="+csgo [username] for csgo stats", colour=discord.Colour(self.faceitorange))
        embedinfo.set_thumbnail(url=info["avatar"])
        embedinfo.set_image(url=info["cover_image"])
        embedinfo.add_field(name="Country", value=info["country"].upper(), inline=True)
        self.setfaceitauthor(embedinfo)

        await ctx.send(embed=embedinfo)

        #await ctx.send(str(info)[:2000])
        return

    @commands.command(aliases=["csgo", "csgouser"])
    async def faceitcsgouser(self, ctx, profile):
        info = self.faceit.player_details(nickname=profile)
        if info == None:
            await ctx.send("i couldnt find that faceit profile!")
            return

        if "csgo" not in info["games"]:
            await ctx.send("that user does not play csgo!")
            return

        csinfo = info["games"]["csgo"]
        playerstats = self.faceit.player_stats(info["player_id"], "csgo")

        if playerstats == None:
            await ctx.send("that user has not played any csgo matches!")
            return

        url = info["faceit_url"].replace("{lang}", "en")
        morestats = self.getaveragestats(playerstats["segments"])

        cranking = self.faceit.player_ranking_of_game(game_id="csgo", region=csinfo["region"], player_id=info["player_id"], country=info["country"], return_items=2) # idk why but if i request for one it gets the wrong profile bruh
        rranking = self.faceit.player_ranking_of_game(game_id="csgo", region=csinfo["region"], player_id=info["player_id"], return_items=2) # this for region

        text = "[FaceIt Profile]({})\n".format(url)
        text += "\n**Player Info**"
        text += "\nName: **{}**".format(csinfo["game_player_name"])
        text += "\nElo: **{} (Lvl {})**".format(csinfo["faceit_elo"], csinfo["skill_level"])

        level = int(csinfo["skill_level"])
        curelo = int(csinfo["faceit_elo"])

        if level > 1 and level < 10:
            minelo = ((level-2) * 150) + 801
            progress = int(round(((curelo - minelo) / 150) * 20, 0))

            bar = "{}█{}".format(progress * "-", (19-progress) * "-")

            text += "\n`{}{}`".format(dfunctions.formatspaces("-" + str(curelo - minelo), 30), dfunctions.formatspaces("+" + str(minelo + 149 - curelo), 4, reverse=True))
            text += "\n`Lvl {} |{}| Lvl {}`".format(level, bar, level+1)
            text += "\n`{}{}`".format(dfunctions.formatspaces(str(minelo), 30), minelo + 149)

        text += "\n\n**Match Info**"
        text += "\nMatches Played: **{}**".format(playerstats["lifetime"]["Matches"])
        text += "\nWins: **{}**".format(playerstats["lifetime"]["Wins"])
        text += "\nLosses: **{}**".format(int(playerstats["lifetime"]["Matches"]) - int(playerstats["lifetime"]["Wins"]))
        text += "\nWin Rate (%): **{}**".format(playerstats["lifetime"]["Win Rate %"])

        text += "\n\n**Stats (Average)**"
        text += "\nHeadshot (%): **{}**".format(playerstats["lifetime"]["Average Headshots %"])
        text += "\nKills: **{}**".format(morestats["Average Kills"])
        text += "\nKD Ratio: **{}**".format(playerstats["lifetime"]["Average K/D Ratio"])
        text += "\nKR Ratio: **{}**".format(morestats["Average K/R Ratio"])

        text += "\n\n**Streak**"
        text += "\nCurrent Win Streak: **{}**".format(playerstats["lifetime"]["Current Win Streak"])
        text += "\nLongest Win Streak: **{}**".format(playerstats["lifetime"]["Longest Win Streak"])

        text += "\n"

        gameresult = ""
        for i in playerstats["lifetime"]["Recent Results"]:
            if i == "1":
                gameresult += "✅ "
            else:
                gameresult += "❌ "

        embedinfo = dfunctions.generatesimpleembed("{}'s CS:GO Stats".format(profile), text, footer="player_id: {}".format(playerstats["player_id"]), colour=discord.Colour(self.faceitorange))
        embedinfo.set_thumbnail(url=info["avatar"])
        embedinfo.set_image(url=info["cover_image"])
        self.setfaceitauthor(embedinfo)

        embedinfo.add_field(name="**Recent Matches**", value=gameresult, inline=False)
        embedinfo.add_field(name="**Country Ranking**", value="#" + str(cranking["items"][0]["position"]), inline=True)
        embedinfo.add_field(name="**Region Ranking**", value="#" + str(rranking["items"][0]["position"]), inline=True)

        await ctx.send(embed=embedinfo)

        return

    @commands.command(aliases=["csgocompare"])
    async def faceitcsgocompare(self, ctx, profile1, profile2):
        info1 = self.faceit.player_details(nickname=profile1)
        info2 = self.faceit.player_details(nickname=profile2)

        if info1 == None:
            await ctx.send("i couldnt find that faceit profile!")
            return
        if info2 == None:
            await ctx.send("i couldnt find that faceit profile!")
            return

        if "csgo" not in info1["games"]:
            await ctx.send("that user does not play csgo!")
            return
        if "csgo" not in info2["games"]:
            await ctx.send("that user does not play csgo!")
            return

        csinfo1 = info1["games"]["csgo"]
        csinfo2 = info2["games"]["csgo"]
        playerstats1 = self.faceit.player_stats(info1["player_id"], "csgo")
        playerstats2 = self.faceit.player_stats(info2["player_id"], "csgo")

        if playerstats1 == None:
            await ctx.send("that user has not played any csgo matches!")
            return
        if playerstats2 == None:
            await ctx.send("that user has not played any csgo matches!")
            return

        morestats1 = self.getaveragestats(playerstats1["segments"])
        morestats2 = self.getaveragestats(playerstats2["segments"])

        url1 = info1["faceit_url"].replace("{lang}", "en")
        url2 = info2["faceit_url"].replace("{lang}", "en")

        text = "[{}'s profile]({})\n[{}'s profile]({})\n\n".format(profile1, url1, profile2, url2)

        text += "```css\n"
        text += ".{} :: {} :: {}".format(dfunctions.formatspaces("Stats", 9), dfunctions.formatspaces(profile1, 10, replacelast=False), dfunctions.formatspaces(profile2, 10, replacelast=False))
        text += "\n\n" + self.statstoline("Elo", csinfo1["faceit_elo"], csinfo2["faceit_elo"])
        text += "\n" + self.statstoline("HS%", playerstats1["lifetime"]["Average Headshots %"], playerstats2["lifetime"]["Average Headshots %"])
        text += "\n" + self.statstoline("KDRatio", playerstats1["lifetime"]["Average K/D Ratio"], playerstats2["lifetime"]["Average K/D Ratio"])

        text += "\n\n" + self.statstoline("WinRate%", playerstats1["lifetime"]["Win Rate %"], playerstats2["lifetime"]["Win Rate %"])
        text += "\n" + self.statstoline("WinStreak", playerstats1["lifetime"]["Longest Win Streak"], playerstats2["lifetime"]["Longest Win Streak"])
        text += "\n" + self.statstoline("AvgMVPs", morestats1["Average MVPs"], morestats2["Average MVPs"])

        text += "\n\n" + self.statstoline("AvgTripl", morestats1["Average Triple Kills"], morestats2["Average Triple Kills"])
        text += "\n" + self.statstoline("AvgQuadr", morestats1["Average Quadro Kills"], morestats2["Average Quadro Kills"])
        text += "\n" + self.statstoline("AvgPenta", morestats1["Average Penta Kills"], morestats2["Average Penta Kills"])
        text += "\n```"

        embedinfo = dfunctions.generatesimpleembed("{} vs {}".format(profile1, profile2), text, footer=None, colour=discord.Colour(self.faceitorange))
        self.setfaceitauthor(embedinfo)
        #dfile = discord.File("E:/Pictures/Memes/Assets/g4.jpg", filename="g4.jpg")
        #embedinfo.set_thumbnail(url="attachment://g4.jpg")

        await ctx.send(embed=embedinfo)

        return

    @commands.command(aliases=["csgolatest"])
    async def faceitcsgolatest(self, ctx, profile):
        info = self.faceit.player_details(nickname=profile)
        if info == None:
            await ctx.send("i couldnt find that faceit profile!")
            return

        if "csgo" not in info["games"]:
            await ctx.send("that user does not play csgo!")
            return

        csinfo = info["games"]["csgo"]
        playerstats = self.faceit.player_stats(info["player_id"], "csgo")

        if playerstats == None:
            await ctx.send("that user has not played any csgo matches!")
            return

        match = self.faceit.player_matches(player_id=info["player_id"], game="csgo", return_items=1)
        if match == None:
            await ctx.send("i couldnt find a match!")
            return

        matchstats = self.faceit.match_stats(match_id=match["items"][0]["match_id"])
        if matchstats == None:
            await ctx.send("i couldnt get any stats for that match!")
            return

        url = match["items"][0]["faceit_url"].replace("{lang}", "en")

        teaminfo = matchstats["rounds"][0]["teams"]
        leaderboardteam1 = sorted(matchstats["rounds"][0]["teams"][0]["players"], key=lambda x: int(x["player_stats"]["Kills"]), reverse=True)
        leaderboardteam2 = sorted(matchstats["rounds"][0]["teams"][1]["players"], key=lambda x: int(x["player_stats"]["Kills"]), reverse=True)

        text = ""

        text += "[Room Link]({})".format(url)

        text += "\n\n**Match Info**"
        text += "\nScore: **{}** - **{}**".format(teaminfo[0]["team_stats"]["Final Score"], teaminfo[1]["team_stats"]["Final Score"])
        text += "\nFirst Half: **{}** - **{}**".format(teaminfo[0]["team_stats"]["First Half Score"], teaminfo[1]["team_stats"]["First Half Score"])
        text += "\nSecond Half: **{}** - **{}**".format(teaminfo[0]["team_stats"]["Second Half Score"], teaminfo[1]["team_stats"]["Second Half Score"])
        if teaminfo[0]["team_stats"]["Overtime score"] != "0" or teaminfo[1]["team_stats"]["Overtime score"] != "0":
            text += "\nOvertime: **{}** - **{}**".format(teaminfo[0]["team_stats"]["Overtime score"], teaminfo[1]["team_stats"]["Overtime score"])

        text += "\n\nMap: **{}**".format(matchstats["rounds"][0]["round_stats"]["Map"])

        text2 = "```css"

        y = lambda z: z["player_stats"]

        text2 += "\n#{} :: [Lv] {} :@: {} :: {} :: {} :: {} :: {} :: {} :: {} :: {} :: {} :: {} ;\n".format(
            "N",
            dfunctions.formatspaces("Name", 20),
            dfunctions.formatspaces("K", 3),
            dfunctions.formatspaces("D", 3),
            dfunctions.formatspaces("A", 3),
            dfunctions.formatspaces("K/D", 4),
            dfunctions.formatspaces("K/R", 4),
            dfunctions.formatspaces("HS%", 4),
            dfunctions.formatspaces("MVP", 3),
            dfunctions.formatspaces("3K", 2),
            dfunctions.formatspaces("4K", 2),
            dfunctions.formatspaces("5K", 2)
        )

        x = 1
        text2 += "\n{}[{}]".format(' '*11, teaminfo[0]["team_stats"]["Team"])

        for guy in leaderboardteam1:
            level = next((item for item in match["items"][0]["teams"]["faction1"]["players"] if item["player_id"] == guy["player_id"]), None)
            if level == None:
                return await ctx.send("an error occured")
            text2 += "\n#{} :: {} {} :@: {} :: {} :: {} :: {} :: {} :: {} :: {} :: {} :: {} :: {} ;".format(
                x,
                dfunctions.formatspaces("[{}]".format(level["skill_level"]), 4, replacelast=False),
                dfunctions.formatspaces(guy["nickname"], 20),
                dfunctions.formatspaces(y(guy)["Kills"], 3),
                dfunctions.formatspaces(y(guy)["Deaths"], 3),
                dfunctions.formatspaces(y(guy)["Assists"], 3),
                dfunctions.formatspaces(self.pttocomma(y(guy)["K/D Ratio"]), 4),
                dfunctions.formatspaces(self.pttocomma(y(guy)["K/R Ratio"]), 4),
                dfunctions.formatspaces(y(guy)["Headshots %"] + "%", 4),
                dfunctions.formatspaces(y(guy)["MVPs"], 3),
                dfunctions.formatspaces(y(guy)["Triple Kills"], 2),
                dfunctions.formatspaces(y(guy)["Quadro Kills"], 2),
                dfunctions.formatspaces(y(guy)["Penta Kills"], 2)
            )
            x += 1

        text2 += "\n"
        x = 1
        text2 += "\n{}[{}]".format(' '*11, teaminfo[1]["team_stats"]["Team"])

        for guy in leaderboardteam2:
            level = next((item for item in match["items"][0]["teams"]["faction2"]["players"] if item["player_id"] == guy["player_id"]), None)
            if level == None:
                return await ctx.send("an error occured")
            text2 += "\n#{} :: {} {} :@: {} :: {} :: {} :: {} :: {} :: {} :: {} :: {} :: {} :: {} ;".format(
                x,
                dfunctions.formatspaces("[{}]".format(level["skill_level"]), 4, replacelast=False),
                dfunctions.formatspaces(guy["nickname"], 20),
                dfunctions.formatspaces(y(guy)["Kills"], 3),
                dfunctions.formatspaces(y(guy)["Deaths"], 3),
                dfunctions.formatspaces(y(guy)["Assists"], 3),
                dfunctions.formatspaces(self.pttocomma(y(guy)["K/D Ratio"]), 4),
                dfunctions.formatspaces(self.pttocomma(y(guy)["K/R Ratio"]), 4),
                dfunctions.formatspaces(y(guy)["Headshots %"] + "%", 4),
                dfunctions.formatspaces(y(guy)["MVPs"], 3),
                dfunctions.formatspaces(y(guy)["Triple Kills"], 2),
                dfunctions.formatspaces(y(guy)["Quadro Kills"], 2),
                dfunctions.formatspaces(y(guy)["Penta Kills"], 2)
            )
            x += 1


        text2 += "\n```"

        embedinfo = dfunctions.generatesimpleembed("{} vs {}".format(teaminfo[0]["team_stats"]["Team"], teaminfo[1]["team_stats"]["Team"]), text, colour=self.faceitorange)
        self.setfaceitauthor(embedinfo)

        if matchstats["rounds"][0]["round_stats"]["Map"] in self.bannerlinks:
            embedinfo.set_image(url=self.bannerlinks[matchstats["rounds"][0]["round_stats"]["Map"]])

        await ctx.send(embed=embedinfo)
        await ctx.send(text2)

        return

def setup(client):
    client.add_cog(faceit(client))