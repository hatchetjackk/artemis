import discord
import datetime
import pytz
import json
import random
from collections import OrderedDict
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
        # todo add 'hours from now', add timezones for uk
        now = datetime.datetime.now
        zones = {'est': now(pytz.timezone('US/Eastern')),
                 'cst': now(pytz.timezone('US/Mountain')),
                 'pst': now(pytz.timezone('US/Alaska')),
                 'gmt': now(pytz.timezone('GMT')),
                 'utc': now(pytz.timezone('UTC')),
                 'bst': now(pytz.timezone('Europe/London'))}

        time_raw = args[0]
        zone = args[1].lower()
        event = ' '.join(args[2:])

        if len(args) < 2:
            await self.client.send_message(ctx.message.channel, 'You did not pass enough arguments to create an event.\n''Use ``setevent <time> <zone> <event>`` to set an event.')
            return
        if zone not in zones:
            await self.client.send_message(ctx.message.channel, '{0} is not a valid timezone.\nUse ``setevent <time> <zone> <event>`` to set an event.'.format(zone))
            return

        # time handling
        if ':' in [c for c in time_raw]:
            # sets event based on 24 hour time
            print('time based')
            await self.event_handler_one(time_raw, zone, event, ctx)
        elif 'h' or 'm' in [c for c in time_raw]:
            # sets event from hours:minutes from now
            print('hour based')
            self.event_handler_two(time_raw, zone, event, ctx)

    async def event_handler_one(self, time_raw, zone, event, ctx):
        error = '{0} is not a valid time.'.format(time_raw)
        time_split = time_raw.split(":")
        # ensure values are integers within 24 hour format
        try:
            hours = int(time_split[0])
            minutes = int(time_split[1])
        except ValueError:
            await self.client.send_message(ctx.message.channel, error)
            return
        if minutes > 59:
            await self.client.send_message(ctx.message.channel, error)
            return
        if hours < 0 or hours > 24:
            await self.client.send_message(ctx.message.channel, error)
            return
        time_set = str(hours) + ':' + str(minutes)

        with open('files/events.json', 'r') as f:
            data = json.load(f)
            while True:
                event_id = random.randint(1, 99999)
                if event_id not in data:
                    data[event_id] = {'event': event,
                                      'time': '{0}:{1} {2}'.format(hours, minutes, zone),
                                      'user_id': ctx.message.author.id}
                    # todo pass this to an embed function
                    embed = self.embed_handler(event, event_id, time_set, zone, ctx, 'new')
                    await self.client.send_message(ctx.message.channel, embed=embed)
                    break
        # write to file
        with open('files/events.json', 'w') as f:
            json.dump(data, f, indent=2)

    @commands.command(pass_context=True)
    async def delevent(self, ctx, args):
        # delete an event that has been created by a user
        pass

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
            data[event_id]['time'] = '{0} {1}'.format(time, zone)
        else:
            await self.client.send_message(ctx.message.channel, 'Event ID {0} does not exist.'.format(event_id))
            return

        with open('files/events.json', 'w') as f:
            json.dump(data, f, indent=2)

        embed = self.embed_handler(data[event_id]['event'], event_id, time, zone, ctx, 'update')
        await self.client.send_message(ctx.message.channel, embed=embed)

    @commands.command(pass_context=True)
    async def checkevents(self, ctx, *args):
        # check current events that are active from current time into the future
        thumb_url = 'https://images-ext-1.discordapp.net/external/veD-zTXyh96Zn-MB2t3vXqiZrRlihx4r5DCnrJ0nEh0/https/i.imgur.com/JK61b19.png?width=676&height=676'
        ev_id = 0
        try:
            ev_id = int(args[0])
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
        ev_id = str(ev_id)
        if ev_id in data:
            event = data[ev_id]['event']
            time = data[ev_id]['time'].upper()
            event_title = ':sparkles: Upcoming Event'
            embed = discord.Embed(
                title='──────────────── [Events] ────────────────',
                color=discord.Color.blue()
            )
            embed.set_thumbnail(url=thumb_url)
            embed.add_field(name=event_title,
                            value='**Event** [{0}]: {1}'.format(ev_id, event),
                            inline=False)
            embed.add_field(name='Time',
                            value='{0} | {1} | {2}'.format(time, 'placeholder', 'placeholder'))
            await self.client.send_message(ctx.message.channel, embed=embed)
        else:
            embed = discord.Embed(
                title='──────────────── [Events] ────────────────',
                color=discord.Color.blue()
            )
            embed.set_thumbnail(url=thumb_url)
            for key, value in data.items():
                embed.add_field(name=value['event'],
                                value='Time: {0} (id: {1})'.format(value['time'].upper(), key),
                                inline=False)
            await self.client.send_message(ctx.message.channel, embed=embed)

    @commands.command(pass_context=True)
    async def nextevent(self, ctx, args):
        # check how much time is left until the next event or specified event
        # /nextevent  <event name> returns time until next event
        pass

    @staticmethod
    def embed_handler(event, event_id, time_set, zone, ctx, method):
        event_title = ':sparkles: Upcoming Event'
        if method == 'update':
            event_title = ':sparkles: Event Updated'
        set_time = '{0} {1}'.format(time_set, zone.upper())
        zone_one = 'TimeZone1'
        zone_two = 'TimeZone2'
        thumb_url = 'https://images-ext-1.discordapp.net/external/veD-zTXyh96Zn-MB2t3vXqiZrRlihx4r5DCnrJ0nEh0/https/i.imgur.com/JK61b19.png?width=676&height=676'
        # thumb_url = ctx.message.author.avatar_url
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
        embed.add_field(
            name='Time',
            value='{0}    |    {1}    |    {2}'.format(set_time, zone_one, zone_two))
        embed.add_field(name='ETA', value='{0}'.format('placeholder'))
        embed.set_footer(
            text=foot + '[Created by: {0}]'.format(ctx.message.author.name) + foot)
        return embed


def setup(client):
    client.add_cog(Events(client))
