import discord
from discord.ext import commands


class Help:
    def __init__(self, client):
        self.client = client

    @commands.group()
    async def help(self, ctx):
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(color=discord.Color.blue())
            embed.set_author(name="Help Page")
            embed.add_field(name='Artemis is in Beta',
                            value='Things might bend, break, or tear a whole into another dimension.\n')
            embed.add_field(
                name="How do I give karma?",
                value="Just say thanks and mention the target\nEx: 'Thanks @Hatchet Jackk'",
                inline=False
            )
            embed.add_field(name="ping", value="Return pong", inline=False)
            embed.add_field(name="roll", value="Roll NdN dice", inline=False)
            embed.add_field(name="karma @user",
                            value="Check your or another <@user>'s current level of karma",
                            inline=False)
            embed.add_field(name='hello', value='Say hi to Artemis!', inline=False)
            embed.add_field(name="status", value="Check Artemis' status", inline=False)
            # embed.add_field(name="leaderboard", value="Check karma levels (WIP)", inline=False)
            # embed.add_field(name="arena", value="Settle the score (WIP)", inline=False)
            embed.add_field(name="flip", value="Flip a coin", inline=False)
            embed.add_field(name="rps choice", value="Play Rock, Paper, Scissors against the bot", inline=False)
            embed.add_field(name="whois user", value="Find user details", inline=False)
            embed.add_field(name='yt search', value='Return the first YouTube video based for <search>.', inline=False)
            embed.add_field(name='g search', value='Return the first Google result for <search>.', inline=False)
            embed.add_field(name='r/', value='Search for a subreddit `r/nameofsub`.', inline=False)
            embed.add_field(name='help events', value='See available options for events.', inline=False)
            embed.add_field(name='help embeds', value='See available options for embeds.', inline=False)
            await ctx.author.send(embed=embed)
            print('Artemis: Sent help to {0}'.format(ctx.author.name))

    @staticmethod
    @help.group()
    async def embeds(ctx):
        embed = discord.Embed(
            title='Embeds Help',
            color=discord.Color.red()
        )
        embed.add_field(
            name='richembed',
            value='Quickly create embeds\n'
                  '`richembed get`: Get the embed information from a message id.\n'
                  '`richembed ex`: Get a richembed example and example input.\n'
                  '`richembed pasta`: Takes richembed input to create a new embed.',
            inline=False
        )
        embed.add_field(
            name='colors',
            value='Show the list of default Discord colors.\n'
                  '``colors <optional: full>``',
            inline=False
        )
        await ctx.author.send(embed=embed)
        print('Artemis: Sent help to {0}'.format(ctx.author))

    @staticmethod
    @help.group()
    async def events(ctx):
        embed = discord.Embed(
            title='Events Help',
            color=discord.Color.green()
        )
        embed.add_field(
            name='events',
            value='Show all events in the guild. New events are UTC by default.\n'
                  '**Add new events with**: \n'
                  '`events set h:m day/mnth event_description`\n'
                  '`events timer hours minutes "event description"`\n'
                  '**Find individual events with**: \n'
                  '`events find event_id`\n'
                  '**Update existing events with**:\n'
                  '`events update event_id h:m day/mnth`',
            inline=False
        )
        embed.add_field(
            name='delevent',
            value='Delete an event\n'
                  '`delevent event_id`',
            inline=False
        )
        embed.add_field(
            name='time',
            value='Show current timezones.\n'
                  '`time`',
            inline=False
        )
        embed.add_field(
            name='mytime',
            value='Show an event in a specified timezone.\n'
                  '`mytime event_id timezone`',
            inline=False
        )
        embed.add_field(
            name='notify',
            value='Tell Artemis to notify you when an event is less than one hour from beginning.\n'
                  '`notify event_id`',
            inline=False
        )
        await ctx.author.send(embed=embed)
        print('Artemis: Sent help to {0}'.format(ctx.author))


def setup(client):
    client.add_cog(Help(client))
