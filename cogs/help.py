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
            embed.add_field(name="ping", value="Return pong", inline=False)
            embed.add_field(name="roll", value="Roll NdN dice", inline=False)
            embed.add_field(name="playing", value="Check what members are playing `playing PUBG`, `playing all`", inline=False)
            embed.add_field(name='hello', value='Say hi to Artemis!', inline=False)
            embed.add_field(name="status", value="Check Artemis' status", inline=False)
            embed.add_field(name="leaderboard", value="Check karma levels of top 10 users.", inline=False)
            embed.add_field(name="rps choice", value="Play Rock, Paper, Scissors against the bot", inline=False)
            # embed.add_field(name="whois user", value="Find user details", inline=False)
            embed.add_field(name='yt search', value='Return the first YouTube video based for <search>.', inline=False)
            embed.add_field(name='g search', value='Return the first Google result for <search>.', inline=False)
            embed.add_field(name='r/', value='Search for a subreddit `r/nameofsub`.', inline=False)
            embed.add_field(name='help elite', value='See available options for Elite: Dangerous.', inline=False)
            embed.add_field(name='help events', value='See available options for events.', inline=False)
            embed.add_field(name='help embeds', value='See available options for embeds.', inline=False)
            await ctx.author.send(embed=embed)
            print('Artemis: Sent help to {0}'.format(ctx.author.name))

    @staticmethod
    @help.group()
    async def elite(ctx):
        embed = discord.Embed(
            title='Elite: Dangerous Help',
            color=discord.Color.red()
        )
        embed.add_field(name='system',
                        value='Find information about Elite Dangerous systems and stations\n'
                              'Stations in the systems information brief are marked with \n'
                              '[m]arket, [o]utfitting, and [s]hipyard and an abbreviation for\n'
                              'the controlling faction.\n'
                              '`system <system name>`\n'
                              '`system <system name>, <station name>`',
                        inline=False)
        embed.add_field(name='cmdr',
                        value='Find information about a CMDR. This information is taken from INARA\n'
                              'and only reflects that which is updated on the site.\n'
                              '`cmdr hatchet jackk`',
                        inline=False)
        embed.add_field(name='wanted',
                        value='When you run into a bad hombre...\n'
                              'Add CMDRs to or check against the wanted list.\n'
                              '`wanted` to check the list\n'
                              '`wanted add <cmdr name>, <reason for being wanted>`\n'
                              '`wanted remove <cmdr name>`',
                        inline=False)

        await ctx.author.send(embed=embed)

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
                  '`event add h:m day/mnth event_description`\n'
                  '`event timer int_hours int_minutes event description`\n'
                  '**Find individual events with**: \n'
                  '`events find keyword`\n'
                  '**Update existing events with**:\n'
                  '`event update event_id h:m day/mnth/year`\n'
                  '**Delete an event** Only event authors or mods can delete events\n'
                  '`event delete event_id1 event_id2 ...`',
            inline=False
        )
        embed.add_field(
            name='time',
            value='Show current timezones.\n'
                  '`time`',
            inline=False
        )
        # embed.add_field(
        #     name='mytime',
        #     value='Show an event in a specified timezone.\n'
        #           '`mytime event_id timezone`',
        #     inline=False
        # )
        embed.add_field(
            name='notify',
            value='Tell Artemis to notify you when an event is happening.\n'
                  '`notify event_id <optional channel_name> <optional time_in_minutes>`\n'
                  'Example: `!notify 0000 general 20` will notify the user in the #general channel 20 minutes\n'
                  'before the event starts!',
            inline=False
        )
        await ctx.author.send(embed=embed)
        print('Artemis: Sent help to {0}'.format(ctx.author))


def setup(client):
    client.add_cog(Help(client))
