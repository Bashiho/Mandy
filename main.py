import discord
from discord.ext import commands   
import yt_dlp
import asyncio

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

FFMPEG_OPTIONS = {
    'before_options': '-nostdin',
    'options' : '-vn'
    }

YDL_OPTIONS = {
    'format' : 'bestaudio/best'
    'outtmpl': 'downloads/%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'
    }

class MusicBot(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.queue = []
        
    @commands.command()
    async def play(self, ctx, *, search):
        voice_channel = ctx.author.voice.channel if ctx.author.voice else None
        if not voice_channel:
            return await ctx.send("Not in vc stinky")
        if not ctx.voice_client:
            await voice_channel.connect()
            
            async with ctx.typing():
                with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
                    info = ydl.extract_info(f"ytsearch:{search}", download=False)
                    if 'entries' in info:
                        info = info['entries'][0]
                    url = info['url']
                    title = info['title']
                    self.queue.append((url, title))
                    await ctx.send(f'Added to queue: **{title}**')
        if not ctx.voice_client.is_playing():
            await self.play_next(ctx)
            
            
    async def play_next(self, ctx):
        if self.queue:
            url, title = self.queue.pop(0)
            source = await discord.FFmpegOpusAudio.from_probe(url, **FFMPEG_OPTIONS)
            ctx.voice_client.play(source, after=lambda _:self.client.loop.create_task(self.play.next(ctx)))
            await ctx.send(f'Now playing **{title}**')
        elif not ctx.voice_client.is_playing():
            await ctx.send("queue is empty!")
            
    @commands.command()
    async def skip(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_playing():
            if self.queue:
                self.play.next(ctx)
            else:
                await ctx.send("queue is empty")
                await ctx.voice_client.stop()
            
    @commands.command()
    async def song(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_playing():
            info = self.info
            title = info['title']
            await ctx.send(f'Current song: **{title}**')
        
    @commands.command()
    async def uhoh(self, ctx):
        voice_channel = ctx.author.voice.channel if ctx.author.voice else None
        if not voice_channel:
            return await ctx.send("Not in vc stinky")
        if not ctx.voice_client:
            await voice_channel.connect()
            
            await ctx.send(f'Making the Bad')
            with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
                info = ydl.extract_info(f"https://www.youtube.com/playlist?list=PLHBvpu2aFjUVEXrd-7Q57k2EYtoxYSQ3G", download=False)
                #replaced if w/ while to create loop appending new songs to queue
                #also intented url, title, self.queue... to put into loop
                #change back if doesn't work, potentially need to rework entire solution
                #possible solution here: https://www.reddit.com/r/Discord_Bots/comments/130zpqn/help_on_my_music_discordpy_bot_with_playlist/
                while 'entries' in info:
                    info = info['entries'][0]
                    url = info['url']
                    title = info['title']
                    self.queue.append((url, title))
                    await ctx.send(f'Added to queue: **{title}**')
        
        if ctx.voice_client and not ctx.voice_client.is_playing():
            await self.play_next(ctx)
            
            
client = commands.Bot(command_prefix="!!", intents = intents)

async def main():
    await client.add_cog(MusicBot(client))
    await client.start('MTI4MzI0OTUyODk0NjAzNjgyOA.GzNs7j.SSB5LQvnrYJev_0IRxR9_Rwggu-pRwjOC36F4o')
    
asyncio.run(main())