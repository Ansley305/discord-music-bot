import discord
from discord.ext import commands
import yt_dlp
import asyncio
import os

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@bot.command()
async def play(ctx, url: str):
    voice_channel = ctx.author.voice.channel
    if not voice_channel:
        await ctx.send("Join a voice channel first!")
        return

    vc = await voice_channel.connect() if not ctx.voice_client else ctx.voice_client

    ydl_opts = {'format': 'bestaudio'}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        url2 = info['url']

    vc.play(discord.FFmpegPCMAudio(url2), after=lambda e: print("Song finished"))
    await ctx.send(f"Now playing: {info['title']}")

@bot.command()
async def stop(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("Stopped playing.")

bot.run("MTM0NTMzOTI4NTM3MjUzODg5MA.GM9SNx.QyQW48D02lwxMFzQxsRcnDOJ1twjZhs28Ruydc")
