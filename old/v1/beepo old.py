import os
import discord
import nextcord
from nextcord.ext import commands
from nextcord.shard import EventItem
import wavelinkcord as wavelink
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getnev('DISCORD_TOKEN')
GUILT = os.getenv('DISCORD_GUILD')

#""""
bot_version = "0.1"

intents = nextcord.Intents.all()
client = nextcord.Client()
bot = commands.Bot(command_prefix="!", intents = intents)

@bot.event
async def on_ready():
        print("Bot Ready")
        bot.loop.create_task(on_node())
        
async def on_node():
    node: wavelink.Node = wavelink.Node(uri="http://lavalink.clxud.pro:2333", password="youshallnotpass")
    await wavelink.NodePool.connect(client=bot, nodes=[node])
    wavelink.Player.autoplay = True

@bot.slash_command(guild_ids=[523638874245955584])
async def play(interaction : nextcord.Interaction, search : str):
    
    query = await wavelink.YouTubeTrack.search(search, return_first=True)
    destination = interaction.user.voice.channel
    
    if not interaction.guild.voice_client:
        
            vc: wavelink.Player = await destination.connect(cls=wavelink.Player)
    else:
            vc: wavelink.Player = interaction.guild.voice_client
            
    if vc.queue.is_empty and not vc.is_playing():
        await vc.play(query)
        await interaction.response.send_message(f"Now Playing {vc.current.title}")
    else:
        await vc.queue.put_wait(query)
        await interaction.response.send_message(f"Now Playing {vc.current.title}")
        
@bot.slash_command(guild_ids=[523638874245955584])
async def skip(interaction: nextcord.Interaction, search : str):
    
    vc: wavelink.Player = interaction.guild.voice_client
    await vc.stop()
    await interaction.response.send_message(f"Song was skipped >:(")
    
@bot.slash_command(guild_ids=[523638874245955584])
async def pause(interaction: nextcord.Interaction):
    vc: wavelink.Player = interaction.guild.voice_client
    
    if vc.is_playing():
        
        await vc.pause()
        await interaction.response.send_message(f"Song was paused")
    else:
        await interaction.response.send_message(f"Song is already paused bozo")
        
@bot.slash_command(guild_ids=[523638874245955584])
async def resume(interaction: nextcord.Interaction):
    vc: wavelink.Player = interaction.guild.voice_client
    
    if vc.is_playing():
        
        await interaction.response.send_message(f"Song is already playing bozo")
    else:
        await interaction.response.send_message(f"Song is playing now :)))))")
        await vc.resume()
        
@bot.slash_command(guild_ids=[523638874245955584])
async def disconnect(interaction: nextcord.Interaction):
    vc: wavelink.Player = interaction.guild.voice_client
    await vc.disconnect()
    await interaction.response.send_mesage(f"The bot left because you're smelly")
    
@bot.slash_command(guild_ids=[523638874245955584])
async def queue(interaction: nextcord.Interaction):
    vc: wavelink.Player = interaction.guild.voice_client
    
    if not vc.queue.is_empty:
        song_counter = 0
        songs = []
        queue = vc.queue.copy()
        embed = nextcord.Embed(title="Queue")
        
        for song in queue:
                song_counter += 1
                songs.append(song)
                embed.add_field(name=f"[{song_counter}] Duration {song.duration}", value=f"{song.title}", inline=False)
                
        await interaction.response.send_message(embed=embed)
    else:
        await interaction.response.send_message(f"Queue is empty")
#""""
        
bot.run("MTI4MzI0OTUyODk0NjAzNjgyOA.GzNs7j.SSB5LQvnrYJev_0IRxR9_Rwggu-pRwjOC36F4o")