import discord
from artemis import load_db
from discord.ext import commands


class Automod:
    def __init__(self, client):
        self.client = client
        self.auto_mod_blacklist = ['Knights of Karma', 'Aurora Corporation']

    @commands.command()
    async def roles(self, ctx):
        for role in ctx.guild.roles:
            await ctx.send(role)

    @commands.command()
    @commands.has_any_role('Moderator', 'mod')
    async def clear(self, ctx, amount: int):
        if 100 < amount or amount < 2:
            await ctx.send('Amount must be between 1 and 100.')
            return
        await ctx.channel.purge(limit=amount+1)

    @staticmethod
    async def on_member_join(member):
        # when a member joins, give them an autorole if it exists
        conn, c = await load_db()
        with conn:
            c.execute("SELECT autorole FROM guilds WHERE id = (:id)", {'id': member.guild.id})
            autorole = c.fetchone()[0]
            role = discord.utils.get(member.guild.roles, id=autorole)
            if role is not None:
                await member.add_roles(role)
            c.execute("SELECT spam FROM guilds WHERE id = (?)", (member.guild.id,))
            spam = c.fetchone()[0]
            if spam is not None:
                msg1 = '{0.name} joined {1}.'.format(member, member.guild)
                msg2 = '{0} was assigned the autorole {1}'.format(member.name, role)
                embed = discord.Embed(color=discord.Color.blue())
                embed.set_thumbnail(url=member.avatar_url)
                embed.add_field(name='Alert', value=msg1, inline=False)
                embed.add_field(name='Alert', value=msg2, inline=False)
                channel = member.guild.get_channel(spam)
                await channel.send(embed=embed)
        channel = discord.utils.get(member.guild.channels, name='general')
        await channel.send('Welcome to {}, {}!'.format(member.guild.name, member.name))

    @staticmethod
    async def on_member_remove(member):
        conn, c = await load_db()
        with conn:
            c.execute("SELECT spam FROM guilds WHERE id = (?)", (member.guild.id,))
            spam = c.fetchone()[0]
            if spam is not None:
                msg = '{0.name} has left {1}.'.format(member, member.guild)
                embed = discord.Embed(color=discord.Color.blue())
                embed.add_field(name='Alert', value=msg, inline=False)
                channel = member.guild.get_channel(spam)
                await channel.send(embed=embed)

    async def on_message_edit(self, before, after):
        if before.guild in self.auto_mod_blacklist:
            return
        if before.author.bot:
            return
        try:
            embed = discord.Embed(title='{0} edited a message'.format(after.author.name),
                                  description='in channel {0.mention}.'.format(after.channel),
                                  color=discord.Color.blue())
            embed.set_thumbnail(url=after.author.avatar_url)
            embed.add_field(name='Before', value=before.content, inline=False)
            embed.add_field(name='After', value=after.content, inline=False)

            conn, c = await load_db()
            c = conn.cursor()
            with conn:
                c.execute("SELECT spam FROM guilds WHERE id = (:id)", {'id': before.guild.id})
                spam_id = c.fetchone()[0]
                if spam_id is None:
                    return
                spam = before.guild.get_channel(spam_id)
            await spam.send(embed=embed)
        except Exception as e:
            print('Error on message edit: {}'.format(e))
            raise

    @staticmethod
    async def on_message_delete(message):
        if message.author.bot:
            return
        msg = '{0.author.name}\'s message was deleted:\n' \
              '**Channel**: {0.channel.mention}\n' \
              '**Content**: {0.content}'

        conn, c = await load_db()
        with conn:
            c.execute("SELECT spam FROM guilds WHERE id = (?)", (message.guild.id,))
            spam = c.fetchone()[0]
            if spam is not None:
                embed = discord.Embed(color=discord.Color.blue())
                embed.add_field(name='Alert', value=msg.format(message))
                channel = message.guild.get_channel(spam)
                if channel is None:
                    return
                await channel.send(embed=embed)

    @staticmethod
    async def spam(ctx, message):
        conn, c = await load_db()
        with conn:
            c.execute("SELECT spam FROM guilds WHERE id = (?)", (ctx.guild.id,))
            spam = c.fetchone()[0]
            if spam is not None:
                embed = discord.Embed(color=discord.Color.blue())
                embed.add_field(name='Alert', value=message)
                channel = ctx.guild.get_channel(spam)
                await channel.send(embed=embed)

    # @autorole.error
    # @botspam.error
    @clear.error
    async def on_message_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            msg = ':sob: You\'ve triggered a cool down. Please try again in {} sec.'.format(
                int(error.retry_after))
            await ctx.send(msg)
        if isinstance(error, commands.CheckFailure):
            msg = 'You do not have permission to run this command.'
            await ctx.send(msg)


def setup(client):
    client.add_cog(Automod(client))
