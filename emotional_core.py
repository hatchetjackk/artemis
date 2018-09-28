import discord
import random
from discord.ext import commands


class Emotions:
    def __init__(self, client):
        self.client = client

    @commands.command(pass_context=True)
    async def status(self, ctx):
        emotional_level = 50
        great = ["Artemis is doing great!",
                 "Everything is optimal.",
                 "Everything looks good from here!",
                 ":sparkler:"]
        good = ["Artemis is good!",
                "No problems, at the moment.",
                ":thumbsup:"]
        ok = ["Artemis is ok!",
              "Everything is fine.",
              "Nothing to report."]
        bad = ["Artemis is doing poorly",
               "Eh, things could be better.",
               "I don't feel so good, Mr. Star-"]
        terrible = ["Artemis is doing terribly",
                    "Couldn't get any worse in here.",
                    "Artemis is operating at sub-optimal levels.",
                    "Everything is on fire!"]
        if emotional_level > 80:
            await self.client.send_message(ctx.message.channel, random.choice(great))
        elif emotional_level > 60:
            await self.client.send_message(ctx.message.channel, random.choice(good))
        elif emotional_level > 40:
            await self.client.send_message(ctx.message.channel, random.choice(ok))
        elif emotional_level > 20:
            await self.client.send_message(ctx.message.channel, random.choice(bad))
        else:
            await self.client.send_message(ctx.message.channel, random.choice(terrible))


def setup(client):
    client.add_cog(Emotions(client))
