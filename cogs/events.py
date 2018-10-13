import discord
import datetime
import pytz
import json
import random
from discord.ext import commands

# todo time zone setting


class Events:
    def __init__(self, client):
        self.client = client

    @commands.command(pass_context=True)
    async def setevents(self, ctx):
        await self.client.send_message(ctx.message.channel, 'Did you mean to use ``setevent``?')

    @commands.command(pass_context=True)
    async def setevent(self, ctx, *args):
        # when a user calls !setevent, they can create an event and a time based on specified timezone. only members
        # should be able to do this once every five minutes. The result is sent to an embed and displayed in the channel
        # that it was created in
        if len(args) < 2:
            await self.client.send_message(ctx.message.channel, 'You did not pass enough arguments to create an event.\n'
                                                                'Use ``setevent <time> <zone> <event>`` to set an event.')
            return
        dt = args[0].split(':')
        h = dt[0]
        m = dt[1]
        tz = args[1].lower()
        event = ' '.join(args[2:])
        await self.event_handler(ctx, h, m, tz, event)

    @commands.command(pass_context=True)
    async def delevent(self, ctx, *args):
        # delete events in events.json using the event_id
        try:
            event_id = int(args[0])
        except IndexError:
            await self.client.send_message(ctx.message.channel, 'Please use the format ``delevent <event id>``.')
            return
        except ValueError:
            await self.client.send_message(ctx.message.channel, 'Event ID must be an integer.')
            return
        if len(args) > 1:
            await self.client.send_message(ctx.message.channel, 'You\'ve passed too many arguments.')
            return

        with open('files/events.json') as f:
            data = json.load(f)

        # events id must be passed as a string to match json
        event_id = str(event_id)
        if event_id in data:
            data.pop(event_id)
        else:
            await self.client.send_message(ctx.message.channel, 'Event {0} not found.'.format(event_id))
            return

        with open('files/events.json', 'w') as f:
            json.dump(data, f, indent=2)
        await self.client.send_message(ctx.message.channel, 'Event {0} deleted.'.format(event_id))

    @commands.command(pass_context=True)
    async def update(self, ctx, *args):
        # update an existing event with a new time and zone
        if len(args) < 1 or len(args) > 3:
            await self.client.send_message(ctx.message.channel, 'Please use the format ``update <event id> <time> <zone>``.')
            return

        # check the validity of the input
        try:
            event_id = args[0]
            dt = args[1].split(':')
            h = dt[0]
            m = dt[1]
            tz = args[2].lower()
            dt_user_set, utc_conversion, diff = await self.time_handler(ctx, h, m, tz)
            datetime_string_full, datetime_string_short = await self.make_string(dt_user_set)
        except IndexError:
            await self.client.send_message(ctx.message.channel,
                                           'Please use the format ``update <event id> <time> <zone>``.')
            return

        with open('files/events.json') as f:
            data = json.load(f)
        if event_id in data:
            orgnl_dt = data[event_id]['time']
            print(orgnl_dt)
            orgnl_tz = data[event_id]['zone']
            data[event_id]['time'] = datetime_string_full
            data[event_id]['zone'] = tz
        else:
            await self.client.send_message(ctx.message.channel, 'Event ID {0} does not exist.'.format(event_id))
            return
        with open('files/events.json', 'w') as f:
            json.dump(data, f, indent=2)
        dt_obj = await self.make_datetime(orgnl_dt)
        original_long, original_short = await self.make_string(dt_obj)
        try:
            # ctx, event_id, event, dt_user_set, tz, utc_conversion, method)
            embed = await self.embed_handler(ctx,
                                             event_id,
                                             data[event_id]['event'],
                                             datetime_string_short,
                                             tz,
                                             utc_conversion,
                                             'update',
                                             original_short,
                                             orgnl_tz)
            await self.client.send_message(ctx.message.channel, embed=embed)
        except Exception as e:
            print(e)

    @commands.command(pass_context=True)
    async def events(self, ctx, *args):
        # todo allow a call to 'all' to pull all events
        # check current events that are active from current time into the future
        # detect server avatar
        event_title = ':sparkles: Upcoming Event'
        event_id = ''

        if ctx.message.server.icon_url is '':
            thumb_url = self.client.user.avatar_url
        else:
            thumb_url = ctx.message.server.icon_url

        try:
            event_id = int(args[0])
        except IndexError:
            pass
        except ValueError:
            await self.client.send_message(ctx.message.channel, 'Event ID must be an integer.')
            return
        if len(args) > 1:
            await self.client.send_message(ctx.message.channel, 'You\'ve passed too many arguments.')
            return

        with open('files/events.json') as f:
            data = json.load(f)

        # if an event id is passed, attempt to return that event
        event_id = str(event_id)
        # ensure that id is in the events.json file and the server_id matches this server
        if event_id in data and data[event_id]['server_id'] == ctx.message.server.id:
            event = data[event_id]['event']
            time = await self.make_datetime(data[event_id]['time'])
            utc = time.astimezone(tz=pytz.UTC)
            time_full, time_short = await self.make_string(time)
            utc_full, utc_short = await self.make_string(utc)

            zone = data[event_id]['zone'].upper()

            embed = discord.Embed(title='──────────────── [Events] ────────────────', color=discord.Color.blue())
            embed.set_thumbnail(url=thumb_url)
            embed.add_field(name=event_title, value='**Event** [{0}]: {1}'.format(event_id, event), inline=False)

            utc_s = ''
            if data[event_id]['zone'].lower() != 'utc':
                utc_s = '| {0} UTC'.format(utc_short)
            embed.add_field(
                name='Time',
                value='{0} {1} {2}'.format(time_short, zone, utc_s)
            )
            eta = await self.eta(event_id)
            embed.add_field(name='ETA', value=eta)
            embed.set_footer(text='──────────────────────────────────────────')
            await self.client.send_message(ctx.message.channel, embed=embed)
            return

        if event_id != '':
            await self.client.send_message(ctx.message.channel,
                                           '{0} is not a valid event ID.\nDisplaying all events...'.format(event_id))
        # if no arguments are passed or event_id is not in data, return all events
        # todo allow the user to page through other events
        if len(data) < 1:
            await self.client.send_message(ctx.message.channel, 'There are currently no scheduled events.')
            return
        embed = discord.Embed(title='──────────────── [Events] ────────────────', color=discord.Color.blue())
        embed.set_thumbnail(url=thumb_url)
        embed.set_footer(text='──────────────────────────────────────────')
        embed.add_field(name=':sparkles: Upcoming Events', value='\u200b')
        # iterate through events and truncate event names longer than 50 characters
        num = 0
        for event_id, value in data.items():
            if data[event_id]['server_id'] == ctx.message.server.id:
                time = await self.make_datetime(data[event_id]['time'])
                utc = time.astimezone(tz=pytz.UTC)
                time_full, time_short = await self.make_string(time)
                utc_full, utc_short = await self.make_string(utc)
                num = num + 1
                diamond = ':small_orange_diamond:'
                if num % 2 == 0:
                    diamond = ':small_blue_diamond:'
                eta = await self.eta(event_id)
                utc = ''
                if value['zone'].lower() != 'utc':
                    utc = '| {0} UTC'.format(utc_short)
                embed.add_field(
                    name='{0}{1}'.format(diamond, value['event'][:50]),
                    value='Time: {0} {1} {2} | ({3})\nETA {4}'.format(time_short,
                                                                      value['zone'].upper(),
                                                                      utc,
                                                                      event_id,
                                                                      eta),
                    inline=False
                )
        await self.client.send_message(ctx.message.channel, embed=embed)

    async def event_handler(self, ctx, h, m, tz, event):
        dt_user_set, utc_conversion, diff = await self.time_handler(ctx, h, m, tz)
        datetime_string_full, datetime_string_short = await self.make_string(dt_user_set)
        # add event to events.json
        with open('files/events.json', 'r') as f:
            data = json.load(f)
            while True:
                event_id = random.randint(1, 99999)
                if event_id not in data:
                    data[event_id] = {
                        'event': event,
                        'time': datetime_string_full,
                        'zone': tz,
                        'user_id': ctx.message.author.id,
                        'server_id': ctx.message.server.id
                    }
                    break
        with open('files/events.json', 'w') as f:
            json.dump(data, f, indent=2)

        embed = await self.embed_handler(
            ctx,
            event_id,
            data[event_id]['event'],
            datetime_string_short,
            tz,
            utc_conversion,
            'new',
            None, None
        )
        await self.client.send_message(ctx.message.channel, embed=embed)

    async def time_handler(self, ctx, h, m, tz):
        d = datetime.datetime.now
        try:
            h = int(h)
            m = int(m)
            zones = {'pst': (pytz.timezone('US/Alaska')), 'pdt': (pytz.timezone('US/Alaska')),
                     'cst': (pytz.timezone('US/Mountain')), 'cdt': (pytz.timezone('US/Mountain')),
                     'est': (pytz.timezone('US/Eastern')), 'edt': (pytz.timezone('US/Eastern')),
                     'gmt': (pytz.timezone('GMT')), 'bst': (pytz.timezone('Europe/London')),
                     'utc': (pytz.timezone('UTC'))}
            # verify timezone
            if tz not in zones:
                await self.client.send_message(ctx.message.channel, '{} is not a valid timezone.'.format(tz))
                return
            # time set by the user using today's date
            dt_user_set = datetime.datetime(year=d().year, month=d().month, day=d().day,
                                            hour=h, minute=m, second=d().second,
                                            microsecond=d().microsecond, tzinfo=zones[tz])
            # current time in the tz set by the user
            dt_current_time = d(zones[tz])
            # utc time based on time input by the user
            if zones[tz] == 'utc':
                utc_conversion = None
            else:
                utc_conversion = dt_user_set.astimezone(pytz.timezone('UTC'))
            # difference between current time and set time
            diff = dt_user_set - dt_current_time
            # if the difference is less than 0 days, the set time is considered to be for tomorrow
            # thus we will add 24 hours to the time.
            if diff.days < 0:
                dt_user_set = dt_user_set + datetime.timedelta(hours=24)
            diff = dt_user_set - dt_current_time
            hours, remainder = divmod(diff.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            diff = '{0}h {1}m'.format(hours, minutes)
            return dt_user_set, utc_conversion, diff
        except ValueError as v:
            print(v)
            await self.client.send_message(ctx.message.channel, '{0}:{1} is not a valid time.'.format(h, m))

    async def embed_handler(self, ctx, event_id, event, dt_string, tz, utc_conversion, method, orgnl_dt, orgnl_tz):
        # set thumbnail icon
        eta = await self.eta(event_id)
        if ctx.message.server.icon_url is '':
            thumb_url = self.client.user.avatar_url
        else:
            thumb_url = ctx.message.server.icon_url

        # set event title
        event_title = ':sparkles: Upcoming Event'
        if method == 'update':
            event_title = ':sparkles: Event Updated'

        try:
            embed = discord.Embed(title='──────────────── [Events] ────────────────', color=discord.Color.blue())
            embed.set_thumbnail(url=thumb_url)
            embed.add_field(name=event_title, value='**Event** [{0}]: {1}'.format(event_id, event), inline=False)
            if utc_conversion is None:
                embed.add_field(name='Time', value='{0} {1}'.format(dt_string, tz.upper()))
            else:
                utc_string_full, utc_string_short = await self.make_string(utc_conversion)
                if method == 'update':
                    embed.add_field(name='Time', value='{0} {1} -> {2} {3}'.format(orgnl_dt, orgnl_tz.upper(), dt_string, tz.upper()))
                else:
                    embed.add_field(name='Time', value='{0} {1} | {2} UTC'.format(dt_string, tz.upper(), utc_string_short))
            embed.add_field(name='ETA', value='{0}'.format(eta))
            foot = int((39 - len(ctx.message.author.name)) / 2) * '─'
            embed.set_footer(text=foot + '[Created by: {0}]'.format(ctx.message.author.name) + foot)
            return embed
        except Exception as e:
            print(e)

    async def eta(self, event_id):
        # use event_id to pull time string
        zones = {'pst': pytz.timezone('US/Alaska'), 'pdt': pytz.timezone('US/Alaska'),
                 'cst': pytz.timezone('US/Mountain'), 'cdt': pytz.timezone('US/Mountain'),
                 'est': pytz.timezone('US/Eastern'), 'edt': pytz.timezone('US/Eastern'),
                 'gmt': pytz.timezone('GMT'), 'bst': pytz.timezone('Europe/London'),
                 'utc': pytz.timezone('UTC')}
        with open('files/events.json') as f:
            data = json.load(f)
        # use time string to generate datetime object and convert to UTC
        # subtract the datetime objects to get a difference
        time_full = await self.make_datetime(data[str(event_id)]['time'])
        time_full = time_full.astimezone(tz=pytz.UTC)
        diff = time_full - datetime.datetime.now(tz=pytz.UTC)
        if diff.days < 0:
            eta = 0
            return eta
        hours, remainder = divmod(diff.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        eta = '{0}h {1}m'.format(hours, minutes)
        return eta

    @staticmethod
    async def make_datetime(datetime_string):
        if type(datetime_string) != str:
            print('Not a string')
        else:
            datetime_object_full = datetime.datetime.strptime(datetime_string, '%Y-%m-%d %H:%M:%S')
            return datetime_object_full

    @staticmethod
    async def make_string(datetime_object):
        if type(datetime_object) != datetime.datetime:
            print('Not a datetime object')
        else:
            datetime_string_full = datetime_object.strftime("%Y-%m-%d %H:%M:%S")
            datetime_string_short = datetime_object.strftime("%H:%M")
            return datetime_string_full, datetime_string_short

    @commands.command(pass_context=True)
    async def time(self, ctx):
        # returns an embed with set time zones
        now = datetime.datetime.now
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


def setup(client):
    client.add_cog(Events(client))
