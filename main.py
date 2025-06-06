import discord
import yt_dlp
import asyncio
import os
from discord.ext import commands
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv
from nacl.secret import Aead

""" TBD
    looping seems to also be not so working so good :(
    improve the join/leave command idea
    Fix issues with not working when disconnecting/moving to different vcs
        Seems to occur when bot is moved to empty vc then into vc with user
    Test dungeon keeper idea
        Separate bot that sits in dungeon vc so that mandy can be moved to it and not have problems
    See if can find way to have it not need to be in vc all the time, might be easier after ^
    Clean up test stuff 
    Maybe find a way to have stop > uhoh not require reconnecting to vc
    Don't download already downloaded songs, separate command to update pl

    Reference: https://github.com/SpaceCowboyZZ/music-bot-yt-dlp/blob/main/main.py
"""
#sets bot permissions
intents = discord.Intents.default() #sets defaults
#these might be included in the default and thus would be unnecessary, can test running w/o
intents.message_content = True #read messages
intents.voice_states = True #check vcs
intents.guilds = True #look in servers
intents.guild_messages = True #see messages in servers
#initiates bot with command prefix as !! and intents as listed above
bot = commands.Bot(command_prefix='!!', intents=intents, activity=discord.Game(name="!!whar"))
#global vars
data = None
bot.songName = None
bot.stop = False
bot.play_status = False #if bot is playing or not
bot.inChat = None
executor = ThreadPoolExecutor(max_workers=4) #num of concurrent processes, used when downloading songs

PL = 'https://www.youtube.com/playlist?list=PLIJH8L_jdxO8ingMAyaOj4cuvZW4Or8l5'
test= 'https://www.youtube.com/playlist?list=PLzFA48i-nuXYFLBJ86iFEuAeoH9yS3bRm'

#main method to load bad music pl
async def doBad(ctx):
    await ctx.send(f'Making The Bad')
    data1 = await playlist(ctx)
    data = data1.copy()
    # await ctx.send("Done downloading playlist")
    await playNow(ctx)
    
async def playlist(ctx):
    #settings for playlist downloads
    pl_opts = { #list of options https://github.com/ytdl-org/youtube-dl/blob/master/youtube_dl/YoutubeDL.py#L128-L278
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'format': 'bestaudio/best',
        'ignoreerrors': True,
        # 'download_archive': 'downloads/!downloads.txt',
        'playlistrandom': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
            }]
    }
    
    playlist_search = yt_dlp.YoutubeDL(pl_opts)
    loop = asyncio.get_event_loop()
    data = await loop.run_in_executor(executor, lambda: playlist_search.extract_info(url=test, download=True))
    if 'entries' in data:
        if 'entries' in data:
            data1 = [[entry['title'], entry['url']] for entry in data['entries']]
    return data1 #returns information of songs

async def playNow(ctx):
    voice_client = await moveVC(ctx)
    queue = []
    queue.extend(data)
    url = queue.pop(0)
    ffmpeg_options = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}   
    bot.play_status = True
    bot.stop = False
    #Recursive method for playing songs after prev song ends
    def after(error):
        if error:
            print(error)

        if queue and not bot.stop:
            #If songs in queue, lines up next song then plays
            url = queue.pop(0)
            bot.songName = f'{url[0]}'
            ctx.voice_client.play(discord.FFmpegPCMAudio(url[1], **ffmpeg_options), after=lambda e: after(e))

        elif not bot.stop:
            #if nothing in queue, reloads playlist
            queue.extend(data)
            url = queue.pop(0)
            bot.songName = f'{url[0]}'
            ctx.voice_client.play(discord.FFmpegPCMAudio(url[1], **ffmpeg_options), after=lambda e: after(e))

        else: 
            return

    #Starts playing of first song in queue
    bot.songName = f'{url[0]}'
    ctx.voice_client.play(discord.FFmpegPCMAudio(url[1], **ffmpeg_options), after=lambda e: after(e))
    
# Moves bot to user's vc
async def moveVC(ctx):
    voice_client = discord.utils.get(bot.voice_clients, guild=ctx.guild)

    voice_channel = ctx.author.voice.channel
    if ctx.author.voice:
        if bot.inChat != voice_channel:    
            bot.inChat == voice_channel
            voice_client = await voice_channel.connect()
        
    elif not voice_client:
        await ctx.send("Not in vc stinky")
        return

    elif bot.inChat != voice_channel:
        await ctx.send("Not in same vc")
        return
    
    return voice_client
 
async def leave(ctx, type):
    if type == "stop":
        queue = []
        bot.stop = True
        ctx.voice_client.stop()
    elif type == "leave":
        ctx.voice_client.pause()
    if not ctx.voice_client:
        return
    bot.play_status = False
    # await ctx.voice_client.disconnect()      
        
# Main class of bot
class Mandy(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.queue = []

    # Sends list of commands
    @commands.command()
    async def whar(self, ctx):
        await ctx.send("Prefix = !!\n" +
        "-Join: Joins The Dungeon vc (in case of dc for whatever reason)" +
        "-Link: Sends link to playlist\n" +
        "-Name: Sends name of current song\n" + 
        "-Pause: Pauses play of current song\n" +
        "-Play: Resumes play of current song\n" +
        "-Skip: Skips current song\n" +
        "-Stop: Stops play entirely\n" +
        "-Uhoh: Downloads the playlist, joins the dungeon and starts playing when done")

    @commands.command()
    async def join(self, ctx):
        await playNow(ctx, queue, queue)

    @commands.command()
    async def leave(self,ctx):
        await leave(ctx, "leave")

    @commands.command()
    async def link(self,ctx):
        await ctx.send('https://www.youtube.com/playlist?list=PLIJH8L_jdxO8ingMAyaOj4cuvZW4Or8l5')

    @commands.command()
    async def name(self, ctx):
        await ctx.send(ctx.bot.songName)
 
    @commands.command()
    async def testpause(self, ctx):
        if bot.play_status:
            bot.play_status = False
            await ctx.send('Paused :)')
            ctx.voice_client.pause()
        elif not bot.stop:
            await ctx.send("Already paused")
        else:
            await ctx.send("Bot is already stopped")
        
    @commands.command()
    async def testplay(self, ctx):
        if bot.play_status:
            await ctx.send("Already playing")
        elif not bot.stop:
            bot.play_status = True
            ffmpeg_options = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
            await ctx.send('Resumed')
            ctx.voice_client.resume()
        else:
            await ctx.send("Bot is stopped, run !!uhoh to start it again")
       
    @commands.command()
    async def testskip(self, ctx):
        #if in vc and a song is loaded, stops curr song and starts next
        if ctx.voice_client:
            await ctx.send("skipped")
            ctx.voice_client.stop()
        else:
            await ctx.send('Not playing currently')
    
    @commands.command()
    async def stop(self, ctx):
        await leave(ctx, "stop")

    @commands.command()
    async def test(self, ctx):
        await doBad(ctx) 

async def main():
    #loads token from .env file
    load_dotenv()
    testToken = os.getenv('TEST')
    mandy = os.getenv('TOKEN')
    await bot.add_cog(Mandy(bot))
    await bot.start(testToken)

asyncio.run(main())