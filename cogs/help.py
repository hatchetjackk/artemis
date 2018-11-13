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
            embed.add_field(name="playing", value="Check what members are playing\n"
                                                  "`playing PUBG`, `playing all`", inline=False)
            embed.add_field(name='hello', value='Say hi to Artemis!', inline=False)
            embed.add_field(name="status", value="Check Artemis' status", inline=False)
            # embed.add_field(name="leaderboard", value="Check karma levels (WIP)", inline=False)
            embed.add_field(name="arena", value="Settle the score (WIP)", inline=False)
            embed.add_field(name="rps choice", value="Play Rock, Paper, Scissors against the bot", inline=False)
            # embed.add_field(name="whois user", value="Find user details", inline=False)
            embed.add_field(name='yt search', value='Return the first YouTube video based for <search>.', inline=False)
            embed.add_field(name='g search', value='Return the first Google result for <search>.', inline=False)
            embed.add_field(name='r/', value='Search for a subreddit `r/nameofsub`.', inline=False)

            embed.add_field(name='help elite', value='See available options for Elite: Dangerous.', inline=False)
            embed.add_field(name='help events', value='See available options for events.', inline=False)
            embed.add_field(name='help embeds', value='See available options for embeds.', inline=False)
            embed.add_field(name='help rpg', value='See available options for role-playing.', inline=False)
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

        await ctx.author.send(embed=embed)

    @staticmethod
    @help.group()
    async def rpg(ctx):
        embed = discord.Embed(
            title='Role-Playing Help',
            color=discord.Color.red()
        )
        embed.add_field(name='duel',
                        value='Duel another member! example: `duel hatchet jackk`\n'
                              '__INFO__: When another member is challenged to a duel, they can `accept` or `deny`.\n'
                              'Dueling another member creates a turn-based 1v1 event. Attack speed is based\n'
                              'on member\'s equipped weight. For example, if a user\'s equipped weight is 5lbs,\n'
                              'the user will take action every 5 turns. Turns are used when the member `attacks` or\n'
                              '`use`s an item.',
                        inline=False)
        embed.add_field(name='raid',
                        value='Fight against an over-powered enemy. example: `raid`\n'
                              '__INFO__: Raids are joint attacks against a single enemy. When a member initiates a raid,\n'
                              'other members can `join` the raid. Once all members have joined, the raid creator \n'
                              'can initiate the raid with `start`. Raids are *not* turn-based. They are real-time\n'
                              'events in which the enemy attacks a random member every x seconds. User actions \n'
                              'are limited to cooldown times for `attack` and `use`. The raid ends either when the \n'
                              'monster reaches 0HP or all members on the raid team reach 0HP.')
        embed.add_field(name='attack',
                        value='Attack a member or monster! example: `attack Hatchet Jackk`\n'
                              '__INFO__: Attacking a member or monster uses the attack roll based on your currently\n'
                              'equipped weapon. For example, a shortsword uses a 1d6 attack die. Additionally, a\n'
                              'hidden 1d20 is rolled to determine critical hits and misses. Critical hits will double\n'
                              'the total roll which is then subtracted from the target\'s HP. If the target is wearing\n'
                              'armor, the attack roll is reduced by the armor\'s defense number.\n'
                              'Guild members cannot be attacked outside of a duel.')
        embed.add_field(name='use',
                        value='Use an item in your inventory! example: `use <item> <target>`\n'
                              '__INFO__: Using an item requires specific syntax especially when activating an item\n'
                              'that is longer than one word. For example, using a healing potion would be activated\n'
                              'with `use healing Hatchet Jackk`. For more items with a space in the item name, use\n'
                              'double quotes. For example, `use "greater healing" Hatchet Jackk`. This will \n'
                              'ensure that you don\'t run into any syntax issues when issuing this command.')
        embed.add_field(name='equip',
                        value='Equip weapons, armors, and accessories from your inventory. example: `equip shortsword`\n'
                              '__INFO__: ')
        embed.add_field(name='unequip',
                        value='Unequip weapons, armors, and accessories from your inventory. example: `unequip weapon`\n'
                              '__INFO__: ')
        embed.add_field(name='inventory',
                        value='Equip weapons, armors, and accessories from your inventory. example: `inventory`\n'
                              '__INFO__: ')
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
                  '`event delete event_id1 event_id2 ...',
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
