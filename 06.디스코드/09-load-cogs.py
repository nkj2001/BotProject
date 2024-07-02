import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
load_dotenv()
TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(
    command_prefix=commands.when_mentioned_or("!"),
    description="테스트봇",
    intents=intents,
    help_command=None
)

@bot.event
async def on_ready():
    print("** 봇이 준비 되었습니다. **")
    await load_extensions()

async def load_extensions():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            print(f"load cog: {filename}")
            await bot.load_extension(f"cogs.{filename[:-3]}")

@bot.command(name="help", aliases=["h", "도움말"])
async def help(ctx, args=None):
    embed = discord.Embed(title="Help NambaksaBot", description="남박사 봇이 이해할 수 있는 명령 목록입니다.", color=0xc600ff)
    view = discord.ui.View()
    for name_cog, class_cog in bot.cogs.items():
        print(name_cog, class_cog)
        if len(class_cog.get_commands()) == 0 and name_cog == "ImageProcess":
            value_str = "```이미지를 업로드 하세요```"
        else:
            value_str = "```"
            for n in class_cog.get_commands():
                cmd = f"!{n.name}|{'|'.join(n.aliases)}"
                if n.signature:
                    cmd += f" <{n.signature}>"
                value_str += f"  {cmd} : {n.help}\n"
            value_str += "```"
        embed.add_field(
            name=f"{name_cog}: {class_cog.__doc__}",
            value=value_str,
            inline=False
        )
    await ctx.send(embed=embed, view=view)

bot.run(TOKEN, reconnect=True)