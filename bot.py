import discord
import os
import yt_dlp as youtube_dl  # Use yt-dlp instead of youtube_dl
from discord.ext import commands
from dotenv import load_dotenv
from flask import Flask
import threading

# Load environment variables from .env file
load_dotenv()

# Get the bot token from environment variables
TOKEN = os.getenv("DISCORD_TOKEN")

# Check if token is loaded correctly
if not TOKEN:
    raise ValueError("❌ No DISCORD_TOKEN found in environment variables. Check Render settings.")

# Initialize bot with command prefix
intents = discord.Intents.default()
intents.message_content = True  # Required for reading messages
bot = commands.Bot(command_prefix="!", intents=intents)

# Initialize Flask web server (only for keeping the app alive)
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

def run_flask():
    app.run(host="0.0.0.0", port=3000)

# FFMPEG options
FFMPEG_OPTIONS = {'options': '-vn'}

# Music Bot Commands
@bot.event
async def on_ready():
    print(f'✅ Logged in as {bot.user}')

@bot.command()
async def join(ctx):
    """Join the voice channel of the user."""
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        await channel.connect()
        await ctx.send(f"🎶 Joined `{channel.name}`")
    else:
        await ctx.send("❌ You need to be in a voice channel first!")

@bot.command()
async def leave(ctx):
    """Leave the voice channel."""
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("👋 Left the voice channel.")
    else:
        await ctx.send("❌ I'm not in a voice channel!")

@bot.command()
async def play(ctx, url: str):
    """Play a YouTube video as audio."""
    if not ctx.voice_client:
        if ctx.author.voice:
            channel = ctx.author.voice.channel
            await channel.connect()
        else:
            return await ctx.send("❌ You need to be in a voice channel first!")

    ctx.voice_client.stop()

    ytdl_options = {'format': 'bestaudio'}
    ytdl = youtube_dl.YoutubeDL(ytdl_options)

    # Extract YouTube audio info asynchronously
    loop = bot.loop
    info = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=False))
    url2 = info['url']

    source = discord.FFmpegPCMAudio(url2, **FFMPEG_OPTIONS)
    ctx.voice_client.play(source)

    await ctx.send(f"🎶 Now playing: **{info['title']}**")

@bot.command()
async def pause(ctx):
    """Pause the currently playing audio."""
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.pause()
        await ctx.send("⏸️ Paused.")
    else:
        await ctx.send("❌ Nothing is playing!")

@bot.command()
async def resume(ctx):
    """Resume the paused audio."""
    if ctx.voice_client and ctx.voice_client.is_paused():
        ctx.voice_client.resume()
        await ctx.send("▶️ Resumed.")
    else:
        await ctx.send("❌ Nothing is paused!")

@bot.command()
async def stop(ctx):
    """Stop the audio playback."""
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        await ctx.send("⏹️ Stopped playback.")
    else:
        await ctx.send("❌ Nothing is playing!")

# Run the Flask server in a separate thread
threading.Thread(target=run_flask).start()

# Run the bot
bot.run(TOKEN)
