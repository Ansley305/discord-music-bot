import os
import discord
from discord.ext import commands
import yt_dlp as youtube_dl
import asyncio
from dotenv import load_dotenv
import threading
from flask import Flask

# Load environment variables from a .env file (for security, avoid hardcoding the bot token)
load_dotenv()

# Initialize the bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# FFmpeg options for yt-dlp (Updated with cookies & rate limiting)
ydl_opts = {
    'format': 'bestaudio/best',
    'outtmpl': 'downloads/%(id)s.%(ext)s',
    'quiet': True,
    'noplaylist': True,
    'cookiefile': 'cookies.txt',  # Use YouTube cookies
    'sleep_interval': 5,  # Delay to avoid rate limits
    'max_sleep_interval': 10,
    'ratelimit': 5000000,  # Limit speed (5MB/s) to avoid bans
    'source_address': '0.0.0.0',  # Avoid regional restrictions
}

# Dummy Flask app to bind to a port
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

def run_flask():
    app.run(host="0.0.0.0", port=8080)

# Command to join a voice channel
@bot.command()
async def join(ctx):
    channel = ctx.author.voice.channel
    if not channel:
        await ctx.send("You need to join a voice channel first!")
        return
    await channel.connect(reconnect=True, timeout=10)

# Command to play a YouTube video/audio
@bot.command()
async def play(ctx, url: str):
    # Check if the bot is connected to a voice channel
    if not ctx.voice_client:
        await ctx.invoke(join)

    # Set up the audio stream
    try:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            url2 = info['formats'][0]['url']
            voice_client = ctx.voice_client

            # Play the audio stream
            voice_client.play(discord.FFmpegPCMAudio(url2))

        await ctx.send(f"Now playing: {info['title']}")
    except youtube_dl.utils.DownloadError as e:
        await ctx.send(f"Error: {str(e)}\nTry using another link or checking your cookies file.")

# Command to pause audio
@bot.command()
async def pause(ctx):
    voice_client = ctx.voice_client
    if voice_client and voice_client.is_playing():
        voice_client.pause()
        await ctx.send("Audio paused.")
    else:
        await ctx.send("No audio is currently playing.")

# Command to resume audio
@bot.command()
async def resume(ctx):
    voice_client = ctx.voice_client
    if voice_client and voice_client.is_paused():
        voice_client.resume()
        await ctx.send("Audio resumed.")
    else:
        await ctx.send("Audio is not paused.")

# Command to skip the current song
@bot.command()
async def skip(ctx):
    voice_client = ctx.voice_client
    if voice_client and voice_client.is_playing():
        voice_client.stop()
        await ctx.send("Skipped the current song.")
    else:
        await ctx.send("No audio is currently playing.")

# Command to stop the bot and disconnect from the voice channel
@bot.command()
async def stop(ctx):
    voice_client = ctx.voice_client
    if voice_client:
        await voice_client.disconnect()
        await ctx.send("Disconnected from voice channel.")
    else:
        await ctx.send("Bot is not connected to any voice channel.")

# Event to handle voice state updates and reconnect if necessary
@bot.event
async def on_voice_state_update(member, before, after):
    if member.id == bot.user.id:
        voice_client = member.guild.voice_client
        if not voice_client or after.channel is None:
            return  # Do nothing if bot is not in a voice channel

        try:
            if not voice_client.is_connected():
                await voice_client.connect(reconnect=True, timeout=10)
        except Exception as e:
            print(f"Error reconnecting to voice channel: {e}")

# Command to queue a song (for later implementation of playlists and queues)
@bot.command()
async def queue(ctx, url: str):
    # A placeholder for queuing songs (implement playlist/queue later)
    await ctx.send(f"Queued song: {url}")

# Command to display the bot's current playing song
@bot.command()
async def current(ctx):
    voice_client = ctx.voice_client
    if voice_client and voice_client.is_playing():
        await ctx.send(f"Currently playing: {voice_client.source.title}")
    else:
        await ctx.send("No song is currently playing.")

# Bot token (use an environment variable for security)
TOKEN = os.getenv('DISCORD_TOKEN')

# Start Flask in a separate thread
if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    if TOKEN:
        bot.run(TOKEN)
    else:
        print("Error: No bot token found. Please ensure the DISCORD_TOKEN environment variable is set.")
