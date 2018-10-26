import json
from discord.ext import commands


class User:
    def __init__(self, client):
        self.client = client

    async def on_member_join(self, member):
        await self.create_user(member)

    async def create_user(self, member):
        guild = member.guild
        gid = str(guild.id)
        mid = str(member.id)
        data_users = await self.load_json('users')
        if mid not in data_users:
            data_users[member.id] = {
                'username': member.name,
                'guild': {},
            }
        if gid not in data_users[mid]['guild']:
            data_users[mid]['guild'].update({gid: guild.name})
        await self.dump_json('users', data_users)

    @staticmethod
    async def load_json(f):
        with open('files/{}.json'.format(f)) as g:
            data = json.load(g)
        return data

    @staticmethod
    async def dump_json(f, data):
        with open('files/{}.json'.format(f), 'w') as g:
            json.dump(data, g, indent=2)

    @staticmethod
    async def on_message_error(ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            msg = ':sob: You\'ve triggered a cool down. Please try again in {} sec.'.format(
                int(error.retry_after))
            await ctx.send(msg)
        if isinstance(error, commands.CheckFailure):
            msg = 'You do not have permission to run this command.'
            await ctx.send(msg)


def setup(client):
    client.add_cog(User(client))
