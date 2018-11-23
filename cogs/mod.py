import discord
from artemis import load_db
from discord.ext import commands


class Mod:
    def __init__(self, client):
        self.client = client
        self.mod_blacklist = []

    @commands.command()
    async def emoji(self, ctx):
        emojis = ctx.guild.emojis
        print("Guild Emoji List:")
        for value in emojis:
            print(value)

    @commands.command()
    async def print_guild_avatar(self, ctx):
        print(ctx.guild.icon_url)

    @commands.command(aliases=['spam'])
    async def botspam(self, ctx, *, channel: str):
        conn, c = await load_db()
        channel = discord.utils.get(ctx.guild.channels, name=channel)
        with conn:
            c.execute("UPDATE guilds SET spam = (:spam) WHERE id = (:id)", {'spam': channel.id, 'id': ctx.guild.id})
        msg = '{0} changed the botspam channel. It is now {1.mention}'.format(ctx.author.name, channel)
        await ctx.send(msg, delete_after=10)
        await self.spam(ctx, msg)

    @commands.command()
    @commands.is_owner()
    async def prefix(self, ctx, prefix: str):
        if len(prefix) > 1:
            await ctx.send('Please use single character prefixes only.')
            return
        conn, c = await load_db()
        with conn:
            c.execute("UPDATE guilds SET prefix = (:prefix) WHERE id = (:id)", {'prefix': prefix, 'id': ctx.guild.id})
        await ctx.send('Changed guild prefix to `{}`'.format(prefix))

    @commands.command()
    async def autorole(self, ctx, command=None, *, role=None):
        if command is None:
            await ctx.send('Invoke `autorole` with `add <role>` or `remove`.')

        if command in ('remove', 'delete'):
            conn, c = await load_db()
            with conn:
                c.execute("UPDATE guilds SET autorole = (:autorole) WHERE id = (:id)",
                          {'autorole': None, 'id': ctx.guild.id})
            msg = '{0} cleared {1}\'s autorole.'.format(ctx.author.name, ctx.guild.name)
            await ctx.send(msg, delete_after=5)
            await self.spam(ctx, msg)

        if command in ('add', 'set'):
            role = discord.utils.get(ctx.guild.roles, name=role)
            if role is None:
                msg = 'Role not found. Please check your spelling. Roles are case-sensitive.'
            else:
                conn, c = await load_db()
                with conn:
                    c.execute("UPDATE guilds SET autorole = (:autorole) WHERE id = (:id)",
                              {'autorole': role.id, 'id': ctx.guild.id})
                msg = '{0} set {1}\'s autorole to *{2}*.'.format(ctx.author.name, ctx.guild.name, role.name)
            await ctx.send(msg, delete_after=5)
            await self.spam(ctx, msg)

    @commands.command()
    async def modrole(self, ctx, command=None, *, role=None):
        if command is None:
            await ctx.send('Invoke `modrole` with `set <role>` or `remove`.')
        if command in ('remove', 'delete'):
            conn, c = await load_db()
            with conn:
                c.execute("UPDATE guilds SET mod_role = (:mod_role) WHERE id = (:id)",
                          {'mod_role': None, 'id': ctx.guild.id})
            msg = '{0} cleared {1}\'s mod role.'.format(ctx.author.name, ctx.guild.name)
            await ctx.send(msg, delete_after=5)
            await self.spam(ctx, msg)

        if command in ('add', 'set'):
            role = discord.utils.get(ctx.guild.roles, name=role)
            if role is None:
                msg = 'Role not found. Please check your spelling. Roles are case-sensitive.'
            else:
                conn, c = await load_db()
                with conn:
                    c.execute("UPDATE guilds SET mod_role = (:mod_role) WHERE id = (:id)",
                              {'mod_role': role.id, 'id': ctx.guild.id})
                msg = '{0} set {1}\'s mod role to *{2}*'.format(ctx.author.name, ctx.guild.name, role.name)
            await ctx.send(msg, delete_after=5)
            await self.spam(ctx, msg)

    @commands.command(aliases=['server'])
    async def guild(self, ctx):
        conn, c = await load_db()
        c.execute("SELECT guild, mod_role, autorole, prefix FROM guilds WHERE id = (:id)", {'id': ctx.guild.id})
        guild, mod_role, autorole, prefix = c.fetchone()
        autorole = discord.utils.get(ctx.guild.roles, id=autorole)
        fmt = (mod_role, autorole, prefix)
        embed = discord.Embed(title='Data for {}'.format(guild),
                              color=discord.Color.blue(),
                              description='Moderator Role: {}\n'
                                          'Auto Role: {}\n'
                                          'Artemis Prefix: `{}`'.format(*fmt))
        await ctx.send(embed=embed)

    async def spam(self, ctx, message):
        conn, c = await load_db()
        c.execute("SELECT guild, spam FROM guilds WHERE id = (:id)", {'id': ctx.guild.id})
        guild, spam = c.fetchone()
        if spam is not None:
            embed = discord.Embed(color=discord.Color.blue())
            embed.add_field(name='Alert', value=message)
            channel = self.client.get_channel(spam)
            await channel.send(embed=embed)

    @prefix.error
    @modrole.error
    @botspam.error
    async def on_message_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            msg = 'You\'ve triggered a cool down. Please try again in {} sec.'.format(int(error.retry_after))
            await ctx.send(msg)
        if isinstance(error, commands.CheckFailure):
            msg = 'You do not have permission to run this command.'
            await ctx.send(msg)
        if isinstance(error, commands.MissingRequiredArgument):
            msg = 'A critical argument is missing from the command.'
            await ctx.send(msg)
        if isinstance(error, commands.CheckFailure):
            msg = 'You do not have permission to run this command.'
            await ctx.send(msg)


def setup(client):
    client.add_cog(Mod(client))
