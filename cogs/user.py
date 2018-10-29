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
        # await self.client.process_commands(message)

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
                        'karma': 0,
                        'karma_cooldown': 0
                    }
                if gid not in data_users[mid]['guild']:
                    data_users[mid]['guild'].update({gid: guild.name})
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
