import discord
from discord.ext import commands
from discord.voice_client import VoiceClient
from discord.utils import get

import asyncio
import youtube_dl
import datetime
import itertools

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
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=True))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        if data["duration"] > 600: # around 10 mins
            return 100

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

        ctx.bot.loop.create_task(self.playerloop())

    async def playerloop(self):
        await self.bot.wait_until_ready()

        """
        try:
            # Wait for the next song. If we timeout cancel the player and disconnect...
            async with timeout(300):  # 5 minutes...
                source = await self.queue.get()
        except asyncio.TimeoutError:
            return self.destroy(self._guild)
        """

        while not self.bot.is_closed():
            self.next.clear()

            source = await self.queue.get()

            self.current = source[0]
            self.guild.voice_client.play(source[0], after=lambda _: self.bot.loop.call_soon_threadsafe(self.next.set))

            embedinfo = dfunctions.generatesimpleembed(source[0].title, "[youtube link](https://youtu.be/" + source[1]["display_id"] + ")\n\n[download video](" + source[1]["url"] + ")\n" + "[download audio](" + source[1]["formats"][0]["url"] + ")", colour=discord.Colour.magenta())
            embedinfo.set_thumbnail(url="https://img.youtube.com/vi/" + source[1]["display_id"] + "/mqdefault.jpg") # ytdl seems unreliable when getting thumbnails
            embedinfo.set_author(name="now playing", icon_url="https://i.ibb.co/Z25Tg7Z/mushroomxpfp.png")
            embedinfo.add_field(name="views", value="{:,}".format(source[1]["view_count"]), inline=True)
            embedinfo.add_field(name="length", value=str(datetime.timedelta(seconds=source[1]["duration"]))[2:])
            embedinfo.add_field(name="uploaded by", value=source[1]["uploader"], inline=True)

            await self.channel.send(embed=embedinfo)

            await self.next.wait()

            source[0].cleanup()
            self.current = None

    def destroy(self, guild):
        """Disconnect and cleanup the player."""
        return self.bot.loop.create_task(self._cog.cleanup(guild))

class music(commands.Cog):
    def __init__(self,client):
        self.client = client
        self.players = {}
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

                await player.channel.send(embed=dfunctions.generatesimpleembed("Disconnected", "I have been moved to a different channel so I have disconnected myself!"))

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

        if ctx.guild.me.voice.channel == voicechannel:
            voice = get(self.client.voice_clients, guild=ctx.guild)
        else:
            await ctx.send("you cant do that if you are not with me!")
            return

        await voice.disconnect()
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
                if voice.is_playing() == True:
                    #await ctx.send("added to the queue!")
                    embedinfo = dfunctions.generatesimpleembed(THE[0].title, "[youtube link](https://youtu.be/" + THE[1]["display_id"] + ")\n\n[download video](" + THE[1]["url"] + ")\n" + "[download audio](" + THE[1]["formats"][0]["url"] + ")", colour=discord.Colour.magenta())
                    embedinfo.set_thumbnail(url="https://img.youtube.com/vi/" + THE[1]["display_id"] + "/mqdefault.jpg") # ytdl seems unreliable when getting thumbnails
                    embedinfo.set_author(name="added to queue", icon_url="https://i.ibb.co/Z25Tg7Z/mushroomxpfp.png")
                    embedinfo.add_field(name="views", value="{:,}".format(THE[1]["view_count"]), inline=True)
                    embedinfo.add_field(name="length", value=str(datetime.timedelta(seconds=THE[1]["duration"]))[2:])
                    embedinfo.add_field(name="uploader", value=THE[1]["uploader"], inline=True)
                    await ctx.send(embed=embedinfo)
                await player.queue.put(THE)
                #player = await YTDLSource.from_url(music)
                #if player == 100:
                #    await ctx.send("video is too long! (10 minute limit) get a shorter video!")
                #    return
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

    @commands.command(aliases=["q"])
    async def queue(self, ctx):
        vc = ctx.voice_client

        player = self.get_player(ctx)
        if player.queue.empty():
            await ctx.send('there is nothing in the queue!')
            return

        upcoming = list(itertools.islice(player.queue._queue, 0, 5))
        fmt = '\n'.join("**`{}`**".format(x) for x in upcoming)
        print(fmt)
        embedinfo = discord.Embed(title='Upcoming - Next {}'.format(len(upcoming)), description=fmt)

        await ctx.send(embed=embedinfo)
        return

def setup(client):
    client.add_cog(music(client))