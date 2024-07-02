import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
load_dotenv()
TOKEN = os.getenv("TOKEN")

CHAT_LIMIT_USERS = {}

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(
    command_prefix=commands.when_mentioned_or("!"),
    description="테스트봇",
    intents=intents
)

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    if "바보" in message.content:
        await message.delete()
        await message.channel.send(f"{message.author.mention}, 메제지가 삭제되었습니다. 부적절한 언어 사용은 자제해주세요.")
        if message.author.id in CHAT_LIMIT_USERS:
            CHAT_LIMIT_USERS[message.author.id] += 1
            if CHAT_LIMIT_USERS[message.author.id] >= 3:
                role = discord.utils.get(message.guild.roles, name="채팅금지")
                await message.author.add_roles(role)
                await message.channel.send(f"3회 이상 제재되어 채팅이 금지됩니다.")
        else:
            CHAT_LIMIT_USERS[message.author.id] = 1
    await bot.process_commands(message)

@bot.command(name="delete")
@commands.has_role("메세지관리자")
async def delete_message(ctx):
    await ctx.channel.purge(limit=None)

@delete_message.error
async def delete_message_error(ctx, error):
    if isinstance(error, commands.MissingRole):
        await ctx.send(f"{ctx.author.mention}, 권한이 없습니다.")

bot.run(TOKEN, reconnect=True)