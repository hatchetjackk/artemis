import asyncio
import discord
from _datetime import datetime
import pytz
import json
import random
from discord.ext import commands

""" All times in events are handled as UTC and then converted to set zone times for local reference """


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
                    print('{0} set {1}\'s autorole to {2}.'.format(ctx.message.author.name, ctx.message.server, role))
                else:
                    await self.client.send_message(ctx.message.channel, '{} is not a valid role.'.format(role))
            except Exception as e:
                print(e)
        elif args[0] == 'del':
            data[ctx.message.server.id]['auto_role'] = None
            await self.dump_servers(data)
            await self.client.send_message(ctx.message.channel, 'The Autorole has been cleared.')
            print('{0} cleared {1}\'s autorole.'.format(ctx.message.author.name, ctx.message.server))
        else:
            await self.client.send_message(ctx.message.channel, '{} is not a valid command.'.format(args[0]))

    async def on_member_join(self, member):
        print('{} joined.'.format(member))
        # when a member joins, give them an autorole if it exists
        data = await self.load_servers()
        if data[member.server.id]['auto_role'] is not None:
            role = discord.utils.get(member.server.roles, id=data[member.server.id]['auto_role'])
            await self.client.add_roles(member, role)
            print('{0} was assigned the autorole {1}'.format(member.name, role))

    async def add(self, ctx):
        # desc that can be accessed by help commands?
        # add a new role
        # data = await self.load_servers()
        # if role already exists, return error
        # await self.dump_servers(data)
        pass

    async def delete(self, ctx):
        # desc that can be accessed by help commands?
        # delete an existing role
        # data = await self.load_servers()
        # if role doesn't exist, return error
        # await self.dump_servers(data)
        pass

    async def assign(self, ctx):
        # desc that can be accessed by help commands?
        # assign a user to a role
        # data = await self.load_servers()
        # if role doesn't exist, return error
        # if user already has role, return error
        # await self.dump_servers(data)
        pass

    async def remove(self, ctx):
        # desc that can be accessed by help commands?
        # remove a user to a role
        # data = await self.load_servers()
        # if role doesn't exist, return error
        # if user doesn't have the role, return error
        # await self.dump_servers(data)
        pass

    @staticmethod
    async def load_servers():
        with open('files/servers.json') as f:
            data = json.load(f)
        return data

    @staticmethod
    async def dump_servers(data):
        with open('files/servers.json', 'w') as f:
            json.dump(data, f, indent=2)


def setup(client):
    client.add_cog(Automod(client))
