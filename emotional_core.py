import discord
import random
from discord.ext import commands


class Emotions:
    def __init__(self, client):
        self.client = client

    @commands.command(pass_context=True)
    async def status(self, ctx):
        responses = ["Artemis is ok!",
                     "Artemis is currently online.",
                     ":thumbsup:",
                     "No problems, at the moment."]
        await self.client.send_message(ctx.message.channel, random.choice(responses))


def setup(client):
    client.add_cog(Emotions(client))
