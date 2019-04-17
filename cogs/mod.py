import os
import sys
import time

import aiohttp
import discord
from discord.ext import commands

import cogs.utilities as utilities


class Mod(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.mod_blacklist = []

    @commands.group()
    @commands.is_owner()
    async def admin(self, ctx):
        if ctx.invoked_subcommand is None:
            pass

    @admin.group()
    async def help(self, ctx):
        embed = discord.Embed(color=discord.Color.blue(), title='Admin Help')
        embed.add_field(name='These commands are only accessible by the bot owner!',
                        value='`admin help` This menu!\n'
                              '`admin ping` Issue a verbose ping\n'
                              '`admin guild` Retrieve guild data\n'
                              '`admin clear [num]` Clear x number of messages\n'
                              '`admin stop` Stop Artemis\n'
                              '`admin reboot` Reboot Artemis\n'
                              '`admin emoji` Print server emoji list\n'
                              '`admin gavatar` Print the guild icon url\n'
                              '`admin spam [channel]` Change the guild\'s spam channel\n'
                              '`admin prefix [new_prefix]` Change the guild\'s prefix\n'
                              '`admin autorole [role name]` Set a new autorole\n'
                              '`admin autorole remove` Remove the set autorole\n'
                              '`admin modrole [role name]` Set the moderator role\n'
                              '`admin modrole remove` Remove the moderator role')
        await ctx.send(embed=embed)

    @admin.group()
    async def stop(self, ctx):
        await ctx.send('Artemis shutting down.')
        exit()

    @admin.group(aliases=['restart'])
    async def reboot(self, ctx):
        await ctx.send("Rebooting Artemis.")
        python = sys.executable
        os.execl(python, python, *sys.argv)

    @admin.group()
    async def ping(self, ctx):
        start = time.monotonic()
        before = time.monotonic()
        content = await ctx.send("Pinging..")
        after = time.monotonic()
        ping = round((after - before) * 1000)
        await content.edit(content=f"Pong! \nMessage:`{ping}ms")
        latency = round(self.client.latency * 1000)
        await content.edit(content=f"Pong! \nMessage: `{ping}ms`\nLatency: `{latency}ms`")
        meh = time.monotonic()
        async with aiohttp.ClientSession() as session:
            url = "https://discordapp.com/"
            async with session.get(url) as resp:
                if resp.status is 200:
                    k = time.monotonic()
                    dp = round((k - meh) * 1000)
                    dp = f"`{dp}ms`"
                else:
                    dp = "Failed"
        await content.edit(content=f"Pong! \nMessage: `{ping}ms`\nLatency: `{latency}ms`\nDiscord: {dp}")
        end = time.monotonic()
        ov = round((end - start) * 1000)
        await content.edit(
            content=f"Pong! \nMessage: `{ping}ms`\nLatency: `{latency}ms`\nDiscord: {dp}\nOverall: `{ov}ms`")

    @admin.group(aliases=['emojis'])
    async def emoji(self, ctx):
        emojis = ctx.guild.emojis
        for em in emojis:
            print(em)
        await ctx.send(emojis)

    @admin.group(aliases=['gavatar'])
    async def print_guild_avatar(self, ctx):
        await ctx.send(ctx.guild.icon_url)

    @admin.group(aliases=['spam'])
    async def botspam(self, ctx, *, channel: str):
        conn, c = await utilities.load_db()
        channel = discord.utils.get(ctx.guild.channels, name=channel)
        with conn:
            c.execute("UPDATE guilds SET spam = (:spam) WHERE id = (:id)", {'spam': channel.id, 'id': ctx.guild.id})
        msg = '{0} changed the botspam channel. It is now {1.mention}'.format(ctx.author.name, channel)
        await ctx.send(msg, delete_after=10)
        await self.spam(ctx, msg)

    @admin.group()
    async def prefix(self, ctx, prefix: str):
        if len(prefix) > 1:
            await ctx.send('Please use single character prefixes only.')
            return
        conn, c = await utilities.load_db()
        with conn:
            c.execute("UPDATE guilds SET prefix = (:prefix) WHERE id = (:id)", {'prefix': prefix, 'id': ctx.guild.id})
        await ctx.send('Changed guild prefix to `{}`'.format(prefix))

    @admin.group()
    async def autorole(self, ctx, *, role=None):
        conn, c = await utilities.load_db()
        if role == 'remove':
            with conn:
                c.execute("UPDATE guilds SET autorole = (:autorole) WHERE id = (:id)",
                          {'autorole': None, 'id': ctx.guild.id})
            msg = '{0} cleared {1}\'s autorole.'.format(ctx.author.name, ctx.guild.name)
            await ctx.send(msg, delete_after=5)
            return

        role = discord.utils.get(ctx.guild.roles, name=role)
        if role is None:
            msg = 'Role not found. Please check your spelling. Roles are case-sensitive.'
        else:
            with conn:
                c.execute("UPDATE guilds SET autorole = (:autorole) WHERE id = (:id)",
                          {'autorole': role.id, 'id': ctx.guild.id})
            msg = '{0} set {1}\'s autorole to *{2}*.'.format(ctx.author.name, ctx.guild.name, role.name)
        await ctx.send(msg, delete_after=5)
        await self.spam(ctx, msg)

    @admin.group()
    async def modrole(self, ctx, *, role=None):
        conn, c = await utilities.load_db()
        if role == 'remove':
            with conn:
                c.execute("UPDATE guilds SET mod_role = (:mod_role) WHERE id = (:id)",
                          {'mod_role': None, 'id': ctx.guild.id})
            msg = '{0} cleared {1}\'s mod role.'.format(ctx.author.name, ctx.guild.name)
            await ctx.send(msg, delete_after=5)
            await self.spam(ctx, msg)

        role = discord.utils.get(ctx.guild.roles, name=role)
        if role is None:
            msg = 'Role not found. Please check your spelling. Roles are case-sensitive.'
        else:
            with conn:
                c.execute("UPDATE guilds SET mod_role = (:mod_role) WHERE id = (:id)",
                          {'mod_role': role.id, 'id': ctx.guild.id})
            msg = '{0} set {1}\'s mod role to *{2}*'.format(ctx.author.name, ctx.guild.name, role.name)
        await ctx.send(msg, delete_after=5)
        await self.spam(ctx, msg)

    @admin.group()
    async def clear(self, ctx, amount=0):
        amount = int(amount)
        if 100 < amount or amount < 2:
            embed = await self.msg('`clear [amount]` must be greater than 1 and less than 100.')
            await ctx.send(embed=embed)
        else:
            await ctx.channel.purge(limit=amount+1)

    @commands.command(aliases=['server'])
    async def guild(self, ctx):
        conn, c = await utilities.load_db()
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
        conn, c = await utilities.load_db()
        c.execute("SELECT guild, spam FROM guilds WHERE id = (:id)", {'id': ctx.guild.id})
        guild, spam = c.fetchone()
        if spam is not None:
            embed = discord.Embed(color=discord.Color.blue())
            embed.add_field(name='Alert', value=message)
            channel = self.client.get_channel(spam)
            await channel.send(embed=embed)

    @staticmethod
    async def msg(msg):
        embed = discord.Embed()
        embed.add_field(name='Watch out!',
                        value=msg,
                        inline=False)
        return embed

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
            msg = 'A critical argument is missing from the command. Use `botspam channel_name`.'
            await ctx.send(msg)
        if isinstance(error, commands.CheckFailure):
            msg = 'You do not have permission to run this command.'
            await ctx.send(msg)


def setup(client):
    client.add_cog(Mod(client))
