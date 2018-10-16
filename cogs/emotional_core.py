import discord
import random
import json
from discord.ext import commands


class Emotions:
    def __init__(self, client):
        self.client = client

    async def generate_points(self, message):
        message = [word.lower() for word in message.content.split()]
        good_keys = ['nice', 'good', 'love']
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
        with open('files/status.json', 'r') as f:
            status = json.load(f)
        if value < 0 and status["status"]["level"] == 0:
            return
        if value > 0 and status["status"]["level"] == 50:
            return
        status["status"]["level"] += value
        print('Artemis emotional level change: {0}'.format(status["status"]["level"]))
        with open('files/status.json', 'w') as f:
            json.dump(status, f, indent=2)

    @commands.command(pass_context=True)
    async def status(self, ctx):
        with open('files/status.json', 'r') as f:
            data = json.load(f)
        level = data["status"]["level"]

        if level >= 40:
            await self.client.send_message(ctx.message.channel, random.choice(data["responses"]["great"]))
            mood = "Great"
        elif level >= 30:
            await self.client.send_message(ctx.message.channel, random.choice(data["responses"]["good"]))
            mood = "Good"
        elif level >= 20:
            await self.client.send_message(ctx.message.channel, random.choice(data["responses"]["ok"]))
            mood = 'OK'
        elif level >= 10:
            await self.client.send_message(ctx.message.channel, random.choice(data["responses"]["bad"]))
            mood = 'Bad'
        else:
            await self.client.send_message(ctx.message.channel, random.choice(data["responses"]["terrible"]))
            mood = 'Terrible'
        print('Mood: {0:<5} Level: {1}/50'.format(mood, level))
        return mood


def setup(client):
    client.add_cog(Emotions(client))
