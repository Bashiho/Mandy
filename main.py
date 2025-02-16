import discord
import yt_dlp
import asyncio
import os
from discord.ext import commands
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv

""" TBD, order of priority
    Bot repeatedly joins and leaves vc when uhoh is called, no clue why lmao
    In progress, might vaguely sort of work but ^ is preventing testing
        Don't download already downloaded songs, separate command to update pl
    Test bot commands, skip might break if skipping last song and test title due to new implementation
    Create ReadMe
    Test adjusting max_workers to larger numbers for potential performance improvements
    Test if intents need to be define or if they are covered by default

Reference: https://github.com/SpaceCowboyZZ/music-bot-yt-dlp/blob/main/main.py
if errors, change Mandy back to music bot in class declaration and in main()
 """
#sets bot permissions
intents = discord.Intents.default() #sets defaults
#these might be included in the default and thus would be unnecessary, can test running w/o
intents.message_content = True #read messages
intents.voice_states = True #check vcs
intents.guilds = True #look in servers
intents.guild_messages = True #see messages in servers
#initiates bot with command prefix as !! and intents as listed above
bot = commands.Bot(command_prefix='!!', intents=intents)
#global vars
queue = [] #queue of songs
title = None #save title of currently playing song for use in title command
bot.play_status = False #if bot is playing or not
executor = ThreadPoolExecutor(max_workers=4) #num of concurrent processes, used when downloading songs

PL = 'https://www.youtube.com/playlist?list=PLIJH8L_jdxO8ingMAyaOj4cuvZW4Or8l5'
test= 'https://www.youtube.com/playlist?list=PLzFA48i-nuXYFLBJ86iFEuAeoH9yS3bRm'

#settings for playlist downloads
pl_opts = { #list of options https://github.com/ytdl-org/youtube-dl/blob/master/youtube_dl/YoutubeDL.py#L128-L278
    'outtmpl': 'downloads/%(title)s.%(ext)s',
    'format': 'bestaudio/best',
    'ignoreerrors': True,
    #saves list of downloaded songs to txt file, doesn't redownload
    'download_archive': 'downloads/!downloads.txt',
    'playlistrandom': True,
    'postprocessors': [{
    'key': 'FFmpegExtractAudio',
    'preferredcodec': 'mp3',
    'preferredquality': '192',
    }]
}

#main method to load bad music pl
async def doBad(ctx):
    await moveVC(ctx)
    await ctx.send(f'Making The Bad')
    #calls playlist method to move info about playlist into data1
    data1 = await playlist(ctx)
    data = data1.copy()
    #lines up songs in queue and calls playNow()
    queue.extend(data)
    await playNow(ctx, data, url=queue.pop(0)) 
    
#used for downloading playlist
'''async def playlist(ctx):
    playlist_search = yt_dlp.YoutubeDL(pl_opts)
    loop = asyncio.get_event_loop()
    data = await loop.run_in_executor(executor, lambda: playlist_search.extract_info(url=test, download=True))
    data.append = await downloadLocal(ctx)
    data1 = []
    if 'entries' in data:
        data1 =[[entry['title'], entry['url']] for entry in data['entries']]
    await ctx.send('returning data1')
    return data1 #returns information of songs
'''

async def playlist(ctx):
    playlist_search = yt_dlp.YoutubeDL(pl_opts)
    loop = asyncio.get_event_loop()
    data = await loop.run_in_executor(executor, lambda: playlist_search.extract_info(url=test, download=True))
    local_songs = await downloadLocal(ctx)
    data1 = []

    if 'entries' in data:
        for entry in data['entries']:
            if entry:
                title = entry['title']
                url = f"downloads/{title}.mp3"
                if os.path.exists(url):
                    data1.append([title, url])
                else:
                    data1.append([entry['title'], entry['url']])

    # Add local songs to data1
    data1.extend(local_songs)

    print('returning data1')
    return data1  # returns information of songs

