import discord
from artemis import load_db
from discord.ext.commands import CommandNotFound
from discord.ext import commands


class Mod:
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def emoji(self, ctx):
        emojis = ctx.guild.emojis
        print("Guild Emoji List:")
        for value in emojis:
            print(value)

    @commands.command(aliases=['spam'])
    # @commands.has_any_role('mod', 'Moderators', 'moderator', 'moderators')
    async def botspam(self, ctx, *, channel: str):
        conn, c = await load_db()
        channel = discord.utils.get(ctx.guild.channels, name=channel)
        with conn:
            c.execute("UPDATE guilds SET spam = (:spam) WHERE id = (:id)", {'spam': channel.id, 'id': ctx.guild.id})
        msg = '{0} changed the botspam channel. It is now {1.mention}'.format(ctx.author.name, channel)
        await ctx.send(msg, delete_after=10)
        await self.spam(ctx, msg)

    async def spam(self, ctx, message):
        conn, c = await load_db()
        c.execute("SELECT guild, spam FROM guilds WHERE id = (:id)", {'id': ctx.guild.id})
        guild, spam = c.fetchone()
        if spam is not None:
            embed = discord.Embed(color=discord.Color.blue())
            embed.add_field(name='Alert', value=message)
            channel = self.client.get_channel(spam)
            await channel.send(embed=embed)

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

    @staticmethod
    async def on_command_error(ctx, error):
        if isinstance(error, CommandNotFound):
            conn, c = await load_db()
            c.execute("SELECT response FROM bot_responses WHERE message_type = 'error_response'")
            error_response = [value[0] for value in c.fetchall()]
            await ctx.send(error_response)

    @prefix.error
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


def setup(client):
    client.add_cog(Mod(client))
