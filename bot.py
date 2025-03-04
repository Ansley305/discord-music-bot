import os
import discord
from discord.ext import commands
import yt_dlp as youtube_dl
import asyncio
from dotenv import load_dotenv
import threading
from flask import Flask

# Load environment variables
load_dotenv()

# Initialize bot with intents
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# yt-dlp options
ydl_opts = {
    'format': 'bestaudio/best',
    'outtmpl': 'downloads/%(id)s.%(ext)s',
    'quiet': True,
    'noplaylist': True,
    'cookiefile': 'cookies.txt',
    'sleep_interval': 5,
    'max_sleep_interval': 10,
    'ratelimit': 5000000,
    'source_address': '0.0.0.0',
}

# Flask app to keep bot alive
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

def run_flask():
    app.run(host="0.0.0.0", port=8080)

# Command: Join Voice Channel
@bot.command()
async def join(ctx):
    channel = ctx.author.voice.channel if ctx.author.voice else None
    if not channel:
        await ctx.send("You need to join a voice channel first!")
        return
    
    if ctx.voice_client:
        await ctx.send("Bot is already connected.")
        return

    try:
        await channel.connect(reconnect=True, timeout=10)
        await ctx.send(f"Joined {channel.name}")
    except Exception as e:
        await ctx.send(f"Error joining voice channel: {str(e)}")

# Command: Play Audio
@bot.command()
async def play(ctx, url: str):
    if not ctx.voice_client:
        await ctx.invoke(join)

    voice_client = ctx.voice_client
    if not voice_client:
        await ctx.send("Failed to join a voice channel.")
        return

    try:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            url2 = info['url']
        
        if not voice_client.is_playing():
            voice_client.play(discord.FFmpegPCMAudio(url2))
            await ctx.send(f"Now playing: {info['title']}")
        else:
            await ctx.send("Already playing a song! Use `!skip` to change.")
    except Exception as e:
        await ctx.send(f"Error playing song: {str(e)}")

# Command: Pause
@bot.command()
async def pause(ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.pause()
        await ctx.send("Audio paused.")
    else:
        await ctx.send("No audio is currently playing.")

# Command: Resume
@bot.command()
async def resume(ctx):
    if ctx.voice_client and ctx.voice_client.is_paused():
        ctx.voice_client.resume()
        await ctx.send("Audio resumed.")
    else:
        await ctx.send("No paused audio to resume.")

# Command: Skip
@bot.command()
async def skip(ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        await ctx.send("Skipped the current song.")
    else:
        await ctx.send("No audio is currently playing.")

# Command: Disconnect
@bot.command()
async def stop(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("Disconnected from voice channel.")
    else:
        await ctx.send("Bot is not connected to any voice channel.")

# Auto-Reconnect if Bot Disconnects
@bot.event
async def on_voice_state_update(member, before, after):
    if member.id == bot.user.id:
        voice_client = member.guild.voice_client
        if voice_client and not voice_client.is_connected():
            try:
                await asyncio.sleep(3)
                await voice_client.connect(reconnect=True, timeout=10)
            except Exception as e:
                print(f"Error reconnecting to voice: {e}")

# Command: Queue Placeholder
@bot.command()
async def queue(ctx, url: str):
    await ctx.send(f"Queued song: {url}")

# Command: Show Currently Playing Song
@bot.command()
async def current(ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
        await ctx.send("Currently playing a song.")
    else:
        await ctx.send("No song is currently playing.")

# Start bot
TOKEN = os.getenv('DISCORD_TOKEN')

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    if TOKEN:
        bot.run(TOKEN)
    else:
        print("Error: No bot token found. Set the DISCORD_TOKEN environment variable.")
