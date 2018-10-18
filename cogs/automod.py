import discord
# import logging
import json
from discord.ext import commands


class Automod:
    def __init__(self, client):
        self.client = client

    @commands.command(pass_context=True)
    async def role(self, ctx, *args):
        # desc that can be accessed by help commands?
        # parent command for other functions
        # data = await self.load_servers()
        # await self.dump_servers(data)
        # len(arg) > 1, return error
        # try:
        # await self.arg(ctx)
        # except Exception
        pass

    @commands.command(pass_context=True)
    async def autorole(self, ctx, *args):
        # allow a user to set the autorole for when members join
        data = await self.load_servers()
        if args[0] == 'add':
            role = discord.utils.get(ctx.message.server.roles, name=args[1])
            try:
                if role in ctx.message.server.roles:
                    data[ctx.message.server.id]['auto_role'] = role.id
                    await self.dump_servers(data)
                    await self.client.send_message(ctx.message.channel, 'The Autorole is now set to `{}`'.format(role))
                    msg = '{0} set {1}\'s autorole to {2}.'.format(ctx.message.author.name, ctx.message.server, role)
                    await self.spam(ctx, msg)
                else:
                    await self.client.send_message(ctx.message.channel, '{} is not a valid role.'.format(role))
            except Exception as e:
                print(e)
        elif args[0] == 'del':
            data[ctx.message.server.id]['auto_role'] = None
            await self.dump_servers(data)
            await self.client.send_message(ctx.message.channel, 'The Autorole has been cleared.')
            msg = '{0} cleared {1}\'s autorole.'.format(ctx.message.author.name, ctx.message.server)
            await self.spam(ctx, msg)
        else:
            await self.client.send_message(ctx.message.channel, '{} is not a valid command.'.format(args[0]))

    @commands.command(pass_context=True)
    async def spamchannel(self, ctx, *args):
        data = await self.load_servers()
        if len(args) != 1:
            await self.client.send_message(ctx.message.channel, 'Please use ``spamchannel <channel_name>``.')
        spam = discord.utils.get(ctx.message.server.channels, name=args[0])
        data[ctx.message.server.id]['spam'] = spam.id
        await self.dump_servers(data)
        msg = 'Spam channel changed. Spam channel is now {0.mention}'.format(spam)
        await self.spam(ctx, msg)

    async def on_member_join(self, member):
        # when a member joins, give them an autorole if it exists
        data = await self.load_servers()
        if data[member.server.id]['auto_role'] is not None:
            role = discord.utils.get(member.server.roles, id=data[member.server.id]['auto_role'])
            await self.client.add_roles(member, role)
        await self.create_user(member)

        server = member.server.id
        if str(server) in data:
            if data[server]['spam'] is not None:
                msg1 = '{0.name} joined {1}.'.format(member, member.server)
                msg2 = '{0} was assigned the autorole {1}'.format(member.name, data[member.server.id]['auto_role'])
                embed = discord.Embed(color=discord.Color.blue())
                embed.add_field(name='Alert', value=msg1)
                embed.add_field(name='Alert', value=msg2)
                embed.set_footer(text='Triggered by: {0.name}'.format(member))
                await self.client.send_message(discord.Object(id=data[server]['spam']), embed=embed)

    async def on_message_edit(self, before, after):
        if after.author.bot:
            return
        data = await self.load_servers()
        embed = discord.Embed(title='{0} edited a message in #{1}'.format(after.author.name, after.channel.name),
                              color=discord.Color.blue())
        embed.set_thumbnail(url=after.author.avatar_url)
        embed.add_field(name='Before', value=before.content)
        embed.add_field(name='After', value=after.content)
        channel = data[after.server.id]['spam']
        await self.client.send_message(discord.Object(id=channel), embed=embed)
        await self.client.send_message(channel, 'yee')

    async def on_message_delete(self, message):
        if message.author.bot:
            return
        msg = '{0.author.name} has deleted the message:\n' \
              '**Channel**: {0.channel.mention}\n' \
              '**Content**: {0.content}'
        embed = discord.Embed(color=discord.Color.blue())
        embed.add_field(name='Alert', value=msg.format(message))
        data = await self.load_servers()
        server = message.server.id
        if str(server) in data:
            if data[server]['spam'] is not None:
                await self.client.send_message(discord.Object(id=data[server]['spam']), embed=embed)

    @staticmethod
    async def create_user(member):
        with open('files/users.json', 'r') as f:
            data_users = json.load(f)
        if member.id not in data_users:
            data_users[member.id] = {
                'username': member.name,
                'server': [],
                'karma': 0,
            }
        with open('files/users.json', 'w') as f:
            json.dump(data_users, f, indent=2)

    @staticmethod
    async def load_servers():
        with open('files/servers.json') as f:
            data = json.load(f)
        return data

    @staticmethod
    async def dump_servers(data):
        with open('files/servers.json', 'w') as f:
            json.dump(data, f, indent=2)

    async def spam(self, ctx, message):
        data = await self.load_servers()
        server = ctx.message.server.id
        if str(server) in data:
            if data[server]['spam'] is not None:
                embed = discord.Embed(color=discord.Color.blue())
                embed.add_field(name='Alert', value=message)
                embed.set_footer(text='Triggered by: {0.name}'.format(ctx.message.author))
                await self.client.send_message(discord.Object(id=data[server]['spam']), embed=embed)


def setup(client):
    client.add_cog(Automod(client))
