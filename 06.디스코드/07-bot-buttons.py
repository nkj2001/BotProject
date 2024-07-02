import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import requests
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
async def on_message(message):
    if message.author == bot.user:
        return
    if len(message.attachments) > 0:
        for file in message.attachments:
            ext = file.filename.split(".")[-1]
            if ext.lower() in ["jpg", "png"]:
                r = requests.get(file.url)
                save_image_file = f"img.{ext}"
                with open(save_image_file, "wb") as f:
                    f.write(r.content)
    await bot.process_commands(message)

@bot.command()
async def buttons(ctx):
    view = discord.ui.View()
    view.add_item(discord.ui.Button(style=discord.ButtonStyle.red, label="버튼1"))
    view.add_item(discord.ui.Button(style=discord.ButtonStyle.green, label="버튼2"))
    view.add_item(discord.ui.Button(style=discord.ButtonStyle.blurple, label="버튼3"))
    view.add_item(discord.ui.Button(style=discord.ButtonStyle.grey, label="버튼4"))
    view.add_item(discord.ui.Button(style=discord.ButtonStyle.danger, label="이모지버튼", emoji="🎄"))
    view.add_item(discord.ui.Button(style=discord.ButtonStyle.link, label="링크버튼", url="https://www.naver.com"))
    await ctx.send("버튼을 선택해주세요", view=view)

@bot.command()
async def interaction(ctx):
    view = discord.ui.View()

    async def callback_button(interaction):
        await interaction.response.send_message(f"{interaction.user.mention}님이 버튼을 눌렀습니다", ephemeral=True)

    for i in range(5):
        button = discord.ui.Button(style=discord.ButtonStyle.green, label=f"{i}.버튼")
        button.callback = callback_button
        view.add_item(button)
    await ctx.send("버튼을 선택해주세요", view=view)

bot.run(TOKEN, reconnect=True)