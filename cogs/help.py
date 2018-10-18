import discord

from discord.ext import commands


class Help:
    def __init__(self, client):
        self.client = client

    @commands.command(pass_context=True)
    async def help(self, ctx, *args):
        if len(args) > 1:
            await self.client.send_message(ctx.message.channel, 'You\'ve passed too many arguments.')
            return
        if len(args) > 0:
            if args[0] == 'events' or args[0] == 'event':
                await self.events_help(ctx)
                return
            if args[0] == 'embeds' or args[0] == 'embed':
                await self.embeds_help(ctx)
                return
            if args[0] == 'roles' or args[0] == 'role':
                await self.roles_help(ctx)
                return
            await self.client.send_message(ctx.message.channel, '{0} is not an option.'.format(args[0]))
            return
        if len(args) == 0:
            embed = discord.Embed(color=discord.Color.blue())
            embed.set_author(name="Help Page")
            embed.add_field(name='Artemis is in Beta', value='Things are likely to break, be broken, or be removed.\n')
            embed.add_field(
                name="How do I give karma?",
                value="Just say thanks and mention the target\nEx: 'Thanks @Hatchet Jackk'",
                inline=False
            )
            embed.add_field(name="ping", value="Return pong", inline=False)
            embed.add_field(name="roll", value="Roll NdN dice", inline=False)
            embed.add_field(name="karma <@user>", value="Check your or another <@user>'s current level of karma",
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
            embed.add_field(name='spamchannel <channel>', value='Set a channel for all spam.', inline=False)
            embed.add_field(name='help events', value='See available options for events.', inline=False)
            embed.add_field(name='help embeds', value='See available options for embeds.', inline=False)
            embed.add_field(name='help role', value='See available options for roles.', inline=False)
            embed.set_footer(text="Author: Hatchet Jackk")
            await self.client.send_message(ctx.message.author, embed=embed)
            print('Artemis: Sent help to {0}'.format(ctx.message.author))

    async def embeds_help(self, ctx):
        embed = discord.Embed(
            title='Embeds Help',
            color=discord.Color.blue()
        )
        embed.add_field(
            name='richembed',
            value='Quickly create a simple embed\n'
                  '*Available variables*: \n'
                  '``title`` ``color`` ``author`` ``footer`` ``thumbnail`` ``fieldname`` ``fieldvalue`` \n\n'
                  '*Example*: title=This is a title, color=dark_blue, author=Hatchet Jackk, fieldname=An interesting title, fieldvalue=Interesting information\n\n',
            inline=False
        )
        embed.add_field(
            name='colors',
            value='Show the list of default Discord colors.\n'
                  '``colors <optional: full>``',
            inline=False
        )
        await self.client.send_message(ctx.message.author, embed=embed)
        print('Artemis: Sent help to {0}'.format(ctx.message.author))

    async def events_help(self, ctx):
        embed = discord.Embed(
            title='Events Help',
            color=discord.Color.blue()
        )
        embed.add_field(
            name='setevent',
            value='Create a new event. Defaults to UTC time.\n'
                  '``setevent <hour:minutes> <day/month> <event>``',
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
                  '``update <event id> <hour:minutes> <day/month>``',
            inline=False
        )
        embed.add_field(
            name='time',
            value='Show current timezones.\n'
                  '``time``',
            inline=False
        )
        embed.add_field(
            name='mytime',
            value='Show an event in a specified timezone.\n'
                  '``mytime <event id> <timezone>``',
            inline=False
        )
        embed.add_field(
            name='notify',
            value='Tell Artemis to notify you when an event is less than one hour from beginning.\n'
                  '``notify <event id>``',
            inline=False
        )
        await self.client.send_message(ctx.message.author, embed=embed)
        print('Artemis: Sent help to {0}'.format(ctx.message.author))

    async def roles_help(self, ctx):
        embed = discord.Embed(
            title='Roles Help',
            color=discord.Color.blue()
        )
        embed.add_field(
            name='autorole',
            value='Create an autorole for new members\n'
                  '`add`: Make a default autorole (there can only be one autorole at a time)\n'
                  '`del`: Remove the autorole',
            inline=False
        )
        await self.client.send_message(ctx.message.author, embed=embed)
        print('Artemis: Sent help to {0}'.format(ctx.message.author))


def setup(client):
    client.add_cog(Help(client))
