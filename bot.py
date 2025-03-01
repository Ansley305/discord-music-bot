import discord
import os
from dotenv import load_dotenv  # Import dotenv to load environment variables

# Load environment variables from .env file
load_dotenv()

# Get the bot token from environment variables
TOKEN = os.getenv("DISCORD_TOKEN")

# Check if token is loaded correctly
if TOKEN is None:
    raise ValueError("No DISCORD_TOKEN found in environment variables. Please check your .env file.")

# Initialize the bot with intents
intents = discord.Intents.default()
intents.message_content = True  # Enable message content intent if needed
bot = discord.Bot(intents=intents)

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
        await ctx.respond(f"🎶 Joined `{channel.name}`")
    else:
        await ctx.respond("❌ You need to be in a voice channel first!")

@bot.command()
async def leave(ctx):
    """Leave the voice channel."""
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.respond("👋 Left the voice channel.")
    else:
        await ctx.respond("❌ I'm not in a voice channel!")

@bot.command()
async def play(ctx, url: str):
    """Play a YouTube video as audio."""
    if not ctx.voice_client:
        if ctx.author.voice:
            channel = ctx.author.voice.channel
            await channel.connect()
        else:
            return await ctx.respond("❌ You need to be in a voice channel first!")

    ctx.voice_client.stop()

    FFMPEG_OPTIONS = {
        'options': '-vn'
    }

    ytdl = youtube_dl.YoutubeDL({'format': 'bestaudio'})
    info = ytdl.extract_info(url, download=False)
    url2 = info['url']
    source = await discord.FFmpegOpusAudio.from_probe(url2, **FFMPEG_OPTIONS)

    ctx.voice_client.play(source)
    await ctx.respond(f"🎶 Now playing: **{info['title']}**")

@bot.command()
async def pause(ctx):
    """Pause the currently playing audio."""
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.pause()
        await ctx.respond("⏸️ Paused.")
    else:
        await ctx.respond("❌ Nothing is playing!")

@bot.command()
async def resume(ctx):
    """Resume the paused audio."""
    if ctx.voice_client and ctx.voice_client.is_paused():
        ctx.voice_client.resume()
        await ctx.respond("▶️ Resumed.")
    else:
        await ctx.respond("❌ Nothing is paused!")

@bot.command()
async def stop(ctx):
    """Stop the audio playback."""
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        await ctx.respond("⏹️ Stopped playback.")
    else:
        await ctx.respond("❌ Nothing is playing!")

# Run the bot
bot.run(TOKEN)
