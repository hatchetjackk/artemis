import json
import random
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
        for value in emojis:
            print(value)

    @commands.command(aliases=['spam'])
    # @commands.has_any_role('mod', 'Moderators', 'moderator', 'moderators')
    async def botspam(self, ctx, *, channel: str):
        conn, c = await load_db()
        channel = discord.utils.get(ctx.guild.channels, name=channel)
        with conn:
            c.execute("UPDATE guilds SET spam = (:spam) WHERE id = (:id)",
                      {'spam': channel.id, 'id': ctx.guild.id})
        msg = '{0} changed the botspam channel. It is now {1.mention}'.format(ctx.author.name, channel)
        await self.spam(ctx, msg)

    async def spam(self, ctx, message):
        conn, c = await load_db()
        c.execute("SELECT spam FROM guilds WHERE id = (?)", (ctx.guild.id,))
        spam = c.fetchone()[0]
        if spam is not None:
            embed = discord.Embed(color=discord.Color.blue())
            embed.add_field(name='Alert', value=message)
            channel = self.client.get_channel(spam)
            await channel.send(embed=embed)

    @commands.command()
    # @commands.is_owner()
    async def prefix(self, ctx, prefix: str):
        conn, c = await load_db()
        with conn:
            c.execute("UPDATE guilds SET prefix = (?) WHERE id = (?)", (prefix, ctx.guild.id))
        await ctx.send('Changed guild prefix to {}'.format(prefix))

    @staticmethod
    async def on_command_error(ctx, error):
        if isinstance(error, CommandNotFound):
            with open('files/status.json') as f:
                data = json.load(f)
            msg = data['bot']['error_response']
            await ctx.send(random.choice(msg))

    @prefix.error
    async def on_message_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            msg = ':sob: You\'ve triggered a cool down. Please try again in {} sec.'.format(
                int(error.retry_after))
            await ctx.send(msg)
        if isinstance(error, commands.CheckFailure):
            msg = 'You do not have permission to run this command.'
            await ctx.send(msg)


def setup(client):
    client.add_cog(Mod(client))
