import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
from modules import movie, money_exchange_rate
load_dotenv()
TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(
    command_prefix=commands.when_mentioned_or("!"),
    description="테스트봇",
    intents=intents
)

# !movie 바람과 함께 사라지다
@bot.command(name="movie", aliases=["m", "mv", "영화검색", "영화", "dudghk"])
async def get_movie(ctx, *, param):
    results = movie.search_movie_daum(param)
    if results:
        embed = discord.Embed(title=results.get("title"), color=discord.Color.blue())
        embed.set_image(url=results.get("thumbnail"))
        for k, v in results.get("info").items():
            if v:
                embed.add_field(name=k, value=v, inline=True)
        await ctx.send(embed=embed)
    else:
        await ctx.send("검색 결과가 없습니다.")

@bot.command(name="embed")
async def embed_test(ctx):
    embed = discord.Embed(
        title="Embed 제목",
        description="이것은 Embed의 설명 입니다.",
        color=discord.Color.blue()
    )
    embed.add_field(name="필드1", value="필드1의 값", inline=False)
    embed.add_field(name="필드2", value="필드2의 값", inline=True)
    embed.add_field(name="필드3", value="필드3의 값", inline=True)
    embed.set_thumbnail(url="https://thumb.ac-illust.com/22/22adc22593b1db4de8f05dc1332b3eb5_t.jpeg")
    embed.set_image(url="https://cdn.mhns.co.kr/news/photo/202101/426827_562550_1753.jpg")
    embed.set_footer(text="발자국 텍스트", icon_url="https://thumb.ac-illust.com/22/22adc22593b1db4de8f05dc1332b3eb5_t.jpeg")
    embed.set_author(name="작성자 이름", url="https://www.naver.com/", icon_url="https://thumb.ac-illust.com/22/22adc22593b1db4de8f05dc1332b3eb5_t.jpeg")
    embed.timestamp = ctx.message.created_at
    await ctx.send(embed=embed)

@bot.command(name="money")
async def get_money(ctx, *, param):
    money, source, target = money_exchange_rate.google_money_exchange_rate(param)
    output = f"```{money} {target}```"
    await ctx.send(output)

bot.run(TOKEN, reconnect=True)