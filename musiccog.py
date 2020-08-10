import discord
from discord.ext import commands
from discord.voice_client import VoiceClient
from discord.utils import get

import asyncio
import youtube_dl
import datetime
import itertools
from async_timeout import timeout

import dfunctions

ffmpeg_options = {
    'options': '-vn'
}

ytdl_format_options = {
    'format': 'bestaudio/best',
    'filter': "audio",
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0', # bind to ipv4 since ipv6 addresses cause issues sometimes
    'forcethumbnail': True
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

        self.playlist = []

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        info = ytdl.extract_info(url, download=False)

        if 'entries' in info:
            # take first item from a playlist
            info = info['entries'][0]

        if info["duration"] > 600: # around 10 mins
            return [100, info]

        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=True))

        if 'entries' in data:
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)

        # wacky stuff
        stuff = [cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data), data]
        return stuff

    @classmethod
    async def regather_stream(cls, data, *, loop):
        loop = loop or asyncio.get_event_loop()
        requester = data['requester']

        to_run = partial(ytdl.extract_info, url=data['webpage_url'], download=False)
        data = await loop.run_in_executor(None, to_run)

        stuff = [cls(discord.FFmpegPCMAudio(data['url']), data=data, requester=requester), data]
        return stuff
        
class MusicPlayer:
    # thanks EvieePy
    # https://gist.github.com/EvieePy/ab667b74e9758433b3eb806c53a19f34
    # created when u&connect
    # destroyed when u&disconnect

    def __init__(self, ctx):
        self.bot = ctx.bot
        self.guild = ctx.guild
        self.channel = ctx.channel
        self.cog = ctx.cog

        self.queue = asyncio.Queue()
        self.next = asyncio.Event()
        self.current = None
        self.looping = False

        ctx.bot.loop.create_task(self.playerloop())

    def getqueueitems(self, maxitems=5):
        print(self.queue.qsize())
        if self.queue.qsize() < 1:
            return None

        return list(itertools.islice(self.queue._queue, 0, maxitems))

    async def playerloop(self):
        await self.bot.wait_until_ready()

        while not self.bot.is_closed():
            self.next.clear()

            try:
                # Wait for the next song. If we timeout cancel the player and disconnect...
                async with timeout(300):  # 5 minutes...
                    source = await self.queue.get()
            except asyncio.TimeoutError:
                await self.channel.send("i have not played anything in a while so i am leaving!")
                return self.destroy(self.guild)

            self.current = source[0]
            self.guild.voice_client.play(source[0], after=lambda _: self.bot.loop.call_soon_threadsafe(self.next.set))

            embedinfo = dfunctions.generatesimpleembed(source[0].title, "[youtube link](https://youtu.be/" + source[1]["display_id"] + ")\n\n[download video](" + source[1]["url"] + ")\n" + "[download audio](" + source[1]["formats"][0]["url"] + ")", colour=discord.Colour(int("0xFF0000", 16)))
            embedinfo.set_thumbnail(url="https://img.youtube.com/vi/" + source[1]["display_id"] + "/mqdefault.jpg") # ytdl seems unreliable when getting thumbnails
            embedinfo.set_author(name="now playing", icon_url="https://i.ibb.co/c8yTt7c/music.png")
            embedinfo.add_field(name="views", value="{:,}".format(source[1]["view_count"]), inline=True)
            embedinfo.add_field(name="length", value=str(datetime.timedelta(seconds=source[1]["duration"]))[2:])
            embedinfo.add_field(name="uploaded by", value=source[1]["uploader"], inline=True)

            await self.channel.send(embed=embedinfo)

            await self.next.wait()

            source[0].cleanup()

            if not self.looping:
                self.current = None

    def destroy(self, guild):
        """Disconnect and cleanup the player."""
        return self.bot.loop.create_task(self.cog.cleanup(guild))

