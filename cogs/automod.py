import discord
# import logging
import json
from discord.ext import commands


class Automod:
    def __init__(self, client):
        self.client = client

    @commands.group()
    @commands.has_role('mod')
    async def autorole(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send('Invoke `autorole` with `add` or `remove`.')

    @autorole.group()
    async def set(self, ctx, role):
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
    async def botspam(self, ctx, channel: str):
        guild = ctx.guild
        gid = str(guild.id)

        data = await self.load_guilds()
        if len(channel) < 1:
            await ctx.send('Please use `spamchannel channel_name`.')
        if channel not in [channel.name for channel in ctx.guild.channels]:
            await ctx.send('{} is not a channel.'.format(channel))
            return
        spam = discord.utils.get(guild.channels, name=channel)
        data[gid]['spam'] = spam.id
        await self.dump_guilds(data)
        msg = '{0} changed the botspam channel. It is now {1.mention}'.format(ctx.message.author.name, spam)
        await self.spam(ctx, msg)

    @commands.command()
    @commands.has_role('mod')
    async def clear(self, ctx, amount=2):
        channel = ctx.channel
        messages = []
        async for message in self.client.logs_from(channel, limit=int(amount)):
            messages.append(message)
            await self.client.delete_messages(messages)

    async def on_member_join(self, member):
        # when a member joins, give them an autorole if it exists
        data = await self.load_guilds()
        guild = member.guild
        gid = str(guild.id)

        if data[gid]['auto_role'] is not None:
            role = discord.utils.get(
                member.guild.roles,
                id=data[gid]['auto_role']
            )
            await self.client.add_roles(member, role)
        await self.create_user(member)

        if gid in data:
            if data[gid]['spam'] is not None:
                msg1 = '{0.name} joined {1}.'.format(member, guild)
                msg2 = '{0} was assigned the autorole {1}'.format(member.name, data[gid]['auto_role'])
                embed = discord.Embed(color=discord.Color.blue())
                embed.add_field(
                    name='Alert',
                    value=msg1
                )
                embed.add_field(
                    name='Alert',
                    value=msg2
                )
                channel = self.client.get_channel(data[gid]['spam'])
                await channel.send(embed=embed)

    async def on_message_edit(self, before, after):
        try:
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
            embed.add_field(
                name='Before',
                value=before.content
            )
            embed.add_field(
                name='After',
                value=after.content
            )

            data = await self.load_guilds()
            channel = self.client.get_channel(data[gid]['spam'])
            if channel is None:
                return
            await channel.send(embed=embed)
        except Exception as e:
            print(e)

    async def on_message_delete(self, message):
        guild = message.guild
        gid = str(guild.id)

        if message.author.bot:
            return
        msg = '{0.author.name}\'s message was deleted:\n' \
              '**Channel**: {0.channel.mention}\n' \
              '**Content**: {0.content}'

        data = await self.load_guilds()
        if gid in data:
            if data[gid]['spam'] is not None:
                embed = discord.Embed(color=discord.Color.blue())
                embed.add_field(
                    name='Alert',
                    value=msg.format(message)
                )
                channel = self.client.get_channel(data[gid]['spam'])
                if channel is None:
                    return
                await channel.send(embed=embed)

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
        gid = str(guild.id)

        data = await self.load_guilds()
        if gid in data:
            if data[gid]['spam'] is not None:
                embed = discord.Embed(color=discord.Color.blue())
                embed.add_field(
                    name='Alert',
                    value=message
                )
                channel = self.client.get_channel(data[gid]['spam'])
                await channel.send(embed=embed)

    @autorole.error
    @botspam.error
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
