import discord
from discord.ext import commands
from modules import youtube
from dotenv import load_dotenv
import os
import log
import config

current_file_path = __file__
dir_name = os.path.dirname(os.path.abspath(current_file_path))
load_dotenv()
TOKEN = os.getenv("TOKEN")
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
intents.reactions = True
bot = commands.Bot(
    command_prefix=commands.when_mentioned_or("!"),
    description="테스트봇",
    intents=intents
)

@bot.event
async def on_ready():
    print("** 봇이 준비 되었습니다. **")
    log.log_message("** 봇이 준비 되었습니다. **")
    await config.load_channel_list()
    await config.load_voice_list()
    await load_extensions()

@bot.command(name="delete")
@commands.has_role("메세지관리자")
async def delete_message(ctx):
    await ctx.channel.purge(limit=None)

async def load_extensions():
    for filename in os.listdir(f"{dir_name}/cogs"):
        if filename.endswith(".py"):
            print(f"load cog: {filename}")
            log.log_message(f"load cog: {filename}")
            await bot.load_extension(f"cogs.{filename[:-3]}")

@bot.command(name="search", aliases=["검색", "ys", "유튜브", "유튜브검색"], help="유튜브를 검색합니다.")
async def y_search(ctx, *, param):
    results = youtube.search_youtube(param)
    if results:
        for cnt, result in enumerate(results):
            if cnt > 4:
                break
            embed = discord.Embed(
                title=result.get("vtitle"),
                color=discord.Color.blurple()
            )
            vurl = f"https://www.youtube.com/watch?v={result.get('vid')}"
            embed.set_image(url=result.get("vthumb"))
            embed.add_field(name="조회수", value=result.get("vcount"), inline=True)
            embed.set_author(name="유튜브 링크", url=vurl, icon_url="https://www.freepnglogos.com/uploads/youtube-logo-hd-8.png")
            await ctx.send(embed=embed)
    else:
        await ctx.send("검색 결과가 없습니다.")

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    ctx = await bot.get_context(message)
    guild_id = str(ctx.guild.id) if ctx.guild else None
    if ctx.command:
        cog_name = type(ctx.command.cog).__name__ if ctx.command.cog else "No Cog"
        if cog_name == "MusicPlayer":
            if guild_id in config.channel_list:
                if config.channel_list.get(guild_id) is not None:
                    if len(config.channel_list.get(guild_id)) > 0:
                        if message.channel.id not in config.channel_list.get(guild_id):
                            channel_name = bot.get_channel(message.channel.id).name
                            await ctx.send(f"해당 명령어는 `{channel_name} 채널` 에서 사용할 수 없습니다.")
                            return
                if config.voice_list.get(guild_id) is not None:
                    if len(config.voice_list.get(guild_id)) > 0:
                        if ctx.author.voice:
                            voice_channel = ctx.author.voice.channel
                            if voice_channel.id not in config.voice_list.get(guild_id):
                                channel_name = bot.get_channel(message.channel.id).name
                                await ctx.send(f"해당 명령어는 `{voice_channel.name} 음성채널` 에서 사용할 수 없습니다.")
                                return
        await bot.process_commands(message)
bot.run(TOKEN, reconnect=True)