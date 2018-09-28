import discord
import random
import json
from discord.ext import commands


class Emotions:
    def __init__(self, client):
        self.client = client

    async def generate_points(self, message):
        message = [word.lower() for word in message.content.split()]
        good_keys = ['nice', 'good', 'thanks', 'thank', 'love']
        bad_keys = ['hate', 'bad']
        for word in message:
            if word in good_keys:
                good = 1
                await self.emotional_level(good)
            if word in bad_keys:
                bad = -1
                await self.emotional_level(bad)

    @staticmethod
    async def emotional_level(value):
        with open('status.json', 'r') as f:
            status = json.load(f)
        if value < 0 and status["status"]["level"] == 0:
            return
        if value > 0 and status["status"]["level"] == 100:
            return
        status["status"]["level"] += value
        print('Artemis emotional level change: {0}'.format(status["status"]["level"]))
        with open('status.json', 'w') as f:
            json.dump(status, f)

    @commands.command(pass_context=True)
    async def status(self, ctx):
        with open('status.json', 'r') as f:
            status = json.load(f)
        level = status["status"]["level"]
        print(level)
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
