import discord
from discord.ext import commands
import yt_dlp as youtube_dl
import os  # Import os module to read environment variables
import asyncio

# Read bot token from Render's environment variable
TOKEN = os.getenv("DISCORD_BOT_TOKEN")

# Bot setup
intents = discord.Intents.default()
intents.voice_states = True  # Allow bot to join voice channels
bot = commands.Bot(command_prefix="!", intents=intents)

# Track voice client state
voice_client = None
voice_channel = None

async def play_audio(ctx, url):
    global voice_client, voice_channel

    if not ctx.author.voice:
        await ctx.send("You must be in a voice channel to use this command.")
        return

    if voice_client is None or not voice_client.is_connected():
        voice_channel = ctx.author.voice.channel
        voice_client = await voice_channel.connect()

    # YouTube audio extraction options
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegAudioConvertor',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': 'downloads/%(id)s.%(ext)s',
        'quiet': True
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        url2 = info['formats'][0]['url']
        voice_client.play(discord.FFmpegPCMAudio(url2))

@bot.command()
async def play(ctx, url):
    await play_audio(ctx, url)
    await ctx.send(f"Now playing: {url}")

@bot.command()
async def stop(ctx):
    global voice_client
    if voice_client and voice_client.is_playing():
        voice_client.stop()
    if voice_client:
        await voice_client.disconnect()

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

# Run bot with token from environment variable
bot.run(TOKEN)
