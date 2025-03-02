import discord
from discord.ext import commands
import yt_dlp as youtube_dl
import os  # For environment variables
import asyncio
from flask import Flask  # Keep-alive server
import threading

# Set up Flask keep-alive web server
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is alive!"

def run():
    app.run(host="0.0.0.0", port=8080)

def keep_alive():
    server = threading.Thread(target=run)
    server.start()

# Read the bot token from environment variables
TOKEN = os.getenv("DISCORD_BOT_TOKEN")

# Set up bot with required intents
intents = discord.Intents.default()
intents.voice_states = True  # Allow voice channel interactions
bot = commands.Bot(command_prefix="!", intents=intents)

voice_client = None  # Global voice client variable

async def play_audio(ctx, url):
    global voice_client

    # Check if user is in a voice channel
    if not ctx.author.voice:
        await ctx.send("You must be in a voice channel to use this command.")
        return

    # Join the user's voice channel if not already connected
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
    await ctx.send(f"🎵 Now playing: {url}")

@bot.command()
async def stop(ctx):
    global voice_client
    if voice_client and voice_client.is_playing():
        voice_client.stop()
    if voice_client:
        await voice_client.disconnect()

@bot.event
async def on_ready():
    print(f'✅ Logged in as {bot.user}')

# Start the keep-alive server
keep_alive()

# Run the bot with the token from environment variables
bot.run(TOKEN)
