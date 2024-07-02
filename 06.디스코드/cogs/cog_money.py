import discord
from discord.ext import commands
from modules import money_exchange_rate

class Money(commands.Cog):
    '''환율 봇'''
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="money", aliases=["ex", "환율"], help="환율로 변환합니다.")
    async def exchange_money(self, ctx, *, param):
        money, source, target = money_exchange_rate.google_money_exchange_rate(param)
        if money == 0:
            await ctx.send("검색 결과가 없습니다.")
            return
        output = f"```{source} ==> {money} {target}"
        await ctx.send(output)

async def setup(bot):
    await bot.add_cog(Money(bot))