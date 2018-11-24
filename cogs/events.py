""" All times in events are handled as UTC and then converted to set zone times for local reference """

import asyncio
import typing
import discord
import pytz
import random
from artemis import load_db
from collections import OrderedDict
from discord.ext import commands
from discord.ext.commands import BucketType, CommandNotFound
from _datetime import datetime, timedelta


class Events:
    def __init__(self, client):
        self.client = client
        self.pop_zones = {
            'pst': pytz.timezone('US/Alaska'),
            'pdt': pytz.timezone('US/Alaska'),
            'cst': pytz.timezone('US/Mountain'),
            'cdt': pytz.timezone('US/Mountain'),
            'est': pytz.timezone('US/Eastern'),
            'edt': pytz.timezone('US/Eastern'),
            'gmt': pytz.timezone('GMT'),
            'bst': pytz.timezone('Europe/London'),
            'utc': pytz.timezone('UTC'),
            'ist': pytz.timezone('Asia/Calcutta'),
            'cest': pytz.timezone('Europe/Brussels'),
            'aest': pytz.timezone('Australia/Brisbane'),
            'aedt': pytz.timezone('Australia/Melbourne')
        }
        self.moderators = ['mod', 'moderator', 'moderators', 'admin', 'administrator', 'sparkle, sparkle!']

    @commands.group(aliases=['event', 'e'])
    @commands.cooldown(rate=2, per=5, type=BucketType.user)
    async def events(self, ctx):
        if ctx.invoked_subcommand is None:
            conn, c = await load_db()

            # set embed
            embed = discord.Embed(color=discord.Color.blue())
            embed.add_field(name=':sparkles: Upcoming Events', value='\u200b')
            thumb_url = await self.get_thumb(ctx.guild.id)
            embed.set_thumbnail(url=thumb_url)
            embed.set_footer(text='Use notify event_id to receive event notifications')

            c.execute("SELECT * FROM events WHERE guild_id = (:guild_id) ORDER BY datetime", {'guild_id': ctx.guild.id})
            events = c.fetchall()
            counter = 1
            for values in events:
                diamond = ':small_orange_diamond:'
                if counter % 2 == 0:
                    diamond = ':small_blue_diamond:'
                event_id, title, dt, creator_id, guild_id = values
                dt = await self.make_datetime(dt)
                dt_long, dt_short = await self.make_string(dt)
                eta = await self.eta(dt)
                fmt = (dt_short, eta, event_id)

                embed.add_field(name='{0} {1}'.format(diamond, title),
                                value='**Time**: {0}\n**ETA**: {1}\n**ID**: {2}'.format(*fmt),
                                inline=False)
                counter += 1
            await ctx.send(embed=embed)

    @events.group(aliases=['d', 'remove'])
    async def delete(self, ctx, *args):
        if len(args) < 1:
            await ctx.send('Use `event delete event_id1 event_id2` to delete an event or events.')
            return

        try:
            event_list = [int(value) for value in args]
        except ValueError:
            await ctx.send('Please check your event ID(s).')
            return
        embed = discord.Embed(color=discord.Color.blue())

        conn, c = await load_db()
        for event_id in event_list:
            c.execute("SELECT EXISTS(SELECT 1 FROM events WHERE id = (:id) AND guild_id = (:guild_id))",
                      {'id': event_id, 'guild_id': ctx.guild.id})

            # if event is in the database allow modifications or else warn the user that the event does not exist
            if 1 in c.fetchone():
                with conn:
                    c.execute("SELECT * FROM events WHERE id = (:id) AND guild_id = (:guild_id)",
                              {'id': event_id, 'guild_id': ctx.guild.id})
                    event_id, title, dt, creator_id, guild_id = c.fetchone()

                    mod_roles = [x.lower() for x in self.moderators]
                    author_roles = [role.name.lower() for role in ctx.author.roles]

                    # check user roles
                    if any(value in mod_roles for value in author_roles):
                        c.execute("DELETE FROM events WHERE id = (:id) AND guild_id = (:guild_id)",
                                  {'id': event_id, 'guild_id': ctx.guild.id})
                        embed.add_field(name='Event Deleted',
                                        value='"{}" successfully deleted.'.format(title),
                                        inline=False)
                    elif ctx.author.id == creator_id:
                        c.execute(
                            """DELETE FROM events WHERE id = (:id) 
                            AND guild_id = (:guild_id) 
                            AND creator_id = (:creator_id)""",
                            {'id': event_id, 'guild_id': ctx.guild.id, 'creator_id': ctx.author.id}
                        )
                        embed.add_field(name='Event Deleted',
                                        value='"{}" successfully deleted.'.format(title),
                                        inline=False)
                    else:
                        await ctx.send('You cannot delete an event you did not create!')
            else:
                embed.add_field(name='{} Not Found'.format(event_id), value='\u200b', inline=False)
            await ctx.send(embed=embed)

    @events.group(aliases=['f'])
    async def find(self, ctx, *, keyword: str):
        conn, c = await load_db()
        keyword = '%{}%'.format(keyword.lower())

        # set embed
        embed = discord.Embed(color=discord.Color.blue())
        embed.add_field(name=':sparkles: Found Events', value='\u200b')
        embed.set_footer(text='Use notify event_id to receive event notifications')
        thumb_url = await self.get_thumb(ctx.guild.id)
        embed.set_thumbnail(url=thumb_url)

        c.execute("SELECT * FROM events WHERE guild_id = (:guild_id) AND title LIKE (:keyword) ORDER BY datetime",
                  {'guild_id': ctx.guild.id, 'keyword': keyword})
        events = c.fetchall()
        if len(events) < 1:
            await ctx.send('Sorry, no events with that keyword were found.')
            return
        for value in events:
            event_id, title, dt, creator_id, guild_id = value
            dt = await self.make_datetime(dt)
            dt_long, dt_short = await self.make_string(dt)
            eta = await self.eta(dt)
            fmt = (event_id, dt_short, eta)
            embed.add_field(name=title,
                            value='**Event ID**: {0}\n**Time**: {1}\n**ETA**: {2}'.format(*fmt),
                            inline=False)
        await ctx.send(embed=embed)

    @events.group(aliases=['t'])
    async def timer(self, ctx, hours: int, minutes: int, *, event: str):
        conn, c = await load_db()

        # format !events timer h m "event"
        dt = datetime.utcnow()
        td = timedelta(hours=hours, minutes=minutes)
        dt = dt + td

        while True:
            event_id = random.randint(1, 99999)
            event_exists = await self.check_if_event_exists(event_id)
            if not event_exists:
                dt_long, dt_short = await self.make_string(dt)
                with conn:
                    c.execute("INSERT INTO events VALUES(:id, :title, :datetime, :creator_id, :guild_id)",
                              {'id': event_id, 'title': event, 'datetime': dt_long, 'creator_id': ctx.author.id,
                               'guild_id': ctx.guild.id})
                embed = await self.embed_handler(ctx, dt, event, event_id, update=False)
                await ctx.send(embed=embed)
                fmt = (ctx.message.author, event, event_id, dt_long)
                msg = 'An event was created by {0}.\n{1} [{2}]\n{3}'.format(*fmt)
                await self.spam(ctx, msg)

    @events.group(aliases=['add', 'a'])
    async def set(self, ctx, *args):
        if len(args) < 2:
            await ctx.send('Please use the format `setevent h:m day/mnth event`.')
            return

        h, m = args[0].split(':')
        event = ' '.join(args[2:])
        try:
            day, month, year = args[1].split('/')
            utc_year = datetime.utcnow().year
            if (2000 + int(year)) - utc_year < 0:
                await ctx.send('You cannot have a date that\'s already passed.')
                return
            if int(month) < datetime.utcnow().month:
                await ctx.send('You cannot have a date that\'s already passed.')
                return
            if int(month) == datetime.utcnow().month and int(day) < datetime.utcnow().day:
                await ctx.send('You cannot have a date that\'s already passed.')
                return
        except ValueError:
            day, month = args[1].split('/')
            utc_year = datetime.utcnow().year
            year = utc_year - 2000

        # format the time to be timezone ready
        dt = await self.time_formatter(ctx, day, month, year, h, m)
        if dt is None:
            return
        dt_long, dt_short = await self.make_string(dt)

        # generate the event with a unique ID
        conn, c = await load_db()
        c.execute("SELECT * FROM events")
        event_values = c.fetchall()
        event_ids = [value[0] for value in event_values]
        while True:
            event_id = random.randint(1, 99999)
            if event_id not in event_ids:
                with conn:
                    c.execute("INSERT INTO events VALUES (:id, :title, :datetime, :creator_id, :guild_id)",
                              {'id': event_id, 'title': event, 'datetime': dt_long, 'creator_id': ctx.author.id,
                               'guild_id': ctx.guild.id})
                    break
        embed = await self.embed_handler(ctx, dt, event, event_id, update=False)
        await ctx.send(embed=embed)
        msg = 'An event was created by {0}.\n{1} [{2}]\n{3}'.format(ctx.message.author, event, event_id, dt_long)
        await self.spam(ctx, msg)

    @events.group(aliases=['u'])
    async def update(self, ctx, *args):
        if 1 > len(args):
            await ctx.send('Please use the format `update event_id h:m day/mnth`.')
            return
        try:
            event_id = str(args[0])
            h, m = args[1].split(':')
            try:
                day, month, year = args[2].split('/')
            except ValueError:
                day, month = args[2].split('/')
                year = datetime.utcnow().year - 2000

            dt = await self.time_formatter(ctx, day, month, year, h, m)
            conn, c = await load_db()

            c.execute("SELECT * FROM events WHERE id = (:id) AND guild_id = (:guild_id)",
                      {'id': event_id, 'guild_id': ctx.guild.id})
            event_id, title, event_time, creator_id, guild_id = c.fetchone()
            dt_long, dt_short = await self.make_string(dt)
            with conn:
                c.execute("UPDATE events SET datetime = (:datetime) WHERE id = (:id)",
                          {'datetime': dt_long, 'id': event_id})
            embed = await self.embed_handler(ctx, dt, title, event_id, update=True)
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send('Please use the format `update event_id h:m day/mnth`.')
            print(e)
            raise

    # @commands.command(aliases=['local'])
    # async def mytime(self, ctx, event_id: str, tz: str):
    #     await ctx.send('This command is not functioning at the moment.')

    #     guild = ctx.guild
    #     author = ctx.author
    #
    #     # set the thumbnail
    #     thumb_url = guild.icon_url
    #     if guild.icon_url is '':
    #         thumb_url = self.client.user.avatar_url
    #
    #     # set embed
    #     title = '──────────────── [Events] ────────────────'
    #     color = discord.Color.blue()
    #     footer_style = int((39 - len(author.name)) / 2) * '─'
    #     fmt_footer = footer_style + '[Created by: {0}]'.format(author.name) + footer_style
    #
    #     # create embed
    #     embed = discord.Embed(title=title, color=color)
    #     embed.set_thumbnail(url=thumb_url)
    #     embed.set_footer(text=fmt_footer)
    #
    #     try:
    #         # find events in data that match the current guild
    #         data = await load_json('events')
    #         if event_id in data:
    #             # Format the event's time
    #             dt = await self.make_datetime(data[event_id]['time'])
    #             verify, tz_conversion = await self.timezones(tz)
    #
    #             # Convert the time with set tz
    #             new_dt = dt.astimezone(tz_conversion)
    #             dt = dt + datetime.utcoffset(new_dt)
    #
    #             # Make the datetime object a string and format it
    #             dt_long, dt_short = await self.make_string(dt)
    #             dt_short = dt_short.replace('UTC', '')
    #
    #             embed.add_field(
    #                 name='{}'.format(data[event_id]['event'][:50]),
    #                 value='This event in {0} is {1}'.format(tz.upper(), dt_short)
    #             )
    #             await ctx.send(embed=embed)
    #         else:
    #             await ctx.send('Event id {} was not found.'.format(event_id))
    #     except TypeError:
    #         await ctx.send('That didn\'t work. Make sure that your command matches the required format.')

    @commands.command()
    @commands.cooldown(rate=1, per=30, type=BucketType.user)
    async def time(self, ctx):
        times = {
            1: ['pst', datetime.now(pytz.timezone('US/Alaska'))],
            2: ['cst', datetime.now(pytz.timezone('US/Mountain'))],
            3: ['est', datetime.now(pytz.timezone('US/Eastern'))],
            4: ['utc', datetime.now(pytz.timezone('GMT'))],
            5: ['bst', datetime.now(pytz.timezone('Europe/London'))],
            6: ['cet', datetime.now(pytz.timezone('Europe/Brussels'))],
            7: ['ist', datetime.now(pytz.timezone('Asia/Calcutta'))],
            8: ['awst', datetime.now(pytz.timezone('Australia/Perth'))],
            9: ['acst', datetime.now(pytz.timezone('Australia/Darwin'))],
            10: ['aest', datetime.now(pytz.timezone('Australia/Brisbane'))],
            11: ['aedt', datetime.now(pytz.timezone('Australia/Melbourne'))]
        }
        embed = discord.Embed(
            title='Popular Timezones',
            color=discord.Color.blue())
        sorted_zones = OrderedDict(sorted(times.items(), key=lambda x: x[0]))
        desc = []
        for key, value in sorted_zones.items():
            if int(key) < 4:
                fmt = '{} ─ {}'.format(value[1].strftime('%H:%M'), value[0].upper())
                desc.append(fmt)
        embed.add_field(name='America', value='\n'.join(value for value in desc), inline=False)
        desc = []
        for key, value in sorted_zones.items():
            if 3 < int(key) < 7:
                fmt = '{} ─ {}'.format(value[1].strftime('%H:%M'), value[0].upper())
                desc.append(fmt)
        embed.add_field(name='Europe', value='\n'.join(value for value in desc), inline=False)
        desc = []
        for key, value in sorted_zones.items():
            if int(key) == 7:
                fmt = '{} ─ {}'.format(value[1].strftime('%H:%M'), value[0].upper())
                desc.append(fmt)
        embed.add_field(name='India', value='\n'.join(value for value in desc), inline=False)
        desc = []
        for key, value in sorted_zones.items():
            if 7 < int(key) < 12:
                fmt = '{} ─ {}'.format(value[1].strftime('%H:%M'), value[0].upper())
                desc.append(fmt)
        embed.add_field(name='Australia', value='\n'.join(value for value in desc), inline=False)
        await ctx.send(embed=embed)

    @commands.command()
    async def bottles(self, ctx, amount: typing.Optional[int] = 99, *, liquid="beer"):
        await ctx.send('{} bottles of {} on the wall!'.format(amount, liquid))
        # print('{} bottles of {} on the wall!'.format(amount, liquid))

    @commands.command()
    @commands.cooldown(rate=3, per=10, type=BucketType.user)
    async def notify(self, ctx, eid=None, channel_name=None, timer=60):
        conn, c = await load_db()
        # display all notifications for author
        if eid is None:
            notifications = []
            c.execute("SELECT * FROM event_notify WHERE member_id = (:member_id) AND guild_id = (:guild_id)",
                      {'member_id': ctx.author.id, 'guild_id': ctx.guild.id})
            events = c.fetchall()
            for event in events:
                event_id, member_id, guild_id, channel_id, dt, title, timer = event
                channel = discord.utils.get(ctx.guild.channels, id=channel_id)
                c.execute("SELECT * FROM events WHERE id = (:id)", {'id': event_id})
                event_id, title, dt, creator_id, guild_id = c.fetchone()
                fmt = (title, event_id, channel, dt, timer)
                notifications.append('Title: *{}*\nID: *{}*\nChannel: {}\nEvent Time: {}\nAlert: {} min\n'.format(*fmt))
            if len(notifications) > 0:
                embed = discord.Embed(title='Events you have notifications set for:',
                                      description='\n'.join(notifications),
                                      color=discord.Color.blue())
            else:
                embed = discord.Embed(title='You do not have any notifications set.', color=discord.Color.blue())
            await ctx.send(embed=embed)
            return

        # if no channel is passed
        if channel_name == 'remove':
            await self.remove_event(ctx, eid)
            return
        elif channel_name is None:
            channel_name = ctx.channel.name
        else:
            # if the user omits a channel but declares a timer
            # check by attempting to convert the channel name to an integer
            try:
                timer = int(channel_name)
                channel_name = ctx.channel.name
            except ValueError:
                pass
        channel = discord.utils.get(ctx.guild.channels, name=channel_name)
        cid = channel.id

        event_exists = await self.check_if_event_exists(eid)
        if not event_exists:
            msg = 'Event ID {} not found.'.format(eid)
            embed = discord.Embed(title=msg, color=discord.Color.dark_purple())
            await ctx.send(embed=embed)
            return
        else:
            # check if event exists
            c.execute("SELECT * FROM events WHERE id = (:id) AND guild_id = (:guild_id)",
                      {'id': eid, 'guild_id': ctx.guild.id})
            event_id, title, dt, creator_id, guild_id = c.fetchone()
            # check if notification exists
            c.execute("""SELECT EXISTS(SELECT 1 
                        FROM event_notify 
                        WHERE event_id = (:event_id) 
                        AND member_id = (:member_id)
                        AND guild_id = (:guild_id))""",
                      {'event_id': event_id, 'member_id': ctx.author.id, 'guild_id': ctx.guild.id})
            if 1 in c.fetchone():
                c.execute("""SELECT EXISTS(SELECT 1 
                            FROM event_notify 
                            WHERE event_id = (:event_id) 
                            AND channel_id = (:channel_id) 
                            AND timer = (:timer))""",
                          {'event_id': event_id, 'channel_id': cid, 'timer': timer})
                if 1 in c.fetchone():
                    msg = 'This notification already exists.'
                else:
                    with conn:
                        c.execute("""UPDATE event_notify 
                                    SET channel_id = (:channel_id), timer = (:timer) 
                                    WHERE event_id = (:event_id)""",
                                  {'channel_id': cid, 'timer': timer, 'event_id': event_id})
                        fmt = (ctx.author.name, channel, title, timer)
                        msg = 'OK! I\'ll notify {0} in {1.mention} when "__{2}__" is {3} minutes away from ' \
                              'starting!'.format(*fmt)
            else:
                with conn:
                    c.execute("""INSERT INTO event_notify 
                                VALUES(:event_id, :member_id, :guild_id, :channel_id, :datetime, :title, :timer)""",
                              {'event_id': event_id,
                               'member_id': ctx.author.id,
                               'guild_id': guild_id,
                               'channel_id': cid,
                               'datetime': dt,
                               'title': title,
                               'timer': timer})
                    fmt = (ctx.author.name, channel, title, timer)
                    msg = 'OK! I\'ll notify {0} in {1.mention} when "__{2}__" is {3} minutes away from ' \
                          'starting!'.format(*fmt)
            embed = discord.Embed(title='Notification Update', color=discord.Color.dark_purple(), description=msg)
            await ctx.send(embed=embed)
            return

    async def remove_event(self, ctx, eid):
        conn, c = await load_db()

        event_exists = await self.check_if_event_exists(eid)
        if event_exists:
            c.execute("SELECT * FROM events WHERE id = (:id) AND guild_id = (:guild_id)",
                      {'id': eid, 'guild_id': ctx.guild.id})
            event_id, title, dt, creator_id, guild_id = c.fetchone()
            with conn:
                c.execute("DELETE FROM event_notify WHERE event_id = (:event_id) AND member_id = (:member_id)",
                          {'event_id': eid, 'member_id': ctx.author.id})
            fmt = (title, ctx.author.name)
            msg = 'Notification for "{}" has been removed for {}'.format(*fmt)
            embed = discord.Embed(title='Notification Update', color=discord.Color.dark_purple(), description=msg)
            await ctx.send(embed=embed, delete_after=10)
        else:
            msg = 'Event ID {} not found.'.format(eid)
            embed = discord.Embed(title=msg, color=discord.Color.dark_purple())
            await ctx.send(embed=embed, delete_after=5)
            return

    @staticmethod
    async def time_formatter(ctx, day, month, year, h, m):
        # takes hours and minutes and formats it to a datetime with UTC tz
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
            return dt
        except ValueError as e:
            print('An improper datetime was passed.', e)
            await ctx.send('An incorrect datetime was passed: {}\n'
                           'Use the format `event add h:m day/mnth/year event`'.format(e))
            return None

    async def embed_handler(self, ctx, dt, event, event_id, update):
        conn, c = await load_db()

        # get two times
        dt_long, dt_short = await self.make_string(dt)

        # set the thumbnail
        thumb_url = await self.get_thumb(ctx.guild.id)

        # set the event title
        event_title = ':sparkles: New Event Added'
        if update:
            event_title = ':sparkles: Event Updated'

        # create embed
        embed = discord.Embed(color=discord.Color.blue())
        embed.add_field(name=event_title, value='\u200b')
        embed.set_thumbnail(url=thumb_url)
        embed.set_footer(text='Use notify event_id to receive event notifications')

        if update:
            event_exists = await self.check_if_event_exists(event_id)
            if event_exists:
                c.execute("SELECT * FROM events WHERE id = (:id)", {'id': event_id})
                event_id, title, dt, creator_id, guild_id = c.fetchone()
                dt = await self.make_datetime(dt)
                dt_data_long, dt_data_short = await self.make_string(dt)
                new_dt_data = await self.make_datetime(dt_long)
                eta = await self.eta(new_dt_data)

                embed.add_field(
                    name=event,
                    value='**ID** {0}\n'
                          '**Time**: {1} **──>** {2}\n'
                          '**ETA**: {3}'.format(event_id, dt_data_short, dt_short, eta),
                    inline=False)
                return embed
        dt = await self.make_datetime(dt_long)
        eta = await self.eta(dt)
        embed.add_field(
            name=event,
            value='**ID** {0}\n'
                  '**Time**: {1}\n'
                  '**ETA**: {2}'.format(event_id, dt_short, eta),
            inline=False)
        return embed

    @staticmethod
    async def eta(dt):
        # dt must be a datetime object
        td = dt - datetime.utcnow()
        days = td.days
        hours, remainder = divmod(td.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        if days < 0:
            eta = '{0}d {1}h {2}m'.format(0, 0, 0)
            return eta
        eta = '{0}d {1}h {2}m'.format(days, hours, minutes)
        return eta

    @staticmethod
    async def make_datetime(datetime_string):
        if type(datetime_string) != str:
            print('Not a string')
            return datetime_string
        else:
            datetime_object_full = datetime.strptime(datetime_string, '%Y-%m-%d %H:%M:%S')
            datetime_object_full.replace(tzinfo=pytz.UTC)
            return datetime_object_full

    @staticmethod
    async def make_string(datetime_object):
        if type(datetime_object) != datetime:
            print('Not a datetime object')
            return datetime_object
        else:
            datetime_string_full = datetime_object.strftime("%Y-%m-%d %H:%M:%S")
            datetime_string_short = datetime_object.strftime('%H:%M UTC, %d/%b')
            return datetime_string_full, datetime_string_short

    async def timezones(self, tz):
        tz = tz.lower()
        if tz in self.pop_zones:
            return True, self.pop_zones[tz]
        else:
            return False

    async def check_notifier(self):
        await self.client.wait_until_ready()
        while not self.client.is_closed():
            conn, c = await load_db()
            await asyncio.sleep(60)

            c.execute("SELECT * FROM event_notify")
            events = c.fetchall()
            for event in events:
                event_id, member_id, guild_id, channel_id, dt, title, timer = event
                dt = await Events.make_datetime(dt)
                eta = await Events.eta(dt)
                days, hours, minutes = eta.split()
                days = int(days.strip('d'))
                hours = int(hours.strip('h'))
                minutes = int(minutes.strip('m'))
                total_hours_in_minutes = hours * 60
                total_minutes_in_days = days * 24 * 60
                total_time_left = total_hours_in_minutes + total_minutes_in_days + minutes
                if total_time_left < timer:
                    user = await self.client.get_user_info(user_id=member_id)
                    channel = self.client.get_channel(channel_id)
                    msg = '{0}: **{1}** is starting in less than {2} minutes!'.format(user.mention, title, timer)
                    await channel.send(msg)
                    with conn:
                        c.execute("DELETE FROM event_notify WHERE event_id = (:event_id) AND guild_id = (:guild_id)",
                                  {'event_id': event_id, 'guild_id': guild_id})

    async def spam(self, ctx, message):
        conn, c = await load_db()
        c.execute("SELECT * FROM guilds where id = (:id)", {'id': ctx.guild.id})
        guild_id, guild_name, mod_role, autorole, prefix, spam, thumbnail = c.fetchone()
        if spam is not None:
            embed = discord.Embed(title='Alert', description=message, color=discord.Color.blue())
            channel = self.client.get_channel(spam)
            await channel.send(embed=embed)

    @staticmethod
    async def check_if_event_exists(event_id):
        conn, c = await load_db()
        c.execute("SELECT EXISTS(SELECT 1 FROM events WHERE id = (:id))", {'id': event_id})
        return_value = False
        if 1 in c.fetchone():
            return_value = True
        return return_value

    async def get_thumb(self, gid):
        conn, c = await load_db()
        thumb_url = self.client.user.avatar_url
        c.execute("SELECT thumbnail FROM guilds WHERE id = (:id)", {'id': gid})
        thumb = c.fetchone()[0]
        if thumb is not None:
            thumb_url = thumb
        return thumb_url

    @events.error
    @notify.error
    # @mytime.error
    async def on_message_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            msg = ':sob: You\'ve triggered a cool down. Please try again in {} sec.'.format(
                int(error.retry_after))
            await ctx.send(msg)
        if isinstance(error, commands.CheckFailure):
            msg = 'You do not have permission to run this command.'
            await ctx.send(msg)
        if isinstance(error, CommandNotFound):
            msg = 'Did you mean to try another command?'
            await ctx.send(msg)


def setup(client):
    client.add_cog(Events(client))
    client.loop.create_task(Events(client).check_notifier())
