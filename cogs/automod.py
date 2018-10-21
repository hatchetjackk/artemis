import discord
# import logging
import json
from discord.ext import commands


class Automod:
    def __init__(self, client):
        self.client = client

    @commands.command()
    @commands.has_role('mod')
    async def role(self, ctx, *args):
        # desc that can be accessed by help commands?
        # parent command for other functions
        # data = await self.load_guilds()
        # await self.dump_guilds(data)
        # len(arg) > 1, return error
        # try:
        # await self.arg(ctx)
        # except Exception
        pass

    @commands.group()
    @commands.has_role('mod')
    async def autorole(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send('Invoke `autorole` with `add` or `remove`.')

    @autorole.group()
    async def add(self, ctx, role):
        data = await self.load_guilds()
        guild = ctx.guild
        gid = str(guild.id)
        author = ctx.author
        role = discord.utils.get(guild.roles, name=role)
        try:
            if role in guild.roles:
                data[gid]['auto_role'] = role.id
                await self.dump_guilds(data)
                await ctx.send('The Autorole is now set to `{}`'.format(role))
                msg = '{0} set {1}\'s autorole to *{2}*.'.format(author.name, guild, role)
                await self.spam(ctx, msg)
            else:
                await ctx.ctx.send('{} is not a valid role.'.format(role))
        except Exception as e:
            print(e)

    @autorole.group()
    async def remove(self, ctx):
        data = await self.load_guilds()
        guild = ctx.guild
        author = ctx.author
        try:
            data[guild.id]['auto_role'] = None
            await self.dump_guilds(data)
            await ctx.send('The Autorole has been cleared.')
            msg = '{0} cleared {1}\'s autorole.'.format(author.name, guild)
            await self.spam(ctx, msg)
        except Exception as e:
            print(e)
            raise

    @commands.command()
    @commands.has_role('mod')
    async def spamchannel(self, ctx, *args):
        guild = ctx.guild
        gid = str(guild.id)

        data = await self.load_guilds()
        if len(args) != 1:
            await ctx.send('Please use `spamchannel <channel_name>`.')
        spam = discord.utils.get(guild.channels, name=args[0])
        data[gid]['spam'] = spam.id
        await self.dump_guilds(data)
        msg = 'Spam channel changed. Spam channel is now {0.mention}'.format(spam)
        await self.spam(ctx, msg)

    async def on_member_join(self, member):
        # when a member joins, give them an autorole if it exists
        data = await self.load_guilds()
        if data[member.guild.id]['auto_role'] is not None:
            role = discord.utils.get(member.guild.roles, id=data[member.guild.id]['auto_role'])
            await self.client.add_roles(member, role)
        await self.create_user(member)

        guild = member.guild.id
        if str(guild) in data:
            if data[guild]['spam'] is not None:
                msg1 = '{0.name} joined {1}.'.format(member, member.guild)
                msg2 = '{0} was assigned the autorole {1}'.format(member.name, data[member.guild.id]['auto_role'])
                embed = discord.Embed(color=discord.Color.blue())
                embed.add_field(name='Alert', value=msg1)
                embed.add_field(name='Alert', value=msg2)
                embed.set_footer(text='Triggered by: {0.name}'.format(member))
                await self.client.send_message(discord.Object(id=data[guild]['spam']), embed=embed)

    async def on_message_edit(self, before, after):
        if before.author.bot:
            return

        guild = before.guild
        gid = str(guild.id)

        embed = discord.Embed(
            title='{0} edited a message'.format(after.author.name),
            description='in channel {0.mention}.'.format(after.channel),
            color=discord.Color.blue()
        )
        embed.set_thumbnail(url=after.author.avatar_url)
        embed.add_field(name='Before', value=before.content)
        embed.add_field(name='After', value=after.content)

        data = await self.load_guilds()
        channel = self.client.get_channel(data[gid]['spam'])
        await channel.send(embed=embed)

    async def on_message_delete(self, message):
        if message.author.bot:
            return
        msg = '{0.author.name}\'s message was deleted:\n' \
              '**Channel**: {0.channel.mention}\n' \
              '**Content**: {0.content}'
        embed = discord.Embed(color=discord.Color.blue())
        # embed.set_author(name='{0.message.author}', icon_url='{0.message.author.avatar_url}')
        embed.add_field(name='Alert', value=msg.format(message))
        data = await self.load_guilds()
        guild = message.guild.id
        if str(guild) in data:
            if data[guild]['spam'] is not None:
                await self.client.send_message(discord.Object(id=data[guild]['spam']), embed=embed)

    @staticmethod
    async def create_user(member):
        guild = member.guild
        gid = str(guild.id)
        mid = str(member.id)

        with open('files/users.json', 'r') as f:
            data_users = json.load(f)

        if mid not in data_users:
            data_users[member.id] = {
                'username': member.name,
                'guild': {},
                'karma': 0,
                'karma_cooldown': 0
            }
        if gid not in data_users[mid]['guild']:
            data_users[mid]['guild'].update({gid: guild.name})

        with open('files/users.json', 'w') as f:
            json.dump(data_users, f, indent=2)

    @staticmethod
    async def load_guilds():
        with open('files/guilds.json') as f:
            data = json.load(f)
        return data

    @staticmethod
    async def dump_guilds(data):
        with open('files/guilds.json', 'w') as f:
            json.dump(data, f, indent=2)

    async def spam(self, ctx, message):
        guild = ctx.guild
        author = ctx.author
        gid = str(guild.id)

        data = await self.load_guilds()
        if gid in data:
            if data[gid]['spam'] is not None:
                embed = discord.Embed(color=discord.Color.blue())
                embed.add_field(name='Alert', value=message)
                embed.set_footer(text='Triggered by: {0.name}'.format(author))
                channel = self.client.get_channel(data[gid]['spam'])
                await channel.send(embed=embed)

    @autorole.error
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
