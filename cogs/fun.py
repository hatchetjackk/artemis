import discord
import random
from discord.ext import commands


class Fun:
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def ping(self):
        print("ping/pong")
        await self.client.say(':ping_pong: Pong')

    @commands.command()
    async def roll(self, dice: str):
        try:
            rolls, limit = map(int, dice.split('d'))
            print(rolls, limit)
        except Exception as e:
            print(e)
            await self.client.say('Please use the format "NdN" when rolling dice. Thanks!')
            return
        result = ', '.join(str(random.randint(1, limit)) for value in range(rolls))
        await self.client.say(result)

    @commands.command(pass_context=True)
    async def hello(self, ctx):
        responses = ["Hi, {0.author.mention}!",
                     "Ahoy, {0.author.mention}!",
                     "Hey there, {0.author.mention}!",
                     "*[insert traditional greeting here]*",
                     "*0100100001000101010011000100110001001111*\nAhem, I mean: hello!",
                     "Hello. Fine weather we're having.",
                     "Hello, fellow human!"]
        msg = random.choice(responses).format(ctx.message)
        await self.client.send_message(ctx.message.channel, msg)


def setup(client):
    client.add_cog(Fun(client))
