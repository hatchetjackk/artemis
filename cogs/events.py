import asyncio
import discord
import pytz
import json
import random
from collections import OrderedDict
from discord.ext import commands
from discord.ext.commands import BucketType, CommandNotFound
from _datetime import datetime, timedelta

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

    @commands.group(aliases=['event', 'e'])
    @commands.cooldown(rate=2, per=5, type=BucketType.user)
    async def events(self, ctx):
        if ctx.invoked_subcommand is None:
            data = await self.load_guilds()
            guild = ctx.guild
            author = ctx.author
            gid = str(guild.id)

            thumb_url = self.client.user.avatar_url
            if data[gid]['thumb_url'] != '':
                thumb_url = data[gid]['thumb_url']

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

            counter = 1
            data = await self.load_events()
            sorted_events = OrderedDict(sorted(data.items(), key=lambda x: x[1]['time']))
            for key, value in sorted_events.items():
                if value['guild_id'] == guild.id:
                    diamond = ':small_orange_diamond:'
                    if counter % 2 == 0:
                        diamond = ':small_blue_diamond:'
                    event = value['event'][:50]

                    dt = await self.make_datetime(value['time'])
                    dt_long, dt_short = await self.make_string(dt)
                    eta = await self.eta(dt)

                    embed.add_field(
                        name='{0} {1}'.format(diamond, event),
                        value='**Time**: {0}\n'
                              '**ETA**: {1}\n'
                              '**ID**: {2}'.format(dt_short, eta, key),
                        inline=False)
                    counter += 1
            await ctx.send(embed=embed)

    @events.group(aliases=['d'])
    async def delete(self, ctx, *args):
        message = ctx.message
        author = message.author
        guild = ctx.guild
        gid = guild.id

        if len(args) < 1:
            await ctx.send('Use `event delete event_id1 event_id2` to delete an event or events.')
            return
        event_list = args[:]
        data = await self.load_events()
        embed = discord.Embed(color=discord.Color.blue())
        for event_id in event_list:
            if event_id in data and data[event_id]['guild_id'] == gid:
                if ctx.author.id == data[event_id]['user_id'] or 'mod' in author.roles:
                    event = data[event_id]['event']
                    data.pop(event_id)
                    await self.dump_events(data)
                    embed.add_field(
                        name='Event Deleted',
                        value='{} successfully deleted.'.format(event_id)
                    )
                    msg = 'An event was deleted by {0}.\n{1} [{2}]'.format(author, event, event_id)
                    await self.spam(ctx, msg)
                    await ctx.send(embed=embed)
                else:
                    await ctx.send('You did not make this event. Only the author or a moderator can delete it.')
            else:
                await ctx.send('Event {} not found.'.format(event_id))
                return

    @events.group(aliases=['f'])
    async def find(self, ctx, *, event_title: str):
        event_title = event_title.lower()
        # find a single event in the events file if it is in the guild
        data_guilds = await self.load_guilds()
        guild = ctx.guild
        author = ctx.author
        gid = str(guild.id)

        thumb_url = self.client.user.avatar_url
        if data_guilds[gid]['thumb_url'] != '':
            thumb_url = data_guilds[gid]['thumb_url']

        # set embed
        title = '──────────────── [Events] ────────────────'
        color = discord.Color.blue()
        footer_style = int((39 - len(author.name)) / 2) * '─'
        fmt_footer = footer_style + '[Created by: {0}]'.format(author.name) + footer_style

        # create embed
        embed = discord.Embed(title=title, color=color)
        embed.set_thumbnail(url=thumb_url)
        embed.set_footer(text=fmt_footer)
        embed.add_field(
            name=':sparkles: Upcoming Events',
            value='\u200b'
        )

        # Ensure that the event matches the guild
        # Then return a single event
        data_events = await self.load_events()
        for key, value in data_events.items():
            if event_title in data_events[key]['event'].lower() and data_events[key]['guild_id'] == int(gid):
                event = data_events[key]['event'][:50]
                dt = await self.make_datetime(data_events[key]['time'])
                dt_long, dt_short = await self.make_string(dt)
                eta = await self.eta(dt)
                embed.add_field(
                    name=event,
                    value='**Event** [{0}]: {1}\n'
                          '**Time**: {2}\n'
                          '**ETA**: {3}'.format(key, event, dt_short, eta),
                    inline=False
                )
        await ctx.send(embed=embed)

    @events.group(aliases=['t'])
    async def timer(self, ctx, hours: int, minutes: int, *, event: str):
        data = await self.load_events()
        guild = ctx.guild
        author = ctx.author

        # format !events timer h m "event"
        dt = datetime.utcnow()
        td = timedelta(
            hours=hours,
            minutes=minutes
        )
        dt = dt + td
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
        embed = await self.embed_handler(
            ctx,
            dt,
            event,
            event_id,
            update=False
        )
        await ctx.send(embed=embed)
        msg = 'An event was created by {0}.\n{1} [{2}]\n{3}'.format(ctx.message.author, event, event_id, dt_long)
        await self.spam(ctx, msg)

    @events.group(aliases=['add', 'a'])
    async def set(self, ctx, *args):
        # set an event using a time (hours:minutes) and date {day/month)
        data = await self.load_events()
        guild = ctx.guild
        author = ctx.author

        if len(args) < 2:
            await ctx.send('Please use the format `setevent h:m day/mnth event`.')
            return

        h, m = args[0].split(':')
        event = ' '.join(args[2:])
        try:
            day, month, year = args[1].split('/')
        except ValueError:
            day, month = args[1].split('/')
            year = datetime.utcnow().year - 2000

        # format the time to be timezone ready
        dt = await self.time_formatter(ctx, day, month, year, h, m)
        if dt is None:
            return

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
        embed = await self.embed_handler(
            ctx,
            dt,
            event,
            event_id,
            update=False
        )
        await ctx.send(embed=embed)
        msg = 'An event was created by {0}.\n{1} [{2}]\n{3}'.format(ctx.message.author, event, event_id, dt_long)
        await self.spam(ctx, msg)

    @events.group(aliases=['u'])
    async def update(self, ctx, *args):
        if 1 > len(args) > 3:
            await ctx.send('Please use the format `update event_id h:m day/mnth`.')
            return
        try:
            event_id = str(args[0])
            h, m = args[1].split(':')
            day, month, year = args[2].split('/')

            dt = await self.time_formatter(ctx, day, month, year, h, m)
            data = await self.load_events()
            if event_id in data:
                dt_long, dt_short = await self.make_string(dt)
                data[event_id]['time'] = dt_long
            else:
                await ctx.send('Event ID {} not found.'.format(event_id))
                return
            event = data[event_id]['event']
            embed = await self.embed_handler(
                ctx,
                dt,
                event,
                event_id,
                update=True
            )
            await ctx.send(embed=embed)
            await self.dump_events(data)
        except Exception as e:
            await ctx.send('Please use the format `update event_id h:m day/mnth`.')
            print(e)

    @commands.command(aliases=['local'])
    async def mytime(self, ctx, event_id: str, tz: str):
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

        try:
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

                embed.add_field(
                    name='{}'.format(data[event_id]['event'][:50]),
                    value='This event in {0} is {1}'.format(tz.upper(), dt_short)
                )
                await ctx.send(embed=embed)
            else:
                await ctx.send('Event id {} was not found.'.format(event_id))
        except TypeError:
            await ctx.send('That didn\'t work. Make sure that your command matches the required format.')

    @commands.command()
    @commands.cooldown(rate=1, per=30, type=BucketType.user)
    async def time(self, ctx):
        # returns an embed with popular time zones
        zones = self.tz_dict
        embed = discord.Embed(
            title='──────────────── [ Time ] ────────────────',
            color=discord.Color.blue()
        )
        embed.add_field(
            name='Zone',
            value='\n'.join([zone.upper() for zone in zones]),
            inline=True
        )
        embed.add_field(
            name='Time',
            value='\n'.join(zones[zone].strftime('%H:%M') for zone in zones))
        embed.set_footer(text='──────────────────────────────────────────')
        await ctx.send(embed=embed)

    @commands.command()
    @commands.cooldown(rate=3, per=10, type=BucketType.user)
    async def notify(self, ctx, eid: str):
        # Allow a user to set a notification for an event
        # Notifier will alert the user one hour before the event in the channel they set the event in
        channel = ctx.channel
        cid = channel.id
        author = ctx.author
        aid = str(author.id)

        data = await self.load_events()
        if eid in data:
            if aid not in data[eid]['member_notify']:
                data[eid]['notify'] = True
                data[eid]['member_notify'].update({aid: cid})
                await ctx.send('Set to notify **{author}** when *{event}* is 1 hour away from '
                               'starting!'.format(author=author.name, event=data[eid]['event']))
                await self.dump_events(data)
                return
            # if user already exists in notification, remove the user
            if str(author.id) in data[eid]['member_notify']:
                data[eid]['member_notify'].pop(aid, None)
                await ctx.send('Removing **{author}\'s** notification for *{event}*.'.format(
                        author=author.name,
                        event=data[eid]['event']
                    )
                )
                if len(data[eid]['member_notify']) < 1:
                    data[eid]['notify'] = False
                await self.dump_events(data)
                return

    @staticmethod
    async def time_formatter(ctx, day, month, year, h, m):
        # takes hours and minutes and formats it to a datetime with UTC tz
        try:
            d = datetime.now
            dt = datetime(
                year=int('20{}'.format(year)),
                month=int(month),
                day=int(day),
                hour=int(h),
                minute=int(m),
                second=d().second,
                microsecond=d().microsecond,
                tzinfo=pytz.UTC
            )
            return dt
        except ValueError as e:
            print('An improper datetime was passed.', e)
            await ctx.send('An incorrect datetime was passed: {}\n'
                           'Use the format `event add h:m day/mnth/year event`'.format(e))
            return None

    async def embed_handler(self, ctx, dt, event, event_id, update):
        guild = ctx.guild
        gid = str(guild.id)
        author = ctx.author

        # get two times
        dt_long, dt_short = await self.make_string(dt)

        with open('files/guilds.json') as f:
            thumbs = json.load(f)
        # set the thumbnail
        if thumbs[gid]['thumb_url'] != '':
            thumb_url = thumbs[gid]['thumb_url']
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

                embed.add_field(
                    name=event_title,
                    value='**Event** [{0}]: {1}\n'
                          '**Time**: {2} **──>** {3}\n'
                          '**ETA**: {4}'.format(event_id, event, dt_data_short, dt_short, eta),
                    inline=False)
                return embed
        dt = await self.make_datetime(dt_long)
        eta = await self.eta(dt)
        embed.add_field(
            name=event_title,
            value='**Event** [{0}]: {1}\n'
                  '**Time**: {2}\n'
                  '**ETA**: {3}'.format(event_id, event, dt_short, eta),
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
            await asyncio.sleep(60 * 2)
            data_events = await self.load_events()
            for key, value in data_events.items():
                if value['notify'] is True:
                    dt = await Events.make_datetime(value['time'])
                    eta = await Events.eta(dt)
                    days, hours, minutes = eta.split()
                    days = int(days.strip('d'))
                    hours = int(hours.strip('h'))
                    minutes = int(minutes.strip('m'))
                    if days < 1 and hours < 1 and minutes > 0:
                        for user, channel in value['member_notify'].items():
                            user = await self.client.get_user_info(user_id=int(user))
                            channel = self.client.get_channel(channel)
                            await channel.send(
                                '{0}: **{1}** is starting in less than 1 hour!'.format(user.mention,
                                                                                       value['event'][:50]))
                        value['notify'] = False
                        value['member_notify'] = {}
                    await self.dump_events(data_events)

    async def spam(self, ctx, message):
        guild = ctx.guild
        author = ctx.author
        gid = str(guild.id)

        data = await self.load_guilds()
        if gid in data:
            if data[gid]['spam'] is not None:
                embed = discord.Embed(color=discord.Color.blue())
                embed.add_field(
                    name='Alert',
                    value=message
                )
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

    @staticmethod
    async def on_command_error(ctx, error):
        if isinstance(error, CommandNotFound):
            with open('files/status.json') as f:
                data = json.load(f)
            msg = data['bot']['error_response']
            await ctx.send(random.choice(msg))

    @events.error
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
