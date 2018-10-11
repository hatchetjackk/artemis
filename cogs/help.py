import discord

from discord.ext import commands


class Help:
    def __init__(self, client):
        self.client = client

    @commands.command(pass_context=True)
    async def help(self, ctx, *args):
        if len(args) > 1:
            await self.client.send_message(ctx.message.channel, 'You\'ve passed too many arguments.')
        try:
            if args[0] == 'events':
                await self.events_help(ctx)
                return
            else:
                await self.client.send_message(ctx.message.channel, '{0} is not an option.'.format(args[0]))
                return
        except IndexError:
            pass
        author = ctx.message.author
        embed = discord.Embed(color=discord.Color.blue())
        embed.set_author(name="Help Page")
        embed.add_field(
            name="How do I give karma?",
            value="Just say thanks and mention the target\nEx: 'Thanks @Hatchet Jackk'",
            inline=False
        )
        embed.add_field(name="ping", value="Return pong", inline=False)
        embed.add_field(name="roll", value="Roll NdN dice", inline=False)
        embed.add_field(name="karma <user>", value="Check your or another <user>'s current level of karma",
                        inline=False)
        embed.add_field(name='hello', value='Say hi to Artemis!', inline=False)
        embed.add_field(name="status", value="Check Artemis' status", inline=False)
        embed.add_field(name="leaderboard", value="Check karma levels (WIP)", inline=False)
        embed.add_field(name="arena", value="Settle the score (WIP)", inline=False)
        embed.add_field(name="flip", value="Flip a coin", inline=False)
        embed.add_field(name="rps <choice>", value="Play Rock, Paper, Scissors against the bot", inline=False)
        embed.add_field(name="whois <user>", value="Find user details (WIP)", inline=False)
        embed.add_field(name="server", value="Check server information (WIP)", inline=False)
        embed.add_field(name='yt <search>', value='Return the first YouTube video based for <search>.', inline=False)
        embed.add_field(name='help events', value='See available options for events.', inline=False)
        embed.set_footer(text="Author: Hatchet Jackk")
        await self.client.send_message(author, embed=embed)
        print('Artemis: Sent help to {0}'.format(author))

    async def events_help(self, ctx):
        embed = discord.Embed(
            title='Events Help',
            color=discord.Color.blue()
        )
        embed.add_field(
            name='setevent',
            value='Create a new event\n'
                  '``setevent <time> <zone> <event>``',
            inline=False
        )
        embed.add_field(
            name='events',
            value='Check current events. Passing an event id will load that specific event only.\n'
                  '``events <optional: event id>``',
            inline=False
        )
        embed.add_field(
            name='delevent',
            value='Delete an event\n'
                  '``delevent <event id>``',
            inline=False
        )
        embed.add_field(
            name='update',
            value='Update an event with a new time and zone.\n'
                  '``update <event id> <time> <zone>``',
            inline=False
        )
        embed.add_field(
            name='time',
            value='Show current timezones.\n'
                  '``time``',
            inline=False
        )
        await self.client.send_message(ctx.message.author, embed=embed)


def setup(client):
    client.add_cog(Help(client))
