import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
load_dotenv()
TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(
    command_prefix=commands.when_mentioned_or("!"),
    description="테스트봇",
    intents=intents
)

@bot.event
async def on_ready():
    print("** 봇이 준비 되었습니다. **")

@bot.event
async def on_connect():
    print("** 디스코드에 접속 되었습니다 **")

@bot.event
async def on_disconnect():
    print("** 디스코드에서 연결이 끊어졌습니다 **")

@bot.command()
async def ping(ctx):
    await ctx.send("pong")

@bot.command()
async def test(ctx):
    await ctx.send("test ok")

bot.run(TOKEN, reconnect=True)