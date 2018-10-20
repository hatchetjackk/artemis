import discord
# import logging
import json
from discord.ext import commands


class Automod:
    def __init__(self, client):
        self.client = client

    @commands.command()
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

    @commands.command()
    async def autorole(self, ctx, *args):
        guild = ctx.guild
        author = ctx.author

        # allow a user to set the autorole for when members join
        data = await self.load_guilds()
        if args[0] == 'add':
            role = discord.utils.get(guild.roles, name=args[1])
            try:
                if role in guild.roles:
                    data[guild.id]['auto_role'] = role.id
                    await self.dump_guilds(data)
                    await ctx.send('The Autorole is now set to `{}`'.format(role))
                    msg = '{0} set {1}\'s autorole to {2}.'.format(author.name, guild, role)
                    await self.spam(ctx, msg)
                else:
                    await ctx.ctx.send('{} is not a valid role.'.format(role))
            except Exception as e:
                print(e)
        elif args[0] == 'del':
            data[guild.id]['auto_role'] = None
            await self.dump_guilds(data)
            await ctx.send('The Autorole has been cleared.')
            msg = '{0} cleared {1}\'s autorole.'.format(author.name, guild)
            await self.spam(ctx, msg)
        else:
            await ctx.send('{} is not a valid command.'.format(args[0]))

    @commands.command()
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
        if after.author.bot:
            return
        data = await self.load_guilds()
        embed = discord.Embed(title='{0} edited a message in #{1}'.format(after.author.name, after.channel.name),
                              color=discord.Color.blue())
        embed.set_thumbnail(url=after.author.avatar_url)
        embed.add_field(name='Before', value=before.content)
        embed.add_field(name='After', value=after.content)
        channel = data[after.guild.id]['spam']
        await self.client.send_message(discord.Object(id=channel), embed=embed)
        await self.client.send_message(channel, 'yee')

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
        with open('files/users.json', 'r') as f:
            data_users = json.load(f)
        if member.id not in data_users:
            data_users[member.id] = {
                'username': member.name,
                'guild': [],
                'karma': 0,
            }
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


def setup(client):
    client.add_cog(Automod(client))
