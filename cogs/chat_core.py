import random
import asyncio
import discord
import sqlite3
import cogs.utilities as utilities
from itertools import cycle
from discord.ext import commands


class Chat(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.morning_check = True

    @commands.Cog.listener()
    async def on_message(self, message):
        msg = [word.lower() for word in message.content.split()]
        content = message.content.lower()
        conn, c = await utilities.load_db()

        # todo add responses when @artemis

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
            if value in content and message.author.id != self.client.user.id and self.morning_check:
                morning_response = ['Good morning!', 'Mornin!', '*yawn" What time is it?']
                await message.channel.send(random.choice(morning_response))
                self.morning_check = False
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
        conn, c = await utilities.load_db()
        c.execute("SELECT * FROM bot_status")
        level = c.fetchone()[0]
        if (value < 0 and level == 0) or (value > 0 and level == 50):
            return
        with conn:
            try:
                level += value
                c.execute("UPDATE bot_status SET level = (:level)", {'level': level})
            except sqlite3.OperationalError as e:
                print('Unable to access DB: ', e)

    async def change_status(self):
        await self.client.wait_until_ready()
        conn, c = await utilities.load_db()
        c.execute("SELECT response FROM bot_responses WHERE message_type = 'bot_status_messages'")
        status_responses = [value[0] for value in c.fetchall()]
        msg = cycle(status_responses)
        while not self.client.is_closed():
            current_status = next(msg)
            await self.client.change_presence(activity=discord.Game(name=current_status))
            await asyncio.sleep(60 * 5)


def setup(client):
    chat = Chat(client)
    client.add_cog(chat)
    client.loop.create_task(chat.change_status())
