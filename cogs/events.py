import discord
import random
import datetime
import urllib.request
import urllib.parse
import re
import pytz
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

        # ensure that enough arguments have been passed
        if len(args) < 2:
            await self.client.send_message(ctx.message.channel,
                                           'You did not pass enough arguments to create an event.\n'
                                           'Use setevent <time> <zone> <event> to set an event.')
            return

        # ensure that input time is valid
        time_raw = args[0]
        time_split = time_raw.split(":")
        error = '{0} is not a valid time.'.format(time_raw)
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

        # timezones
        time = datetime.datetime
        zones = {'est': time.now(pytz.timezone('US/Eastern')),
                 'cst': time.now(pytz.timezone('US/Mountain')),
                 'pst': time.now(pytz.timezone('US/Alaska'))}
        zone = args[1].lower()
        if zone not in zones:
            await self.client.send_message(ctx.message.channel,
                                           '{0} is not a valid timezone.\n'
                                           'Use setevent <time> <zone> <event> to set an event.'.format(zone))

        event = ' '.join(args[2:])

        # create an embed
        embed = discord.Embed(
            title='NEW EVENT CREATED',
            color=discord.Color.blue()
        )
        embed.set_thumbnail(url=ctx.message.author.avatar_url)
        embed.add_field(name='Event', value=event, inline=False)
        embed.add_field(name='Time', value='{0} {1}'.format(time_raw, zone.upper()), inline=False)
        await self.client.send_message(ctx.message.channel, embed=embed)

    @commands.command(pass_context=True)
    async def delevent(self, ctx, args):
        # delete an event that has been created by a user
        pass

    @commands.command(pass_context=True)
    async def checkevent(self, ctx, args):
        # check current events that are active from current time into the future
        pass

    @commands.command(pass_context=True)
    async def nextevent(self, ctx, args):
        # check how much time is left until the next event or specified event
        # /nextevent  <event name> returns time until next event
        pass


def setup(client):
    client.add_cog(Events(client))
