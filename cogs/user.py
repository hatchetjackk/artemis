from artemis import load_json, dump_json
from discord.ext import commands


class User:
    def __init__(self, client):
        self.client = client

    async def on_member_join(self, member):
        await self.create_user(member)

    async def on_message(self, message):
        if message.author.id == self.client.user.id:
            return
        if not message.content.startswith('!'):
            await self.update_users(message)

    @staticmethod
    async def update_users(message):
        try:
            guild = message.guild
            gid = str(guild.id)
            data_users = await load_json('users')

            for member in message.guild.members:
                mid = str(member.id)
                if mid not in data_users:
                    data_users[mid] = {
                        'username': member.name,
                        'guild': {},
                    }
                if 'hp' in data_users[mid]:
                    data_users[mid].pop('hp')
                if 'health' not in data_users[mid]:
                    data_users[mid].update({'health': {'hp': 100, 'mp': 100}})
                if 'inventory' not in data_users[mid]:
                    data_users[mid].update({'inventory': {
                        'gold': 10,
                        'healing': 5,
                        'revive': 2
                    }})
                if 'equipped' not in data_users[mid]:
                    data_users[mid].update({'equipped': {
                        'weapon': None,
                        'armor': None,
                        'acc.': None}
                    })
                data_users[mid].update({'username': member.name})
                data_users[mid]['guild'].update({gid: {guild.name: member.nick}})
            await dump_json('users', data_users)

        except Exception as e:
            print(e)
            raise

    @staticmethod
    async def create_user(member):
        try:
            guild = member.guild
            gid = str(guild.id)
            mid = str(member.id)
            data_users = await load_json('users')
            if mid not in data_users:
                data_users[member.id] = {
                    'username': member.name,
                    'guild': {},
                }
            if gid not in data_users[str(member.id)]['guild']:
                data_users[str(member.id)]['guild'].update({gid: guild.name})
            if 'health' not in data_users[mid]:
                data_users[mid]['health'].update({'hp': 100, 'mp': 100})
            if 'inventory' not in data_users[mid]:
                data_users[mid]['inventory'].update({})
            if 'equipped' not in data_users[mid]:
                data_users[mid]['equipped'].update({'weapon': None,
                                                    'armor': None,
                                                    'Acc.': None})
            await dump_json('users', data_users)
        except KeyError as e:
            print('KeyError: {} when creating user. {}'.format(str(member.id), e))

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
