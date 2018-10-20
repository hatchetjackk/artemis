import asyncio
import discord
from _datetime import datetime
import pytz
import json
import random
from discord.ext import commands
from discord.ext.commands import BucketType

""" All times in events are handled as UTC and then converted to set zone times for local reference """


class Events:
    def __init__(self, client):
        self.client = client
        self.tz_dict = {
            'pst/pdt': datetime.now(pytz.timezone('US/Alaska')),
            'cst/cdt': datetime.now(pytz.timezone('US/Mountain')),
            'est/edt': datetime.now(pytz.timezone('US/Eastern')),
            'utc/gmt': datetime.now(pytz.timezone('GMT')),
            'bst': datetime.now(pytz.timezone('Europe/London')),
            'cest': datetime.now(pytz.timezone('Europe/Brussels'))
        }
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
            'cest': pytz.timezone('Europe/Brussels')}

    @commands.command()
    @commands.cooldown(rate=2, per=30, type=BucketType.user)
    async def setevent(self, ctx, *args):
        guild = ctx.guild
        author = ctx.author

        if len(args) < 2:
            await ctx.send('Please use the format ``setevent <h:m> <day/mnth> <event>``.')
            return

        h, m = args[0].split(':')
        day, month = args[1].split('/')
        event = ' '.join(args[2:])

        # format the time to be timezone ready
        dt = await self.time_formatter(ctx, day, month, h, m)
        if dt is None:
            return

        data = await self.load_events()

        # generate the event with a unique ID
        while True:
            event_id = random.randint(1, 99999)
            if event_id not in data:
                dt_long, dt_short = await self.make_string(dt)
                data[event_id] = {
                    'event': event,
                    'time': dt_long,
                    'user_id': author.id,
                    'guild_id': guild.id,
                    'notify': False,
                    'member_notify': {}
                }
                break

        await self.dump_events(data)

        embed = await self.embed_handler(ctx, dt, event, event_id, update=False)
        await ctx.send(embed=embed)

        msg = 'An event was created.\n{0} [{1}]\n{2}'.format(event, event_id, dt_long)
        await self.spam(ctx, msg)

    @commands.group()
    @commands.cooldown(rate=2, per=30, type=BucketType.user)
    async def delevent(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send('Use `delevent id event_id1 event_id2` to delete an event.')

    @delevent.group()
    async def id(self, ctx, *args):
        # delete specific events
        if len(args) < 1:
            await ctx.send('Use `delevent id event_id1 event_id2` to delete an event.')
            return
        event_list = args[:]
        data = await self.load_events()
        for event_id in event_list:
            if event_id in data:
                event = data[event_id]['event']
                data.pop(event_id)
                await self.dump_events(data)
                embed = discord.Embed(color=discord.Color.blue())
                embed.add_field(name='Event Deleted', value='{} successfully deleted.'.format(event_id))
                await ctx.send(embed=embed)
            else:
                await ctx.send('Event {} not found.'.format(event_id))
                return
            await asyncio.sleep(5)
            msg = 'An event was deleted.\n{0} [{1}]'.format(event, event_id)
            await self.spam(ctx, msg)

    @delevent.group()
    @commands.has_role('mod')
    async def all(self, ctx):
        # delete all events
        data = await self.load_events()
        while len(data) > 0:
            try:
                for event in data:
                    data.pop(event)
                    await self.dump_events(data)
            except RuntimeError:
                pass
        await ctx.send('All events deleted!')

    @commands.command()
    async def update(self, ctx, *args):

        if 1 > len(args) > 3:
            await ctx.send('Please use the format ``update <event id> <h:m> <day/mnth> ``.')
            return
        event_id = str(args[0])
        h, m = args[1].split(':')
        day, month = args[2].split('/')

        dt = await self.time_formatter(ctx, day, month, h, m)
        data = await self.load_events()
        if event_id in data:
            dt_long, dt_short = await self.make_string(dt)
            data[event_id]['time'] = dt_long
        else:
            await ctx.send('Event ID {} not found.'.format(event_id))
            return
        event = data[event_id]['event']
        embed = await self.embed_handler(ctx, dt, event, event_id, update=True)
        await ctx.send(embed=embed)
        await self.dump_events(data)

    @commands.command()
    async def events(self, ctx, *args):
        """ Return one or all events in events.json dependent on the guild id
        Method will check for args, and if none are passed, all events will be sent
        """
        guild = ctx.guild
        author = ctx.author
        gid = str(guild.id)

        if len(args) > 1:
            await ctx.send('Please use `events <event id>` to check a single event\n'
                           'or use `events` to check all events.')
            return

        # set the thumbnail
        with open('files/guilds.json') as f:
            thumbs = json.load(f)
        thumb_url = self.client.user.avatar_url
        if thumbs[gid]['thumb_url'] != '':
            thumb_url = thumbs[gid]['thumb_url']

        # set embed
        title = '──────────────── [Events] ────────────────'
        color = discord.Color.blue()
        footer_style = int((39 - len(author.name)) / 2) * '─'
        fmt_footer = footer_style + '[Created by: {0}]'.format(author.name) + footer_style

        # create embed
        embed = discord.Embed(title=title, color=color)
        embed.set_thumbnail(url=thumb_url)
        embed.set_footer(text=fmt_footer)
        embed.add_field(name=':sparkles: Upcoming Events', value='\u200b')

        # create variables
        event_id = False
        try:
            event_id = str(args[0])
        except IndexError:
            pass

        data = await self.load_events()
        # Ensure that the event matches the guild
        # Then return a single event
        if event_id in data and data[event_id]['guild_id'] == guild.id:
            print(data[event_id]['guild_id'])
            print(guild.id)
            event = data[event_id]['event'][:50]
            dt = await self.make_datetime(data[event_id]['time'])
            dt_long, dt_short = await self.make_string(dt)
            embed.add_field(name=event, value='**Event** [{0}]: {1}\n'
                                              '**Time**: {2}'.format(event_id, event, dt_short), inline=False)
            await ctx.send(embed=embed)
            return

        # If no arguments were passed, iterate through the events.json file
        # Return all events that match the guild id
        # todo sort events by eta
        elif not event_id:
            counter = 1
            for key, value in data.items():
                if value['guild_id'] == guild.id:
                    diamond = ':small_orange_diamond:'
                    if counter % 2 == 0:
                        diamond = ':small_blue_diamond:'
                    # trim long event names
                    event = value['event'][:50]

                    # format the event's time
                    dt = await self.make_datetime(value['time'])
                    dt_long, dt_short = await self.make_string(dt)
                    eta = await self.eta(dt)

                    embed.add_field(name='{0} {1}'.format(diamond, event),
                                    value='**Time**: {0}\n'
                                          '**ETA**: {1}\n'
                                          '**ID**: {2}'.format(dt_short, eta, key), inline=False)
                    counter += 1
            await ctx.send(embed=embed)

    @commands.command()
    async def mytime(self, ctx, *args):
        guild = ctx.guild
        author = ctx.author

        # set the thumbnail
        thumb_url = guild.icon_url
        if guild.icon_url is '':
            thumb_url = self.client.user.avatar_url

        # set embed
        title = '──────────────── [Events] ────────────────'
        color = discord.Color.blue()
        footer_style = int((39 - len(author.name)) / 2) * '─'
        fmt_footer = footer_style + '[Created by: {0}]'.format(author.name) + footer_style

        # create embed
        embed = discord.Embed(title=title, color=color)
        embed.set_thumbnail(url=thumb_url)
        embed.set_footer(text=fmt_footer)

        # Check if the right number of arguments have been passed
        try:
            event_id = args[0]
            tz = args[1]
        except IndexError:
            await ctx.send('Use `mytime <event id> <time zone>` to check an event in a specific timezone.')
            return

        # find events in data that match the current guild
        data = await self.load_events()
        if event_id in data:
            # Format the event's time
            dt = await self.make_datetime(data[event_id]['time'])
            verify, tz_conversion = await self.timezones(tz)

            # Convert the time with set tz
            new_dt = dt.astimezone(tz_conversion)
            dt = dt + datetime.utcoffset(new_dt)

            # Make the datetime object a string and format it
            dt_long, dt_short = await self.make_string(dt)
            dt_short = dt_short.replace('UTC', '')

            embed.add_field(name='{}'.format(data[event_id]['event'][:50]),
                            value='This event in {0} is {1}'.format(tz.upper(), dt_short))
            await ctx.send(embed=embed)
        else:
            await ctx.send('Event id {} was not found.'.format(event_id))

    @commands.command()
    async def time(self, ctx):
        # returns an embed with popular time zones
        zones = self.tz_dict
        embed = discord.Embed(title='──────────────── [ Time ] ────────────────', color=discord.Color.blue())
        embed.add_field(name='Zone', value='\n'.join([zone.upper() for zone in zones]), inline=True)
        embed.add_field(name='Time', value='\n'.join(zones[zone].strftime('%H:%M') for zone in zones))
        embed.set_footer(text='──────────────────────────────────────────')
        await ctx.send(embed=embed)

    @commands.command()
    async def notify(self, ctx, *args):
        # Allow a user to set a notification for an event
        # Notifier will alert the user one hour before the event in the channel they set the event in
        author = ctx.author
        event_id = str(args[0])

        data = await self.load_events()
        if event_id in data:
            if author.id not in data[event_id]['member_notify']:
                data[event_id]['notify'] = True
                data[event_id]['member_notify'].update({str(author.id): ctx.channel})
                await ctx.send('Set to notify **{author}** when *{event}* is 1 hour away from '
                               'starting!'.format(author=author.name, event=data[event_id]['event']))
                await self.dump_events(data)
                return
            # if user already exists in notification, remove the user
            if str(author.id) in data[event_id]['member_notify']:
                data[event_id]['member_notify'].pop(str(author.id), None)
                await ctx.send(
                    'Removing **{author}\'s** notification for *{event}*.'.format(author=author.name, event=data[event_id]['event'])
                )
                if len(data[event_id]['member_notify']) < 1:
                    data[event_id]['notify'] = False
                await self.dump_events(data)
                return

    @staticmethod
    async def time_formatter(ctx, day, month, h, m):
        # takes hours and minutes and formats it to a datetime with UTC tz
        try:
            d = datetime.now
            dt = datetime(year=d().year,
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
                           'Use the format `setevent <h:m> <day/mnth> <event>`'.format(e))
            return None

    async def embed_handler(self, ctx, dt, event, event_id, update):
        guild = ctx.guild
        author = ctx.author

        # get two times
        dt_long, dt_short = await self.make_string(dt)

        with open('files/guilds.json') as f:
            thumbs = json.load(f)
        # set the thumbnail
        if thumbs[str(guild.id)]['thumb_url'] != '':
            thumb_url = thumbs[guild.id]['thumb_url']
        else:
            thumb_url = self.client.user.avatar_url

        # set the event title
        event_title = ':sparkles: Upcoming Event'
        if update:
            event_title = ':sparkles: Event Updated'

        # set embed
        title = '──────────────── [Events] ────────────────'
        color = discord.Color.blue()
        footer_style = int((39 - len(author.name)) / 2) * '─'
        fmt_footer = footer_style + '[Created by: {0}]'.format(author.name) + footer_style

        # create embed
        embed = discord.Embed(title=title, color=color)
        embed.set_thumbnail(url=thumb_url)
        embed.set_footer(text=fmt_footer)

        if update:
            data = await self.load_events()
            if event_id in data:
                dt_data = data[event_id]['time']
                dt_data = await self.make_datetime(dt_data)
                dt_data_long, dt_data_short = await self.make_string(dt_data)
                new_dt_data = await self.make_datetime(dt_long)
                eta = await self.eta(new_dt_data)

                embed.add_field(name=event_title, value='**Event** [{0}]: {1}\n'
                                                        '**Time**: {2} **──>** {3}\n'
                                                        '**ETA**: {4}'.format(event_id, event, dt_data_short, dt_short, eta), inline=False)
                return embed
        dt = await self.make_datetime(dt_long)
        eta = await self.eta(dt)
        embed.add_field(name=event_title, value='**Event** [{0}]: {1}\n'
                                                '**Time**: {2}\n'
                                                '**ETA**: {3}'.format(event_id, event, dt_short, eta), inline=False)
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
            await asyncio.sleep(60 * 5)
            print('Checking notifier...')
            data_events = await Events.load_events()
            for key, value in data_events.items():
                if value['notify'] is True:
                    dt = await Events.make_datetime(value['time'])
                    eta = await Events.eta(dt)
                    days, hours, minutes = eta.split()
                    days = int(days.strip('d'))
                    hours = int(hours.strip('h'))
                    minutes = int(minutes.strip('m'))
                    print(days, hours, minutes)
                    if days < 1 and hours < 1 and minutes > 0:
                        for values in value['member_notify']:
                            for user, channel in values.items():
                                user = await self.client.get_user_info(user_id=user)
                                await self.client.send_message(
                                    self.client.get_channel(channel),
                                    '{0}: **{1}** is starting in less than 1 hour!'.format(user.mention, value['event'][:50]))
                        value['notify'] = False
                        value['member_notify'] = []
                    await Events.dump_events(data_events)

    async def spam(self, ctx, message):
        guild = ctx.guild
        author = ctx.author
        gid = str(guild.id)

        data = await self.load_guilds()
        if gid in data:
            if data[gid]['spam'] is not None:
                embed = discord.Embed(color=discord.Color.blue())
                embed.add_field(name='Alert', value=message)
                embed.set_footer(text='Triggered by: {0.name}'.format(author))
                channel = self.client.get_channel(int(data[gid]['spam']))
                await channel.send(embed=embed)

    @staticmethod
    async def create_user(member):
        with open('files/users.json', 'r') as f:
            data_users = json.load(f)
        if member.id not in data_users:
            data_users[member.id] = {
                'username': member.name,
                'guild': [],
                'karma': 0,
            }
        with open('files/users.json', 'w') as f:
            json.dump(data_users, f, indent=2)

    @staticmethod
    async def load_guilds():
        with open('files/guilds.json') as f:
            data = json.load(f)
        return data

    @staticmethod
    async def load_events():
        with open('files/events.json') as f:
            data = json.load(f)
        return data

    @staticmethod
    async def dump_events(data):
        with open('files/events.json', 'w') as f:
            json.dump(data, f, indent=2)

    @setevent.error
    @delevent.error
    async def on_message_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            msg = ':sob: You\'ve triggered a cool down. Please try again in {} sec.'.format(
                int(error.retry_after))
            await ctx.send(msg)


def setup(client):
    client.add_cog(Events(client))
    client.loop.create_task(Events(client).check_notifier())