class music(commands.Cog):
    def __init__(self,client):
        self.client = client
        self.players = {}
        self.youtubered = int("0xFF0000", 16)
        return

    async def cleanup(self, guild):
        try:
            await guild.voice_client.disconnect()
        except AttributeError:
            pass

        try:
            del self.players[guild.id]
        except KeyError:
            pass

    def get_player(self, ctx):
        """Retrieve the guild player, or generate one."""
        try:
            player = self.players[ctx.guild.id]
        except KeyError:
            player = MusicPlayer(ctx)
            self.players[ctx.guild.id] = player
        
        return player

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if member == self.client.user:
            if before.channel != None and before.channel != after.channel and after.channel != None:
                # get player
                try:
                    player = self.players[member.guild.id]
                except KeyError:
                    print("bruh")
                    return

                await player.guild.voice_client.disconnect()
                await player.channel.send(embed=dfunctions.generatesimpleembed("Disconnected", "I have been moved to a different channel so I have disconnected myself!"))
                await self.cleanup(member.guild)
        return

    @commands.command(aliases=["con"])
    async def connect(self, ctx):
        voicechannel = ctx.author.voice
        if voicechannel == None:
            await ctx.send("you have to connect to a voice channel for me to join!")
            return

        voicechannel = voicechannel.channel
        vc = ctx.voice_client
        player = self.get_player(ctx)

        try:
            voice = await voicechannel.connect(timeout=3, reconnect=False)
        except:
            await ctx.send("im already connected to a voice channel!")
            return
        await ctx.send("oka")
        return

    @commands.command(aliases=["dcon","discon","disc"])
    async def disconnect(self, ctx):
        voicechannel = ctx.author.voice.channel

        if ctx.guild.me.voice == None:
            await self.cleanup(ctx.guild)
            return

        if ctx.guild.me.voice.channel == voicechannel:
            voice = get(self.client.voice_clients, guild=ctx.guild)
        else:
            await ctx.send("you cant do that if you are not with me!")
            return

        await self.cleanup(ctx.guild)
        return

    @commands.command(aliases=["p"])
    async def play(self, ctx, *, music):
        voicechannel = ctx.author.voice.channel

        try:
            voice = await voicechannel.connect(timeout=3, reconnect=False)
        except discord.ClientException:
            if ctx.guild.me.voice.channel == voicechannel:
                voice = get(self.client.voice_clients, guild=ctx.guild)
            else:
                await ctx.send("im already connected to another voice channel!")
                return
        except:
            await ctx.send("nah")
            return

        await ctx.send("oka")
        player = self.get_player(ctx)
        THE = None
        vc = ctx.voice_client
        
        async with ctx.channel.typing():
            try:
                THE = await YTDLSource.from_url(music)

                if THE[0] == 100:
                    await ctx.send("the video \"**{}**\" is too long! (10 minute limit) get a shorter video!".format(THE[1]["title"]))
                    return

                if voice.is_playing() == True:
                    #await ctx.send("added to the queue!")
                    embedinfo = dfunctions.generatesimpleembed(THE[0].title, "[youtube link](https://youtu.be/" + THE[1]["display_id"] + ")\n\n[download video](" + THE[1]["url"] + ")\n" + "[download audio](" + THE[1]["formats"][0]["url"] + ")", colour=discord.Colour(self.youtubered))
                    embedinfo.set_thumbnail(url="https://img.youtube.com/vi/" + THE[1]["display_id"] + "/mqdefault.jpg") # ytdl seems unreliable when getting thumbnails
                    embedinfo.set_author(name="added to queue", icon_url="https://i.ibb.co/SXBtBm7/threedot2.png")
                    embedinfo.add_field(name="views", value="{:,}".format(THE[1]["view_count"]), inline=True)
                    embedinfo.add_field(name="length", value=str(datetime.timedelta(seconds=THE[1]["duration"]))[2:])
                    embedinfo.add_field(name="uploader", value=THE[1]["uploader"], inline=True)
                    await ctx.send(embed=embedinfo)
                await player.queue.put(THE)
                
            except Exception as errorstring:
                icecube = ctx.guild.get_member(208192812108349443)
                if icecube == None: # fail silently if im not in the server
                    await ctx.send("erm... seems like something went wrong")
                else:
                    await ctx.send("erm... seems like something went wrong " + icecube.mention)
                await ctx.send("```\n" + str(errorstring) + "\n```")
                return
        return

    @commands.command()
    async def stop(self, ctx):
        vc = ctx.voice_client
        if not vc or not vc.is_connected():
            return await ctx.send('I am not currently playing anything!', delete_after=20)

        await self.cleanup(ctx.guild)
        await ctx.send("oka")
        return

    @commands.command(aliases=["s"])
    async def skip(self, ctx):
        voice = get(self.client.voice_clients, guild=ctx.guild)
        if voice.is_connected() == False:
            await ctx.send("im not connected to a voice channel :/")
            return

        if voice.is_playing() == False:
            await ctx.send("im not playing anything :/")
            return

        voice.stop()
        await ctx.send("oka")
        return

    """
    @commands.command(aliases=["q"])
    async def queue(self, ctx):
        vc = ctx.voice_client

        print(player)
        if player.queue.qsize() == 0:
            await ctx.send('there is nothing in the queue!')
            return

        upcoming = player.getqueueitems(5)
        fmt = '\n'.join("**`{}`**".format(x) for x in upcoming)
        print(fmt)
        embedinfo = dfunctions.generatesimpleembed('Upcoming - Next {}'.format(len(upcoming)), fmt, colour=discord.Colour(self.youtubered))

        await ctx.send(embed=embedinfo)
        return
    """
    
    """
    @commands.command(aliases=["l"])
    async def loop(self, ctx):
        vc = ctx.voice_client
        player = self.get_player(ctx)

        if player.looping == False:
            player.looping = True
            await ctx.send("okay now looping")
        else:
            player.looping = False
            await ctx.send("okay stopped looping")
        return
    

    @commands.command()
    async def remove(self, ctx, element):
        vc = ctx.voice_client
        player = self.get_player(ctx)
        
        try:
            player.queue._getters.pop(element)
        except ValueError:
            pass

        await ctx.send("removed")
        return
    """

def setup(client):
    client.add_cog(music(client))