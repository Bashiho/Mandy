import discord
from discord.ext import commands

class help_cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
        self.help_message="""

```
General commands:
/help - displays all commands
/p <keywords> - finds song on yt and plays in curr channel
/q - displays curr music queue
/skip - skips curr song
/clear - stops music and clears q
/leave - dcs bot from vc
/pause - pauses curr song or resumes if paused
/resume - resumes playing curr song
```
"""
        self.text_channel_text = []
        
    @commands.Cog.listener()
    async def on_ready(self):
        for guild in self.bot.guilds:
            for channel in guild.text_channels:
                self.text_channel_text.append(channel)
                
        await self.send_to_all(self.help_message)
        
    async def send_to_all(self, msg):
        channel = self.bot.get_channel(523638874245955587)
        await channel.send(msg)
            
    @commands.command(name="help", help="Displays all commands")
    async def help(self,ctx):
        await ctx.send(self.help_message)
        