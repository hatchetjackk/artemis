import random
import pytz
import asyncio
import discord
from itertools import cycle
from artemis import load_db
from datetime import datetime


class Chat:
    def __init__(self, client):
        self.client = client
        self.popular_zones = {
            'pst': pytz.timezone('US/Alaska'),
            'pdt': pytz.timezone('US/Alaska'),
            'cst': pytz.timezone('US/Mountain'),
            'cdt': pytz.timezone('US/Mountain'),
            'est': pytz.timezone('US/Eastern'),
            'edt': pytz.timezone('US/Eastern'),
            'gmt': pytz.timezone('GMT'),
            'bst': pytz.timezone('Europe/London'),
            'utc': pytz.timezone('UTC'),
            'cest': pytz.timezone('Europe/Brussels')}
        self.morning_check = True

    async def on_message(self, message):
        artemis = self.client.user
        channel = message.channel
        contents_lower = message.content.lower()

        if contents_lower.startswith('{0.mention}'.format(artemis)):
            contents_lower = contents_lower.split()

            # natural language for creating an event
            # general format:
            # @artemis make an event for [date] at [time] called [event name]
            # @artemis delete [event_id]
            try:
                create = ['create', 'make', 'set']
                if any(value in create for value in contents_lower[1:]):
                    await self.create_an_event(message)
                delete = ['delete', 'remove']
                if any(value in delete for value in contents_lower[1:]):
                    await self.delete_an_event(message)

            except IndexError:
                await channel.send('Hm?')

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
            if value in content and message.author.id != self.client.user.id and self.morning_check:
                morning_response = ['Good morning!', 'Mornin!']
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

    async def create_an_event(self, message):
        contents_split = message.content.lower().split()
        msg = contents_split[1:]

        def check(m):
            return m.author == message.author and m.channel == message.channel
        try:
            time = [value for value in msg if ':' in value]
            time = time[0]
        except IndexError:
            await message.channel.send('What time is the event at?')
            time = await self.client.wait_for('message', check=check)
            time = time.content
        try:
            date = [value for value in msg if '/' in value]
            date = date[0]
        except IndexError:
            await message.channel.send('What date is the event for?')
            date = await self.client.wait_for('message', check=check)
            date = date.content

        replaced_time = time.replace('am', '').replace('pm', '')
        hours, minutes = replaced_time.split(':')
        if int(hours) < 12 and 'pm' in msg or 'pm' in time:
            hours = int(hours) + 12
        # attempt tomorrow, today, days of week, month names
        try:
            day, month, year = date.split('/')
        except ValueError:
            day, month = date.split('/')
            year = datetime.utcnow().year - 2000

        if any(tz in self.popular_zones for tz in msg):
            tz = [tz for tz in self.popular_zones if tz in msg]
            tz = tz[0]
        else:
            tz = 'utc'

        datetime_object = await self.time_formatter(message, day, month, year, hours, minutes, tz)
        dt_string_date, dt_string_time, dt_long, dt_short = await self.make_string(datetime_object)
        called_list = ['called', 'titled']

        if any(True for value in called_list if value in msg) is True:
            try:
                called_index = msg.index('called')
            except ValueError:
                called_index = msg.index('titled')
            contents = message.content.split()
            msg = contents[2:]
            event = ' '.join(msg[called_index:])
        else:
            await message.channel.send('What is the event called?')
            event = await self.client.wait_for('message', check=check)
            event = event.content

        conn, c = load_db()
        c.execute("SELECT * FROM events")
        event_ids = [value[0] for value in c.fetchall()]
        while True:
            event_id = random.randint(1, 99999)
            if event_id not in event_ids:
                with conn:
                    c.execute("INSERT INTO events VALUES (:id, :title, :datetime, :creator_id, :guild_id)",
                              {'id': event_id, 'title': event, 'datetime': dt_long, 'creator_id': message.author.id,
                               'guild_id': message.guild.id})
                    break
        await message.channel.send(
            'Making an event for {} at {} {} titled *{}*.\n'
            'The event has been assigned the id **{}**.'.format(dt_string_date, dt_string_time, tz.upper(), event,
                                                                event_id))

    @staticmethod
    async def delete_an_event(message):
        contents_lower = message.content.lower().split()
        msg = contents_lower[1:]

        conn, c = await load_db()
        try:
            c.execute("SELECT * FROM events WHERE guild_id = (:guild_id)", {'guild_id': message.guild.id})
            events = c.fetchall()
            for event in events:
                event_id, title, dt, creator_id, guild_id = event
                if event_id in msg and creator_id == message.author.id:
                    with conn:
                        c.execute("DELETE row FROM events WHERE id = (:id)", {'id': event_id})
                    await message.channel.send('Event **{}**: *{}* has been deleted!'.format(event_id, title))
                elif event_id in msg and creator_id != message.author.id:
                    await message.channel.send('You are not the event\'s original author.')
        except Exception as e:
            print('Chat_core (delete_an_event):', e)
        await message.channel.send('Sorry, I couldn\'t find that event.')

    async def time_formatter(self, message, day, month, year, h, m, tz):
        # takes hours and minutes and formats it to a datetime with UTC tz
        tz = self.popular_zones[tz]
        try:
            d = datetime.now
            dt = datetime(year=int('20{}'.format(year)),
                          month=int(month),
                          day=int(day),
                          hour=int(h),
                          minute=int(m),
                          second=d().second,
                          microsecond=d().microsecond,
                          tzinfo=pytz.UTC)
            dt = dt.replace(tzinfo=tz)
            return dt
        except ValueError as e:
            print('An improper datetime was passed.', e)
            await message.channel.send('An incorrect datetime was passed: {}'.format(e))
            return
        except TypeError as e:
            print('Make datetime', e)
            await message.channel.send('An incorrect datetime was passed: {}'.format(e))
            return

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
        # print('Artemis emotional level change: {0}'.format(level))

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

    @staticmethod
    async def make_string(datetime_object):
        if type(datetime_object) != datetime:
            print('Not a datetime object')
            return datetime_object
        else:
            dt_full = datetime_object.strftime("%Y-%m-%d %H:%M:%S")
            dt_short = datetime_object.strftime('%H:%M UTC, %d/%b')
            datetime_string_date = datetime_object.strftime('%d/%m/%y')
            datetime_string_time = datetime_object.strftime('%H:%M')
            return datetime_string_date, datetime_string_time, dt_full, dt_short


def setup(client):
    client.add_cog(Chat(client))
    client.loop.create_task(Chat(client).change_status())
