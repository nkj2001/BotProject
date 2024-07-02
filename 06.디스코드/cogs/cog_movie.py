import discord
from discord.ext import commands
from modules import movie

class Movie(commands.Cog):
    '''영화 검색 봇'''
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="movie", aliases=["m", "mv", "영화검색", "영화", "dudghk"], help="영화를 검색합니다.")
    async def get_movie(self, ctx, *, param):
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

async def setup(bot):
    await bot.add_cog(Movie(bot))