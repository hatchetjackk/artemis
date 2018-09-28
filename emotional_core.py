import discord
import random
import json
from discord.ext import commands


class Emotions:
    def __init__(self, client):
        self.client = client

    async def generate_points(self, message):
        message = [word.lower() for word in message.content.split()]
        good_keys = []
        bad_keys = []
        for value in good_keys:
            if value in message:
                good = 1
                self.emotional_level(good)
        for value in bad_keys:
            if value in message:
                bad = -1
                self.emotional_level(bad)

    @staticmethod
    async def emotional_level(value):
        with open('status.json') as f:
            status = json.load(f)
        status['status'] += value
        with open('status.json') as f:
            json.dump(status, f)
        return status

    @commands.command(pass_context=True)
    async def status(self, ctx):
        level = self.emotional_level(0)
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
        if level > 80:
            await self.client.send_message(ctx.message.channel, random.choice(great))
        elif level > 60:
            await self.client.send_message(ctx.message.channel, random.choice(good))
        elif level > 40:
            await self.client.send_message(ctx.message.channel, random.choice(ok))
        elif level > 20:
            await self.client.send_message(ctx.message.channel, random.choice(bad))
        else:
            await self.client.send_message(ctx.message.channel, random.choice(terrible))


def setup(client):
    client.add_cog(Emotions(client))
