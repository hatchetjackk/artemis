import random
from discord.ext import commands


class Fun:
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def ping(self, ctx):

        print("ping/pong")
        await ctx.send(':ping_pong: Pong')

    @commands.command()
    async def lennie(self, ctx):
        await ctx.send('( ͡° ͜ʖ ͡°)')

    @commands.command()
    async def roll(self, ctx, dice: str):
        try:
            rolls, limit = map(int, dice.split('d'))
            print(rolls, limit)
        except Exception as e:
            print(e)
            await ctx.send('Please use the format "NdN" when rolling dice. Thanks!')
            return
        result = ', '.join(str(random.randint(1, limit)) for value in range(rolls))
        await ctx.send(result)

    @commands.command()
    async def hello(self, ctx):
        responses = ["Hi, {0.author.mention}!",
                     "Ahoy, {0.author.mention}!",
                     "Hey there, {0.author.mention}!",
                     "*[insert traditional greeting here]*",
                     "*0100100001000101010011000100110001001111*\nAhem, I mean: hello!",
                     "Hello. Fine weather we're having.",
                     "Hello, fellow human!"]
        msg = random.choice(responses).format(ctx.message)
        await ctx.send(msg)


def setup(client):
    client.add_cog(Fun(client))
