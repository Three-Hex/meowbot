import os
import random
import asyncio
import inspect
import discord
from discord.ext import commands

# -------------------------- meowbot Config ---------------------------
TOKEN = "your token here"
AUDIO_FILE = r"C:\users\your_user\your_folder\your_mp3.mp3"
FFMPEG_PATH = r"C:\Program Files\ffmpeg-2025-06-04-git-a4c1a5b084-full_build\bin\ffmpeg.exe" #This is an example location. This way no setting of ffmpeg as PATH is necessary, just point to ffmpeg.exe
# ----------- a 5 minute coding adventure made by three-hex -----------

def dbg(msg: str):
    print(f"[DEBUG] {msg} (line {inspect.currentframe().f_back.f_lineno})") # This DEBUG will show in your Terminal, that way you can check details.

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
intents.guilds = True
intents.messages = True
intents.members = True

dbg("Intents configured")

bot = commands.Bot(command_prefix='!', intents=intents)
dbg("Bot created")

class AudioPlayer(commands.Cog):
    def __init__(self, bot: commands.Bot):
        dbg("AudioPlayer.__init__ entered")
        self.bot = bot
        self.voice_client: discord.VoiceClient | None = None
        self.audio_task: asyncio.Task | None = None

    @commands.command(name="meow")
    async def join(self, ctx: commands.Context):
        dbg("join command invoked")

        if ctx.author.voice is None:
            await ctx.send('You are not connected to a voice channel.')
            dbg("Author not in voice")
            return

        channel = ctx.author.voice.channel
        dbg(f"Detected voice channel: {channel}")
        dbg(f"Voice client state: {self.voice_client}")

        try:
            if self.voice_client and self.voice_client.is_connected():
                await self.voice_client.move_to(channel)
                dbg("Moved to new voice channel")
            else:
                self.voice_client = await channel.connect()
                dbg("Connected to voice channel")
        except Exception as e:
            await ctx.send(f"Error joining voice channel: {e}")
            dbg(f"Failed to join/move to voice channel: {e}")
            return

        await ctx.send(f'Joined {channel.mention}')
        dbg("Join confirmation sent")

        if self.audio_task is None or self.audio_task.done():
            self.audio_task = self.bot.loop.create_task(self.random_loop())
            dbg("Audio loop task created")

    @commands.command(name="neuterkitty")
    async def leave(self, ctx: commands.Context):
        dbg("leave command invoked")

        if self.voice_client and self.voice_client.is_connected():
            await self.voice_client.disconnect()
            await ctx.send('Disconnected.')
            dbg("Disconnected from voice channel")
        else:
            await ctx.send('Not connected to any voice channel.')
            dbg("No voice client to disconnect")

        if self.audio_task:
            self.audio_task.cancel()
            self.audio_task = None
            dbg("Audio loop task cancelled")

    async def random_loop(self):
        dbg("Entered random_loop")

        
        first_wait = 5
        dbg(f"First wait: {first_wait} seconds")
        await asyncio.sleep(first_wait)

        while True:
            if self.voice_client is None or not self.voice_client.is_connected():
                dbg("Voice client invalid or disconnected, breaking loop")
                break

            if not os.path.exists(AUDIO_FILE):
                dbg(f"Audio file {AUDIO_FILE} not found, breaking loop")
                break

            dbg("Preparing to play audio")
            audio_source = discord.FFmpegPCMAudio(AUDIO_FILE, executable=FFMPEG_PATH)

            if not self.voice_client.is_playing():
                try:
                    self.voice_client.play(audio_source)
                    dbg("Audio started playing")
                except Exception as e:
                    dbg(f"Playback failed: {e}")
            else:
                dbg("Already playing audio")

            while self.voice_client.is_playing():
                dbg("Audio still playing... sleeping 1s")
                await asyncio.sleep(1)

            dbg("Playback finished or stopped")

            
            wait_seconds = random.choice(range(5, 3601, 5))
            dbg(f"Waiting {wait_seconds} seconds before next playback")
            await asyncio.sleep(wait_seconds)

async def main():
    dbg("Main started")
    async with bot:
        await bot.add_cog(AudioPlayer(bot))
        dbg("AudioPlayer cog added")
        await bot.start(TOKEN)

if __name__ == '__main__':
    dbg("Starting bot with asyncio.run()")
    asyncio.run(main())
