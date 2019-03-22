import cogs.utilities as utilities
from discord.ext import commands


class Help(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def help(self, ctx):
        conn, c = await utilities.load_db()
        c.execute("SELECT prefix FROM guilds WHERE id = (:id)", {'id': ctx.guild.id})
        prefix = c.fetchone()[0]
        await utilities.single_embed(
            color=utilities.color_help,
            title='Help Menu',
            description=f'Use `{prefix}[command] help` to get help for each command!',
            name='Commands that can use `help`:',
            value='`challonge`, `elite`, `fun`, `karma`, `admin`',
            channel=ctx
        )

    # @staticmethod
    # @help.group()
    # async def embeds(ctx):
    #     embed = discord.Embed(
    #         title='Embeds Help',
    #         color=discord.Color.red()
    #     )
    #     embed.add_field(
    #         name='richembed',
    #         value='Quickly create embeds\n'
    #               '`richembed get`: Get the embed information from a message id.\n'
    #               '`richembed ex`: Get a richembed example and example input.\n'
    #               '`richembed pasta`: Takes richembed input to create a new embed.',
    #         inline=False
    #     )
    #     embed.add_field(
    #         name='colors',
    #         value='Show the list of default Discord colors.\n'
    #               '``colors <optional: full>``',
    #         inline=False
    #     )
    #     await ctx.author.send(embed=embed)
    #     print('Artemis: Sent help to {0}'.format(ctx.author))
    #
    # @staticmethod
    # @help.group()
    # async def events(ctx):
    #     embed = discord.Embed(
    #         title='Events Help',
    #         color=discord.Color.green()
    #     )
    #     embed.add_field(
    #         name='events',
    #         value='Show all events in the guild. New events are UTC by default.\n'
    #               '**Add new events with**: \n'
    #               '`event add h:m day/mnth event_description`\n'
    #               '`event timer int_hours int_minutes event description`\n'
    #               '**Find individual events with**: \n'
    #               '`events find keyword`\n'
    #               '**Update existing events with**:\n'
    #               '`event update event_id h:m day/mnth/year`\n'
    #               '**Delete an event** Only event authors or mods can delete events\n'
    #               '`event delete event_id1 event_id2 ...`',
    #         inline=False
    #     )
    #     embed.add_field(
    #         name='time',
    #         value='Show current timezones.\n'
    #               '`time`',
    #         inline=False
    #     )
    #     # embed.add_field(
    #     #     name='mytime',
    #     #     value='Show an event in a specified timezone.\n'
    #     #           '`mytime event_id timezone`',
    #     #     inline=False
    #     # )
    #     embed.add_field(
    #         name='notify',
    #         value='Tell Artemis to notify you when an event is happening.\n'
    #               '`notify event_id <optional channel_name> <optional time_in_minutes>`\n'
    #               'Example: `!notify 0000 general 20` will notify the user in the #general channel 20 minutes\n'
    #               'before the event starts!',
    #         inline=False
    #     )
    #     await ctx.author.send(embed=embed)
    #     print('Artemis: Sent help to {0}'.format(ctx.author))


def setup(client):
    client.add_cog(Help(client))
