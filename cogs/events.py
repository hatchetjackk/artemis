import asyncio
import discord
from _datetime import datetime
import pytz
import json
import random
from discord.ext import commands

""" All times in events are handled as UTC and then converted to set zone times for local reference """


class Events:
    def __init__(self, client):
        self.client = client

    @commands.command(pass_context=True)
    async def setevent(self, ctx, *args):
        if len(args) < 2:
            await self.client.send_message(ctx.message.channel, 'Please use the format ``setevent <h:m> <day/mnth> <event>``.')
            return

        h, m = args[0].split(':')
        day, month = args[1].split('/')
        event = ' '.join(args[2:])

        # format the time to be timezone ready

        dt = await self.time_formatter(ctx, day, month, h, m)
        if dt is None:
            return

        # utc = await self.utc_conversion(dt, tz)
        data = await self.load_events()

        # generate the event with a unique ID
        while True:
            event_id = random.randint(1, 99999)
            if event_id not in data:
                dt_long, dt_short = await self.make_string(dt)
                data[event_id] = {
                    'event': event,
                    'time': dt_long,
                    'user_id': ctx.message.author.id,
                    'server_id': ctx.message.server.id,
                    'notify': False,
                    'member_notify': {}
                }
                break

        await self.dump_events(data)

        embed = await self.embed_handler(ctx, dt, event, event_id, update=False)
        await self.client.send_message(ctx.message.channel, embed=embed)

    @commands.command(pass_context=True)
    async def delevent(self, ctx, *args):
        if len(args) < 1:
            await self.client.send_message(ctx.message.channel, 'Use ``delevent <event id>`` to delete an event.')
            return
        event_list = args[:]
        data = await self.load_events()
        if str(event_list[0]) == 'all':
            # delete all events
            while len(data) > 0:
                try:
                    for event in data:
                        data.pop(event)
                        await self.dump_events(data)
                except RuntimeError:
                    pass
            await self.client.send_message(ctx.message.channel, 'All events deleted!')
            return
        # print out results and delete after 5 seconds
        for event_id in event_list:
            count = 1
            messages = []
            if event_id in data:
                count += 1
                data.pop(event_id)
                await self.dump_events(data)
                await self.client.send_message(ctx.message.channel, 'Event {} successfully deleted.'.format(event_id))
                async for message in self.client.logs_from(ctx.message.channel, limit=int(count)):
                    messages.append(message)
            else:
                count += 1
                await self.client.send_message(ctx.message.channel, 'Event {} not found.'.format(event_id))
                async for message in self.client.logs_from(ctx.message.channel, limit=int(count)):
                    messages.append(message)
            await asyncio.sleep(5)
            await self.client.delete_messages(messages)

    @commands.command(pass_context=True)
    async def update(self, ctx, *args):
        if 1 > len(args) > 3:
            await self.client.send_message(ctx.message.channel,
                                           'Please use the format ``update <event id> <h:m> <day/mnth> ``.')
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
            await self.client.send_message(ctx.message.channel, 'Event ID {} not found.'.format(event_id))
            return
        event = data[event_id]['event']
        embed = await self.embed_handler(ctx, dt, event, event_id, update=True)
        await self.client.send_message(ctx.message.channel, embed=embed)
        await self.dump_events(data)

    @commands.command(pass_context=True)
    async def events(self, ctx, *args):
        if len(args) > 1:
            await self.client.send_message(ctx.message.channel, 'Please use `events <event id>` to check a single event\n'
                                                                'or use `events` to check all events.')
            return

        with open('files/servers.json') as f:
            thumbs = json.load(f)
        # set the thumbnail
        if thumbs[ctx.message.server.id]['thumb_url'] != '':
            thumb_url = thumbs[ctx.message.server.id]['thumb_url']
        else:
            thumb_url = self.client.user.avatar_url

        # set embed
        title = '──────────────── [Events] ────────────────'
        color = discord.Color.blue()
        footer_style = int((39 - len(ctx.message.author.name)) / 2) * '─'
        fmt_footer = footer_style + '[Created by: {0}]'.format(ctx.message.author.name) + footer_style

        # create embed
        embed = discord.Embed(title=title, color=color)
        embed.set_thumbnail(url=thumb_url)
        embed.set_footer(text=fmt_footer)
        embed.add_field(name=':sparkles: Upcoming Events', value='\u200b')

        # create variables
        event_id = ''
        try:
            event_id = str(args[0])
        except IndexError:
            pass
        data = await self.load_events()
        # ensure that the event matches the server
        if event_id in data and data[event_id]['server_id'] == ctx.message.server.id:
            print(data[event_id]['server_id'])
            print(ctx.message.server.id)
            event = data[event_id]['event'][:50]
            dt = await self.make_datetime(data[event_id]['time'])
            dt_long, dt_short = await self.make_string(dt)
            embed.add_field(name=event, value='**Event** [{0}]: {1}\n'
                                              '**Time**: {2}'.format(event_id, event, dt_short), inline=False)
            await self.client.send_message(ctx.message.channel, embed=embed)
            return
        elif event_id == '':
            counter = 1
            for key, value in data.items():
                if value['server_id'] == ctx.message.server.id:
                    diamond = ':small_orange_diamond:'
                    if counter % 2 == 0:
                        diamond = ':small_blue_diamond:'
                    event = value['event'][:50]
                    event_id = key
                    dt = await self.make_datetime(data[key]['time'])
                    dt_long, dt_short = await self.make_string(dt)
                    eta = await self.eta(dt)
                    embed.add_field(name='{0} {1}'.format(diamond, event), value='**Time**: {0}\n'
                                                                                 '**ETA**: {1}\n'
                                                                                 '**ID**: {2}'.format(dt_short, eta, event_id), inline=False)
                    counter += 1
            await self.client.send_message(ctx.message.channel, embed=embed)

    @commands.command(pass_context=True)
    async def mytime(self, ctx, *args):
        # set the thumbnail
        if ctx.message.server.icon_url is '':
            thumb_url = self.client.user.avatar_url
        else:
            thumb_url = ctx.message.server.icon_url

        # set embed
        title = '──────────────── [Events] ────────────────'
        color = discord.Color.blue()
        footer_style = int((39 - len(ctx.message.author.name)) / 2) * '─'
        fmt_footer = footer_style + '[Created by: {0}]'.format(ctx.message.author.name) + footer_style

        # create embed
        embed = discord.Embed(title=title, color=color)
        embed.set_thumbnail(url=thumb_url)
        embed.set_footer(text=fmt_footer)
        try:
            event_id = args[0]
            tz = args[1]
            data = await self.load_events()
        except IndexError:
            await self.client.send_message(ctx.message.channel,
                                           'Use `mytime <event id> <time zone>` to check an event in a specific timezone.')
            return
        # find events in data that match the current server
        if event_id in data:
            dt = await self.make_datetime(data[event_id]['time'])
            verify, tz_conversion = await self.timezones(tz)
            new_dt = dt.astimezone(tz_conversion)
            dt = new_dt + datetime.utcoffset(new_dt)

            dt_long, dt_short = await self.make_string(dt)
            dt_short = dt_short.replace('UTC', '')
            embed.add_field(name='{}'.format(data[event_id]['event'][:50]),
                            value='This event in {0} is {1}'.format(tz.upper(), dt_short))
            await self.client.send_message(ctx.message.channel, embed=embed)
            return
        await self.client.send_message(ctx.message.channel,
                                       'Use `mytime <event id> <time zone>` to check an event in a specific timezone.')

    @commands.command(pass_context=True)
    async def time(self, ctx):
        # returns an embed with set time zones
        now = datetime.now
        zones = {'pst/pdt': now(pytz.timezone('US/Alaska')),
                 'cst/cdt': now(pytz.timezone('US/Mountain')),
                 'est/edt': now(pytz.timezone('US/Eastern')),
                 'utc/gmt': now(pytz.timezone('GMT')),
                 'bst': now(pytz.timezone('Europe/London'))}
        embed = discord.Embed(title='──────────────── [ Time ] ────────────────', color=discord.Color.blue())
        embed.add_field(name='Zone', value='\n'.join([zone.upper() for zone in zones]), inline=True)
        embed.add_field(name='Time', value='\n'.join(zones[zone].strftime('%H:%M') for zone in zones))
        embed.set_footer(text='──────────────────────────────────────────')
        await self.client.send_message(ctx.message.channel, embed=embed)

    @commands.command(pass_context=True)
    async def notify(self, ctx, *args):
        event_id = str(args[0])
        channel = str(ctx.message.channel.id)
        author = ctx.message.author
        data = await self.load_events()
        if event_id in data:
            if author.id not in data[event_id]['member_notify']:
                data[event_id]['notify'] = True
                data[event_id]['member_notify'].update({str(author.id): channel})
                await self.client.send_message(ctx.message.channel, 'Set to notify **{author}** when *{event}* is 1 hour away from '
                                                                    'starting!'.format(author=author.name, event=data[event_id]['event']))
                await self.dump_events(data)
                return
            # if user already exists in notification, remove the user
            if str(author.id) in data[event_id]['member_notify']:
                data[event_id]['member_notify'].pop(str(author.id), None)
                await self.client.send_message(ctx.message.channel,
                                               'Removing **{author}\'s** notification for *{event}*.'.format(
                                                   author=author.name,
                                                   event=data[event_id]['event']))
                if len(data[event_id]['member_notify']) < 1:
                    data[event_id]['notify'] = False
                await self.dump_events(data)
                return

    async def time_formatter(self, ctx, day, month, h, m):
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
            await self.client.send_message(ctx.message.channel, 'An incorrect datetime was passed: {}\n'
                                                                'Use the format `setevent <h:m> <day/mnth> <event>`'.format(e))
            return None

    async def embed_handler(self, ctx, dt, event, event_id, update):
        # get two times
        dt_long, dt_short = await self.make_string(dt)

        with open('files/servers.json') as f:
            thumbs = json.load(f)
        # set the thumbnail
        if thumbs[ctx.message.server.id]['thumb_url'] != '':
            thumb_url = thumbs[ctx.message.server.id]['thumb_url']
        else:
            thumb_url = self.client.user.avatar_url

        # set the event title
        event_title = ':sparkles: Upcoming Event'
        if update:
            event_title = ':sparkles: Event Updated'

        # set embed
        title = '──────────────── [Events] ────────────────'
        color = discord.Color.blue()
        footer_style = int((39 - len(ctx.message.author.name)) / 2) * '─'
        fmt_footer = footer_style + '[Created by: {0}]'.format(ctx.message.author.name) + footer_style

        # create embed
        embed = discord.Embed(title=title, color=color)
        embed.set_thumbnail(url=thumb_url)
        embed.set_footer(text=fmt_footer)

        if update:
            data = await self.load_events()
            if event_id in data:
                dt_data = data[event_id]['time']
                dt_data = await self.make_datetime(dt_data)
                eta = await self.eta(dt_data)
                dt_data_long, dt_data_short = await self.make_string(dt_data)
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

    @staticmethod
    async def timezones(tz):
        zones = {'pst': pytz.timezone('US/Alaska'), 'pdt': pytz.timezone('US/Alaska'),
                 'cst': pytz.timezone('US/Mountain'), 'cdt': pytz.timezone('US/Mountain'),
                 'est': pytz.timezone('US/Eastern'), 'edt': pytz.timezone('US/Eastern'),
                 'gmt': pytz.timezone('GMT'), 'bst': pytz.timezone('Europe/London'),
                 'utc': pytz.timezone('UTC')}
        if tz in zones:
            return True, zones[tz]
        else:
            return False

    @staticmethod
    async def load_events():
        with open('files/events.json') as f:
            data = json.load(f)
        return data

    @staticmethod
    async def dump_events(data):
        with open('files/events.json', 'w') as f:
            json.dump(data, f, indent=2)


def setup(client):
    client.add_cog(Events(client))
