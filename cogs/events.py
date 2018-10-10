import discord
import datetime
import pytz
import json
import random
from discord.ext import commands

# todo event planning, time zone setting, ETA against current time, time zone comparison, check event time compared to custom input
# todo make it all embedded with set image depending on time called.


class Events:
    def __init__(self, client):
        self.client = client

    @commands.command(pass_context=True)
    async def setevent(self, ctx, *args):
        # when a user calls !setevent, they can create an event and a time based on specified timezone. only members should be able to do this once
        # every five minutes.
        # todo add 'hours from now'
        now = datetime.datetime.now
        zones = {'est': now(pytz.timezone('US/Eastern')), 'edt': now(pytz.timezone('US/Eastern')),
                 'cst': now(pytz.timezone('US/Mountain')), 'cdt': now(pytz.timezone('US/Mountain')),
                 'pst': now(pytz.timezone('US/Alaska')), 'pdt': now(pytz.timezone('US/Alaska')),
                 'gmt': now(pytz.timezone('GMT')), 'bst': now(pytz.timezone('Europe/London')),
                 'utc': now(pytz.timezone('UTC'))}

        if len(args) < 2:
            await self.client.send_message(ctx.message.channel, 'You did not pass enough arguments to create an event.\n'
                                                                'Use ``setevent <time> <zone> <event>`` to set an event.')
            return

        dt = args[0]
        zone = args[1].lower()
        event = ' '.join(args[2:])

        if zone not in zones:
            await self.client.send_message(ctx.message.channel, '{0} is not a valid timezone.\n'
                                                                'Use ``setevent <time> <zone> <event>`` to set an event.'.format(zone))
            return

        try:
            dt = datetime.datetime.strptime(dt, '%H:%M')
            await self.event_handler_one(dt, zone, event, ctx)
        except ValueError:
            await self.client.send_message(ctx.message.channel, '{0} is not a valid time.'.format(dt))
            return

    @commands.command(pass_context=True)
    async def time(self, ctx, arg):
        now = datetime.datetime.now
        zones = {'est': now(pytz.timezone('US/Eastern')), 'edt': now(pytz.timezone('US/Eastern')),
                 'cst': now(pytz.timezone('US/Mountain')), 'cdt': now(pytz.timezone('US/Mountain')),
                 'pst': now(pytz.timezone('US/Alaska')), 'pdt': now(pytz.timezone('US/Alaska')),
                 'gmt': now(pytz.timezone('GMT')), 'bst': now(pytz.timezone('Europe/London')),
                 'utc': now(pytz.timezone('UTC'))}
        if arg not in zones:
            await self.client.send_message(ctx.message.channel, '{0} is not a valid timezone.'.format(arg.upper()))
            return
        if arg == 'utc':
            await self.client.send_message(ctx.message.channel,
                                           'The current time for {0} is {1}.'.format(arg.upper(), zones[arg].strftime('%H:%M')))
            return
        await self.client.send_message(ctx.message.channel,
                                       'The current time for {0} is {1}. (UTC time is {2}) '.format(arg.upper(), zones[arg].strftime('%H:%M'), zones['utc'].strftime('%H:%M')))

    @commands.command(pass_context=True)
    async def delevent(self, ctx, *args):
        # delete events in events.json
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
        if len(args) < 1 or len(args) > 3:
            await self.client.send_message(ctx.message.channel, 'Please use the format ``update <event id> <time> <zone>``.')
            return
        event_id = args[0]
        time = args[1]
        zone = args[2]
        with open('files/events.json') as f:
            data = json.load(f)
        if event_id in data:
            data[event_id]['time'] = time
            data[event_id]['zone'] = zone
        else:
            await self.client.send_message(ctx.message.channel, 'Event ID {0} does not exist.'.format(event_id))
            return

        with open('files/events.json', 'w') as f:
            json.dump(data, f, indent=2)
        dt2 = None
        tz2 = None
        embed = self.embed_handler(data[event_id]['event'], event_id, time, dt2, zone, tz2, ctx, 'update')
        await self.client.send_message(ctx.message.channel, embed=embed)

    @commands.command(pass_context=True)
    async def checkevents(self, ctx, *args):
        # check current events that are active from current time into the future
        thumb_url = 'https://images-ext-1.discordapp.net/external/veD-zTXyh96Zn-MB2t3vXqiZrRlihx4r5DCnrJ0nEh0/https/i.imgur.com/JK61b19.png?width=676&height=676'
        event_id = 0
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
        # return single event
        event_id = str(event_id)
        if event_id in data:
            event = data[event_id]['event']
            time = data[event_id]['time']
            zone = data[event_id]['zone'].upper()
            event_title = ':sparkles: Upcoming Event'
            embed = discord.Embed(
                title='──────────────── [Events] ────────────────',
                color=discord.Color.blue()
            )
            embed.set_thumbnail(url=thumb_url)
            embed.add_field(name=event_title,
                            value='**Event** [{0}]: {1}'.format(event_id, event),
                            inline=False)
            embed.add_field(name='Time',
                            value='{0} {1} | {2} {3}'.format(time, zone, await self.time_handler(time, zone), 'UTC'))
            embed.add_field(name='ETA',
                            value='placeholder')
            embed.set_footer(text='──────────────────────────────────────────')
            await self.client.send_message(ctx.message.channel, embed=embed)
        else:
            embed = discord.Embed(
                title='──────────────── [Events] ────────────────',
                color=discord.Color.blue()
            )
            embed.set_thumbnail(url=thumb_url)
            for key, value in data.items():
                embed.add_field(name=value['event'],
                                value='Time: {0} {1} (id: {2})'.format(value['time'], value['zone'].upper(), key),
                                )
                embed.add_field(name='ETA',
                                value='placeholder')
                embed.set_footer(text='──────────────────────────────────────────')
            await self.client.send_message(ctx.message.channel, embed=embed)

    async def event_handler_one(self, time_raw, tz, event, ctx):
        try:
            dt = datetime.datetime.strptime(time_raw, '%H:%M')
            if tz == 'utc':
                dt2 = await self.utc_handler(dt, tz)
                tz2 = None
            else:
                dt2 = await self.time_handler(dt, tz)
                tz2 = 'utc'
            dt2 = dt2.strftime('%H:%M')
        except ValueError:
            await self.client.send_message(ctx.message.channel, '{0} is not a valid time.'.format(time_raw))
            return

        with open('files/events.json', 'r') as f:
            data = json.load(f)
            while True:
                event_id = random.randint(1, 99999)
                if event_id not in data:
                    data[event_id] = {'event': event,
                                      'time': dt.strftime('%H:%M'),
                                      'zone': tz,
                                      'user_id': ctx.message.author.id}
                    embed = self.embed_handler(event, event_id, dt, dt2, tz, tz2, ctx, 'new')
                    await self.client.send_message(ctx.message.channel, embed=embed)
                    break
        with open('files/events.json', 'w') as f:
            json.dump(data, f, indent=2)

    @staticmethod
    async def event_handler_two(ctx, args):
        # handle input for hours and minutes
        print(args)
        utc = datetime.datetime.now(pytz.timezone('UTC'))
        print(utc)
        time = args[0]
        print(time)
        time = time.split('h')
        print(time)
        hours = time[0]
        minutes = time[1].strip('m')
        print(hours, minutes)
        zone = args[1]
        event = ' '.join(args[2:])
        pass

    @staticmethod
    async def time_handler(dt, tz):
        # take a time and convert to utc
        tdelta = datetime.timedelta
        zones = {'est': 4, 'edt': 4,
                 'cst': 5, 'cdt': 5,
                 'pst': 7, 'pdt': 7,
                 'gmt': 0, 'bst': -1,
                 'utc': 0}
        if tz in zones and tz != 'utc':
            dt1 = dt + tdelta(hours=zones[tz])
            return dt1

    @staticmethod
    async def utc_handler(dt, tz):
        tdelta = datetime.timedelta
        zones = {'est': 4, 'edt': 4,
                 'cst': 5, 'cdt': 5,
                 'pst': 7, 'pdt': 7,
                 'gmt': 0, 'bst': -1,
                 'utc': 0}
        if tz in zones and tz != 'utc':
            dt1 = dt - tdelta(hours=zones[tz])
            return dt1
        return dt

    @staticmethod
    def embed_handler(event, event_id, dt1, dt2, tz1, tz2, ctx, method):
        event_title = ':sparkles: Upcoming Event'
        if method == 'update':
            event_title = ':sparkles: Event Updated'
        if type(dt1) != datetime.datetime:
            dt1 = datetime.datetime.strptime(dt1, '%H:%M')
            dt1 = dt1.strftime('%H:%M')
        else:
            dt1 = dt1.strftime('%H:%M')
        thumb_url = 'https://images-ext-1.discordapp.net/external/veD-zTXyh96Zn-MB2t3vXqiZrRlihx4r5DCnrJ0nEh0/https/i.imgur.com/JK61b19.png?width=676&height=676'
        foot = int((39 - len(ctx.message.author.name)) / 2) * '─'

        embed = discord.Embed(
            title='──────────────── [Events] ────────────────',
            color=discord.Color.blue())
        embed.set_thumbnail(
            url=thumb_url)
        embed.add_field(
            name=event_title,
            value='**Event** [{0}]: {1}'.format(event_id, event),
            inline=False)
        if tz2 is None:
            embed.add_field(
                name='Time',
                value='{0} {1}'.format(dt1, tz1))
        else:
            embed.add_field(
                name='Time',
                value='{0} {1} | {2} {3}'.format(dt1, tz1.upper(), dt2, tz2.upper()))
        embed.add_field(name='ETA', value='{0}'.format('placeholder'))
        embed.set_footer(
            text=foot + '[Created by: {0}]'.format(ctx.message.author.name) + foot)
        return embed


def setup(client):
    client.add_cog(Events(client))
