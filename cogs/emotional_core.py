import asyncio
import random
import discord
from artemis import load_db
from itertools import cycle
from discord.ext import commands


class Emotions:
    def __init__(self, client):
        self.client = client

    async def on_message(self, message):
        msg = [word.lower() for word in message.content.split()]
        content = message.content.lower()
        conn, c = await load_db()

        c.execute("SELECT * FROM bot_responses WHERE message_type = 'status_changing_word_good'")
        good_keys = [value[1] for value in c.fetchall()]
        c.execute("SELECT * FROM bot_responses WHERE message_type = 'status_changing_word_negative'")
        bad_keys = [value[1] for value in c.fetchall()]

        c.execute("SELECT * FROM bot_responses WHERE message_type = 'bot_responder_good'")
        good_bot = [value[1] for value in c.fetchall()]
        c.execute("SELECT * FROM bot_responses WHERE message_type = 'bot_responder_bad'")
        bad_bot = [value[1] for value in c.fetchall()]

        good_morning = ['good morning', 'morning guys', 'morning, guys', 'morning artie',
                        'good morning, artie', 'good morning, Artemis',
                        'good morning, Artie', 'morning artemis', 'good morning, arty',
                        'good morning arty']

        for word in msg:
            if word in good_keys:
                await self.emotional_level(1)
            if word in bad_keys:
                await self.emotional_level(-1)
        for value in good_morning:
            if value in content and message.author.id != self.client.user.id:
                morning_response = ['Good morning!', 'Mornin!', 'Good morning, {}!'.format(message.author.name)]
                await message.channel.send(random.choice(morning_response))
                return
        for value in good_bot:
            if value in content:
                c.execute("SELECT * FROM bot_responses WHERE message_type = 'bot_responder_good_response'")
                good_response = [value[1] for value in c.fetchall()]
                await message.channel.send(random.choice(good_response))
        for value in bad_bot:
            if value in content:
                c.execute("SELECT * FROM bot_responses WHERE message_type = 'bot_responder_bad_response'")
                bad_response = [value[1] for value in c.fetchall()]
                await message.channel.send(random.choice(bad_response))

    @staticmethod
    async def emotional_level(value):
        conn, c = await load_db()
        c.execute("SELECT * FROM bot_status")
        level = c.fetchone()[0]
        if value < 0 and level == 0:
            return
        if value > 0 and level == 50:
            return
        with conn:
            level += value
            c.execute("UPDATE bot_status SET level = (:level)", {'level': level})
        print('Artemis emotional level change: {0}'.format(level))

    @commands.command()
    async def artemis(self, ctx):
        conn, c = await load_db()
        c.execute("SELECT level FROM bot_status")
        level = c.fetchone()[0]
        if level >= 40:
            c.execute("SELECT response FROM bot_responses WHERE message_type = 'great'")
            await ctx.channel.send(random.choice([value[0] for value in c.fetchall()]))
            mood = "Great"
        elif level >= 30:
            c.execute("SELECT response FROM bot_responses WHERE message_type = 'good'")
            await ctx.channel.send(random.choice([value[0] for value in c.fetchall()]))
            mood = "Good"
        elif level >= 20:
            c.execute("SELECT response FROM bot_responses WHERE message_type = 'ok'")
            await ctx.channel.send(random.choice([value[0] for value in c.fetchall()]))
            mood = 'OK'
        elif level >= 10:
            c.execute("SELECT response FROM bot_responses WHERE message_type = 'bad'")
            await ctx.channel.send(random.choice([value[0] for value in c.fetchall()]))
            mood = 'Bad'
        else:
            c.execute("SELECT response FROM bot_responses WHERE message_type = 'terrible'")
            await ctx.channel.send(random.choice([value[0] for value in c.fetchall()]))
            mood = 'Terrible'
        print('Mood: {0:<5} Level: {1}/50'.format(mood, level))
        return mood

    async def change_status(self):
        await self.client.wait_until_ready()
        conn, c = await load_db()
        c.execute("SELECT response FROM bot_responses WHERE message_type = 'bot_status_messages'")
        status_responses = [value[0] for value in c.fetchall()]
        msg = cycle(status_responses)
        while not self.client.is_closed():
            current_status = next(msg)
            await self.client.change_presence(game=discord.Game(name=current_status))
            await asyncio.sleep(60 * 5)


def setup(client):
    client.add_cog(Emotions(client))
    client.loop.create_task(Emotions(client).change_status())
