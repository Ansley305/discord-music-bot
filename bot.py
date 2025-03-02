import discord
from discord.ext import commands
import yt_dlp as youtube_dl
import os  # For environment variables
import asyncio
from flask import Flask  # Keep-alive server
import threading
from asyncio import sleep

# 🔹 Flask keep-alive web server for UptimeRobot
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is alive!"

def run():
    app.run(host="0.0.0.0", port=8080)

def keep_alive():
    server = threading.Thread(target=run)
    server.start()

# 🔹 Read the bot token from Render's environment variables
TOKEN = os.getenv("DISCORD_BOT_TOKEN")

# 🔹 Set up bot with intents
intents = discord.Intents.default()
intents.message_content = True  # Required for reading messages
bot = commands.Bot(command_prefix="!", intents=intents)

voice_client = None  # Global voice client variable

# 🔹 Command to join a voice channel (for debugging)
@bot.command()
async def join(ctx):
    global voice_client
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        await reconnect_voice_channel(channel)  # Call the reconnect function
        await ctx.send("✅ Joined the voice channel!")
    else:
        await ctx.send("❌ You must be in a voice channel to use this command.")

# 🔹 Play music from YouTube
@bot.command()
async def play(ctx, url):
    global voice_client

    if not ctx.author.voice:
        await ctx.send("❌ You must be in a voice channel to play music.")
        return

    if voice_client is None or not voice_client.is_connected():
        await reconnect_voice_channel(ctx.author.voice.channel)

    # YouTube audio extraction options
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegAudioFile',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': True
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        url2 = info['url']
        voice_client.play(discord.FFmpegPCMAudio(url2))
        await ctx.send(f"🎵 Now playing: {info['title']}")

# 🔹 Stop music and disconnect
@bot.command()
async def stop(ctx):
    global voice_client
    if voice_client and voice_client.is_playing():
        voice_client.stop()
    if voice_client:
        await voice_client.disconnect()
        voice_client = None
        await ctx.send("⏹ Stopped music and left the channel.")

# 🔹 Check if bot is responding
@bot.command()
async def ping(ctx):
    await ctx.send("🏓 Pong! Bot is online.")

# 🔹 Reconnect voice channel if needed
async def reconnect_voice_channel(channel):
    global voice_client
    if voice_client is not None:
        await voice_client.disconnect()
        await sleep(2)  # Wait a bit before reconnecting
    voice_client = await channel.connect()

# 🔹 Handle voice state update (for disconnects)
@bot.event
async def on_voice_state_update(member, before, after):
    global voice_client
    if before.channel != after.channel:  # Check if the bot got disconnected
        if voice_client:
            await voice_client.disconnect()
            voice_client = None
        if after.channel:
            voice_client = await after.channel.connect()

@bot.event
async def on_ready():
    print(f'✅ Logged in as {bot.user}')

# 🔹 Start keep-alive server to prevent Render from sleeping
keep_alive()

# 🔹 Run the bot with token from environment variable
bot.run(TOKEN)