#handles adding local songs to queue
async def downloadLocal(ctx):
    download_dir = 'downloads'
    if not os.path.exists(download_dir):
        print(f"Directory {download_dir} does not exist.")
        return []

    files = [os.path.join(download_dir, f) for f in os.listdir(download_dir) if os.path.isfile(os.path.join(download_dir, f))]
    if not files:
        print(f"No files found in {download_dir}.")
        return []

    # thePath = os.getenv('GORP')
    local_songs = []
    for file in files:
        title = os.path.splitext(os.path.basename(file))[0]
        if(title != '!downloads'):
            # filepath = os.path.join(thePath, file)
            # filepath = filepath.replace("\\", "/")
            filepath = file.replace("\\", "/")
            local_songs.append([title, filepath])

    print(f"Found {len(local_songs)} local files in {download_dir}.")
    return local_songs
        
#method used to start playing songs
async def playNow(ctx, data, url):
    await moveVC(ctx)
    ffmpeg_options = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}   
    bot.play_status = True
    #Recursive method for playing songs after prev song ends
    def after(error):
        if error:
            print(error)
                
        if queue:
            #If songs in queue, lines up next song then plays
            next_song = queue.pop(0)
            title = f'{next_song[0]}'
            ctx.voice_client.play(discord.FFmpegPCMAudio(executable="C:/ffmpeg/bin/ffmpeg.exe", source=next_song[1], **ffmpeg_options), after=lambda e: after(e))
        else:
            #if nothing in queue, reloads playlist from data and repeats
            queue.extend(data)
            next_song = queue.pop(0)
            title = f'{next_song[0]}'
            ctx.voice_client.play(discord.FFmpegPCMAudio(source=next_song[1], **ffmpeg_options), after=lambda e: after(e))
    #Starts playing of first song in queue
    print('starting voice_client.play')
    print(url[0] + " url[0]")
    print(url[1] + " url[1]")
    ctx.voice_client.play(discord.FFmpegPCMAudio(source=url[1], **ffmpeg_options), after=lambda e: after(e))
    
#moves bot to user's vc
async def moveVC(ctx):
    print('in moveVC')
    voice_channel = ctx.author.voice.channel if ctx.author.voice else None
    if not voice_channel:
        print('moveVC if not voice_channel')
        await ctx.send("Not in vc stinky")

    if ctx.voice_client and ctx.voice_client.channel != voice_channel:
        print('moveVC if ctx.voice_client')
        await ctx.voice_client.move_to(voice_channel)

    else:
        print('moveVC else')
        await voice_channel.connect()
 
#main class of bot
class Mandy(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.queue = []
            
    #sends message containing link to the playlist for user ease of access
    @commands.command()
    async def link(self,ctx):
        await ctx.send('https://www.youtube.com/playlist?list=PLIJH8L_jdxO8ingMAyaOj4cuvZW4Or8l5')
        
    #skips current song
    @commands.command()
    async def skip(self, ctx):
        #if in vc and a song is loaded, stops curr song and starts next
        if ctx.voice_client and (ctx.voice_client.is_playing() or ctx.voice_client.is_paused()):
            #Try replacing w/ .stop() and see if it still causes problems
            ctx.voice_client.pause()
            await playNow(ctx, url = queue.pop(0))
        #if not running and queue is empty, stops curr song and sets play_status to false
        #Implement a way for it to reload playlist and continue playing
        elif not queue:
            ctx.voice_client.stop()
            bot.play_status = False
        else:
            await ctx.send('Not playing currently')
    
    #pauses song
    @commands.command()
    async def pause(self, ctx):
        bot.play_status = False
        await ctx.send('Paused :)')
        ctx.voice_client.pause()
        
    #resumes song
    @commands.command()
    async def play(self, ctx):
        bot.play_status = True
        ffmpeg_options = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
        await ctx.send('Resumed')
        ctx.voice_client.resume()
       
    #command to stop play completely
    @commands.command()
    async def stop(self, ctx):
        #if bot is playing, clears queue and curr song info and stops bot
        if bot.play_status:
            queue = []
            ctx.voice_client.stop()
            bot.play_status = False
        else:
            await ctx.send('Not playing anything')

    #loads and begins play of playlist of bad music, main function of Mandy       
    @commands.command()
    async def uhoh(self, ctx):
        await doBad(ctx)

    #command to send the title of the currently playing song
    @commands.command()
    async def title(self, ctx):
        await ctx.send(title)
        
async def main():
    #loads token from .env file
    load_dotenv()
    token = os.getenv('TOKEN')
    await bot.add_cog(Mandy(bot))
    await bot.start(token)

asyncio.run(main())