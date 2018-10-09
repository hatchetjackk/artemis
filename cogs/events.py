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

        # write to json file
        with open('files/events.json', 'r') as f:
            data = json.load(f)
            event_id = random.randint(1, 9999)
            # check if event already exists
            if event not in data:
                data[event] = {'time': '{0}:{1} {2}'.format(hours, minutes, zone),
                               'user_id': ctx.message.author.id,
                               'id': event_id}
                embed = discord.Embed(
                    title='NEW EVENT CREATED',
                    color=discord.Color.blue()
                )
                embed.set_thumbnail(url=ctx.message.author.avatar_url)
                embed.add_field(name=event, value='(id: {0})'.format(event_id), inline=False)
                embed.add_field(name='Time', value='{0} {1}'.format(time_raw, zone.upper()))
                await self.client.send_message(ctx.message.channel, embed=embed)

            # if event exists and creator is the same user, update time
            elif event in data and data[event]['user_id'] == ctx.message.author.id:
                data[event]['time'] = '{0}:{1} {2}'.format(hours, minutes, zone)
                embed = discord.Embed(
                    title='EVENT UPDATED',
                    color=discord.Color.blue()
                )
                embed.set_thumbnail(url=ctx.message.author.avatar_url)
                embed.add_field(name=event, value='(id: {0})'.format(data[event]['id']), inline=False)
                embed.add_field(name='Time', value='{0} {1}'.format(time_raw, zone.upper()))
                await self.client.send_message(ctx.message.channel, embed=embed)

            # else create the event with the current author
            else:
                data[event] = {'time': '{0}:{1} {2}'.format(hours, minutes, zone),
                               'user_id': ctx.message.author.id,
                               'id': event_id}
                embed = discord.Embed(
                    title='NEW EVENT CREATED',
                    color=discord.Color.blue()
                )
                embed.set_thumbnail(url=ctx.message.author.avatar_url)
                embed.add_field(name=event, value='(id: {0})'.format(event_id), inline=False)
                embed.add_field(name='Time', value='{0} {1}'.format(time_raw, zone.upper()))
                await self.client.send_message(ctx.message.channel, embed=embed)

        with open('files/events.json', 'w') as f:
            json.dump(data, f)

    @commands.command(pass_context=True)
    async def delevent(self, ctx, args):
        # delete an event that has been created by a user
        pass

    @commands.command(pass_context=True)
    async def checkevents(self, ctx, arg):
        # check current events that are active from current time into the future
        # todo a specific event can be called via its ID
        embed = discord.Embed(
            title='UPCOMING EVENTS',
            color=discord.Color.blue()
        )
        with open('files/events.json', 'r') as f:
            data = json.load(f)
            for key, value in data.items():
                embed.add_field(name=key,
                                value='Time: {1} (id: {0})'.format(value['id'], value['time'].upper()),
                                inline=False)
        await self.client.send_message(ctx.message.channel, embed=embed)

    @commands.command(pass_context=True)
    async def nextevent(self, ctx, args):
        # check how much time is left until the next event or specified event
        # /nextevent  <event name> returns time until next event
        pass


def setup(client):
    client.add_cog(Events(client))
