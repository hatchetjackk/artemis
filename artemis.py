#! python3

import discord
import asyncio
import json
import datetime
# import traceback
import logging
import random
from itertools import cycle
from discord.ext import commands

with open('files/bot.json', 'r') as b:
    bot_data = json.load(b)
command_prefix = bot_data['prefix']
# try:
#     for key, value in server_data.items():
#         if key == discord.Server.id:
#             command_prefix = value['prefix']
# except Exception as e:
#     print(e)
#     sys.exit(1)
with open('files/credentials.json', 'r') as c:
    credentials = json.load(c)
token = credentials['token']

logging.basicConfig(filename='files/artemis.log', format='%(asctime)s %(message)s', level=logging.INFO)
logging.info('Starting')

client = commands.Bot(command_prefix=command_prefix)
client.remove_command('help')
extensions = ['cogs.mod', 'cogs.karma', 'cogs.fun',
              'cogs.emotional_core', 'cogs.arena', 'cogs.user',
              'cogs.events', 'cogs.help', 'cogs.richembeds',
              'cogs.automod']


@client.event
async def on_ready():
    # log login
    now = datetime.datetime.now()
    print("{0:<15} {1}".format("Logged in as", client.user.name))
    print("{0:<15} {1}".format("User ID:", client.user.id))
    print("---------------------------------------")
    print("[{0}] Artemis is online.".format(now))

    # tell a channel that Artemis has logged in
    # responses = ["Artemis is online.",
    #              "Artemis is ready.",
    #              "Artemis, reporting in.",
    #              "Artemis, logging in."]
    # report in to botspam for all servers
    # await botspam(random.choice(responses))
    try:
        with open('files/servers.json') as f:
            data_servers = json.load(f)
        for server in client.servers:
            if str(server.id) not in data_servers:
                data_servers[server.id] = {
                    'server_name': server.name,
                    'thumb_url': '',
                    'prefix': '!',
                    'auto_role': None,
                    'spam': None
                }
        with open('files/servers.json', 'w') as f:
            json.dump(data_servers, f, indent=2)
    except Exception as e:
        print(e)


@client.event
async def on_resumed():
    now = datetime.datetime.now()
    message = '[{0}] Artemis is back online.'.format(now)
    print(message)


@client.event
async def on_error(event):
    now = datetime.datetime.now().strftime('%d/%Y %H:%M')
    msg = "An error has occurred.\n[{0}] Error: {1}".format(now, event)


@client.event
async def on_message(message):
    if message.author.id == client.user.id:
        return
    if not message.content.startswith('!'):
        try:
            await update_users(message)
        except ValueError as e:
            print(e)
        except AttributeError as e:
            print(e)

        bot_kudos = [
            'good bot', 'good job bot', 'good job, bot',
            'good artemis', 'good, artie', 'good artie'
        ]
        bad_bot = [
            'bad bot', 'bad artie', 'bad artemis', 'damnit artie',
            'damn it, artemis', 'you suck, Artemis'
        ]
        for value in bot_kudos:
            if value in message.content.lower():
                responses = [
                    "You're welcome!", "No problem.",
                    "Anytime!", "Sure thing, fellow human!",
                    "*eats karma* Mmm.", 'I try!', 'I do it for the kudos!', ':wink:',
                    'Appreciate it!', 'You got it!', ':smile:', 'Yeet!',
                    '( ͡° ͜ʖ ͡°)'
                ]
                await client.send_message(message.channel, random.choice(responses))
        for value in bad_bot:
            if value in message.content.lower():
                responses = [
                    ':sob:', ':cry:', 'Oh... ok',
                    'S-sorry.', '( ͡° ͜ʖ ͡°)', 'Sowwy onyii-chan'
                ]
                await client.send_message(message.channel, random.choice(responses))

    await client.process_commands(message)


async def change_status():
    # Change Artemis' play status every 5 minutes
    await client.wait_until_ready()
    status_response = [
        'type !help',
        'with 1\'s and 0\'s',
        'with fellow humans',
        'with infinite loops',
        'with Python'
    ]
    msg = cycle(status_response)
    while not client.is_closed:
        current_status = next(msg)
        await client.change_presence(game=discord.Game(name=current_status))
        await asyncio.sleep(60*5)


async def update_users(message):
    with open('files/users.json', 'r') as f:
        data_users = json.load(f)

    for member in message.server.members:
        if member.id not in data_users:
            data_users[member.id] = {
                'username': member.name,
                'server': [],
                'karma': 0,
            }
        if str(message.server) not in data_users[member.id]['server']:
            data_users[member.id]['server'].append(str(message.server))

    with open('files/users.json', 'w') as f:
        json.dump(data_users, f, indent=2)


async def spam(self, ctx, message):
    data = await self.load_servers()
    server = ctx.message.server.id
    if str(server) in data:
        if data[server]['spam'] is not None:
            embed = discord.Embed(color=discord.Color.blue())
            embed.add_field(name='Alert', value=message)
            embed.set_footer(text='Triggered by: {0.name}'.format(ctx.message.author))
            await self.client.send_message(discord.Object(id=data[server]['spam']), embed=embed)


@staticmethod
async def load_servers():
    with open('files/servers.json') as f:
        data = json.load(f)
    return data


@staticmethod
async def dump_servers(data):
    with open('files/servers.json', 'w') as f:
        json.dump(data, f, indent=2)

client.loop.create_task(change_status())

if __name__ == '__main__':
    for extension in extensions:
        try:
            client.load_extension(extension)
        except Exception as error:
            print('{0} cannot be loaded [{1}]'.format(extension, error))
    client.run(token)
