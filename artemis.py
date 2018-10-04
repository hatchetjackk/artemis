#! python3

import discord
import asyncio
import os
import json
import datetime
import logging
from files import credentials
import random
from cogs.karma import Karma
from cogs.emotional_core import Emotions
from itertools import cycle
from discord.ext import commands

with open('files/bot.json', 'r') as jf:
    bot = json.load(jf)
command_prefix = bot['artemis']['prefix']

# todo check logging
logging.basicConfig(filename='artemis.log', format='%(asctime)s %(message)s', level=logging.DEBUG)
logging.info('Starting')

token = credentials.tkn()
client = commands.Bot(command_prefix=command_prefix)
os.chdir(credentials.home_dir())
client.remove_command('help')
extensions = ['cogs.mod', 'cogs.karma', 'cogs.fun',
              'cogs.emotional_core', 'cogs.arena', 'cogs.user']

verbose = False


@client.event
async def on_ready():
    # log login
    now = datetime.datetime.now()
    print("{0:<15} {1}".format("Logged in as", client.user.name))
    print("{0:<15} {1}".format("User ID:", client.user.id))
    print("---------------------------------------")
    print("[{0}] Artemis is online.".format(now))

    # tell a channel that Artemis has logged in
    responses = ["Artemis is online.",
                 "Artemis is ready.",
                 "Artemis, reporting in.",
                 "Artemis, logging in."]
    # report in to botspam for all servers
    if verbose:
        await botspam(random.choice(responses))


@client.event
async def on_resumed():
    now = datetime.datetime.now()
    message = '[{0}] Artemis is back online.'.format(now)
    print(message)
    if verbose:
        await botspam(message)


@client.event
async def on_error(event):
    now = datetime.datetime.now()
    message = "An error has occurred.\n[{0}] Error: {1}".format(now, event)
    print(message)
    if verbose:
        await botspam(message)


@client.event
async def on_member_join(member):
    server = member.server
    fmt = ["Welcome {0.mention} to {1.name}.\nPlease make yourself at home."]
    await client.send_message(server, fmt.format(member, server))
    role = discord.utils.get(member.server.roles, name="Test Role")
    await client.add_roles(member, role)

    jfile = 'users.json'
    with open(jfile, 'r') as f:
        users = json.load(f)

    await update_data(users, member, member.server)

    with open(jfile, 'w') as f:
        json.dump = (users, f)


@client.event
async def on_message(message):
    k = Karma(client)
    e = Emotions(client)
    srv = str(message.server)
    with open('files/users.json', 'r') as f:
        users = json.load(f)
    # members = [member for member in message.server.members]
    # for member in members:
    for member in message.server.members:
        await update_data(users, member, srv)
    with open('files/users.json', 'w') as f:
        json.dump(users, f)

    if not message.content.startswith('!'):
        await k.generate_karma(message)
        await e.generate_points(message)

    bot_kudos = ['good bot', 'good job bot', 'good job, bot',
                 'good artemis', 'thanks artemis', 'thank you, artemis',
                 'good, artie', 'good artie']
    bad_bot = ['bad bot', 'bad artie', 'bad artemis', 'damnit artie',
               'damn it, artemis', 'you suck, Artemis']
    for value in bot_kudos:
        if value in message.content.lower():
            responses = ['I try!', 'I do it for the kudos!', ':wink:'
                         'Appreciate it!', 'You got it!', ':smile:', 'Yeet!']
            await client.send_message(message.channel, random.choice(responses))
    for value in bad_bot:
        if value in message.content.lower():
            responses = [':sob:', ':cry:', 'Oh... ok', 'S-sorry.']
            await client.send_message(message.channel, random.choice(responses))

    await client.process_commands(message)


@client.command(pass_context=True)
async def help(ctx):
    author = ctx.message.author
    embed = discord.Embed(
        color=discord.Color.blue()
    )
    embed.set_author(name="Help Page")
    embed.add_field(
        name="How do I give karma?",
        value="Just say thanks and mention the target\n"
              "Ex: 'Thanks @Hatchet Jackk'",
        inline=False)
    embed.add_field(name="!ping", value="Return pong", inline=False)
    embed.add_field(name="!roll", value="Roll NdN dice", inline=False)
    embed.add_field(name="!karma <user>", value="Check your or another <user>'s current level of karma", inline=False)
    embed.add_field(name='!hello', value='Say hi to Artemis!', inline=False)
    embed.add_field(name="!status", value="Check Artemis' status", inline=False)
    embed.add_field(name="!leaderboard", value="Check karma levels (WIP)", inline=False)
    embed.add_field(name="!arena", value="Settle the score (WIP)", inline=False)
    embed.add_field(name="!flip", value="Flip a coin", inline=False)
    embed.add_field(name="!rps <choice>", value="Play Rock, Paper, Scissors against the bot", inline=False)
    embed.add_field(name="!whois <user>", value="Find user details (WIP)", inline=False)
    embed.add_field(name="!server", value="Check server information (WIP)", inline=False)
    embed.add_field(name='!yt <search>', value='Return the first YouTube video based for <search>.', inline=False)
    embed.set_footer(text="Author: Hatchet Jackk")
    await client.send_message(author, embed=embed)
    print('Artemis: Sent help to {0}'.format(author))


async def change_status():
    # Change Artemis' play status every 5 minutes
    await client.wait_until_ready()
    status_response = ['type !help',
                       'with 1\'s and 0\'s',
                       'with fellow humans',
                       'with infinite loops',
                       'with Python']
    msg = cycle(status_response)
    while not client.is_closed:
        current_status = next(msg)
        await client.change_presence(game=discord.Game(name=current_status))
        await asyncio.sleep(60*5)


async def on_message_edit(before, after):
    message = '**{0.author}** edited their message:\n{1.content}'
    if verbose:
        await botspam(message.format(after, before))


async def update_data(users, user, srv):
    if user.id not in users:
        users[user.id] = {}
        users[user.id]['server'] = []
        users[user.id]['karma'] = 0
        users[user.id]['todo'] = []
    if srv not in users[user.id]['server']:
        users[user.id]['server'].append(srv)


async def botspam(message):
    spam = ['botspam']
    for channel in [channel.name for channel in client.get_all_channels()]:
        if channel in spam:
            await client.send_message(channel, message)


client.loop.create_task(change_status())


if __name__ == '__main__':
    for extension in extensions:
        try:
            client.load_extension(extension)
        except Exception as error:
            print('{0} cannot be loaded [{1}]'.format(extension, error))
    client.run(token)
