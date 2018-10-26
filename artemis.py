#! python3
import os
import discord
import json
import datetime
# import traceback
import logging
from discord.ext import commands

with open('files/guilds.json', 'r') as g:
    guild_data = json.load(g)
with open('files/credentials.json', 'r') as c:
    credentials = json.load(c)

token = credentials['token']
default_prefix = '!'

logging.basicConfig(filename='files/artemis.log', format='%(asctime)s %(message)s', level=logging.INFO)
logging.info('Starting')


async def prefix(bot, message):
    gid = str(message.guild.id)
    return guild_data[gid]['prefix']

client = commands.Bot(command_prefix=prefix)
client.remove_command('help')


@client.event
async def on_ready():
    # log login
    now = datetime.datetime.now()
    print("{0:<15} {1}".format("Logged in as", client.user.name))
    print("{0:<15} {1}".format("Client", client.user.id))
    print('{0:<15} {1}'.format('Discord.py', discord.__version__))
    print("---------------------------------------")
    print("[{0}] Artemis is online.".format(now))

    try:
        for guild in client.guilds:
            if str(guild.id) not in guild_data:
                guild_data[guild.id] = {
                    'guild_name': guild.name,
                    'thumb_url': '',
                    'prefix': '!',
                    'auto_role': None,
                    'mod_roles': [],
                    'spam': None
                }

        with open('files/guilds.json', 'w') as f:
            json.dump(guild_data, f, indent=2)
    except Exception as e:
        print(e)


@client.event
async def on_guild_join(guild):
    gid = str(guild.id)
    if gid not in guild_data:
        guild_data[gid] = {
            'guild_name': guild.name,
            'thumb_url': '',
            'prefix': '!',
            'auto_role': None,
            'mod_roles': [],
            'spam': None
        }
    with open('files/guilds.json', 'w') as f:
        json.dump(guild_data, f, indent=2)

    with open('files/users.json', 'r') as f:
        data_users = json.load(f)

    for member in guild.members:
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

    with open('files/users.json', 'w') as f:
        json.dump(data_users, f, indent=2)


@client.event
async def on_resumed():
    now = datetime.datetime.now()
    message = '[{0}] Artemis is back online.'.format(now)
    print(message)


@client.event
async def on_message(message):

    if message.author.id == client.user.id:
        return
    if not message.content.startswith('!'):
        await update_users(message)

    await client.process_commands(message)


async def update_users(message):
    try:
        guild = message.guild
        gid = str(guild.id)
        with open('files/users.json', 'r') as f:
            data_users = json.load(f)

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

        with open('files/users.json', 'w') as f:
            json.dump(data_users, f, indent=2)
    except Exception as e:
        print(e)
        raise


async def spam(ctx, message):
    data = await load_guilds()
    guild = ctx.guild
    gid = str(guild.id)

    if gid in data:
        if data[gid]['spam'] is not None:
            embed = discord.Embed(color=discord.Color.blue())
            embed.add_field(name='Alert', value=message)
            embed.set_footer(text='Triggered by: {0.name}'.format(ctx.message.author))
            await ctx.Object(id=data[gid]['spam']).send(embed=embed)


async def load_guilds():
    with open('files/guilds.json') as f:
        data = json.load(f)
    return data


async def dump_guilds(data):
    with open('files/guilds.json', 'w') as f:
        json.dump(data, f, indent=2)


if __name__ == '__main__':
    for extension in [f.replace('.py', '') for f in os.listdir('cogs/')]:
        try:
            client.load_extension('cogs.' + extension)
        except Exception as error:
            print('{0} cannot be loaded [{1}]'.format(extension, error))
    client.run(token)
