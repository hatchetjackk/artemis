#! python3

import discord
import asyncio
import datetime
import os
import json
import credentials
from karma import Karma
from emotional_core import Emotions
from itertools import cycle
from discord.ext import commands

token = credentials.tkn()
client = commands.Bot(command_prefix='!')
os.chdir(credentials.home_dir())
client.remove_command('help')
extensions = ['mod', 'karma', 'fun',
              'emotional_core', 'arena', 'user']


@client.event
async def on_ready():
    # log login
    print("{0:<15} {1}".format("Logged in as", client.user.name))
    print("{0:<15} {1}".format("User ID:", client.user.id))
    print("---------------------------------------")
    now = datetime.datetime.now()
    print("[{0}] Artemis is online.".format(now))

    # tell a channel that Artemis has logged in
    responses = ["Artemis is online.",
                 "Artemis is ready.",
                 "Artemis, reporting in.",
                 "Artemis, logging in."]
    # report in to botspam for all servers
    spam = ['botspam']
    channels = client.get_all_channels()
    for channel in channels:
        ch = channel.name
        if ch in spam:
            pass
            # await client.send_message(channel, random.choice(responses))


@client.event
async def on_resumed():
    print("Artemis: Back online")
    await client.send_message(discord.Object(id="477966302871289866"), "Artemis is back online.")


@client.event
async def on_error(event):
    now = datetime.datetime.now()
    print("Artemis: An error has occurred")
    print("[{0}] Error: {1}".format(now, event))
    channel_id = discord.Object(id="493904844592250882")
    await client.send_message(channel_id, "Warning! An error occurred!\nError: {0}".format(event))


@client.event
async def on_member_join(member):
    k = Karma(client)
    server = member.server
    fmt = ["Welcome {0.mention} to {1.name}.\nPlease make yourself at home."]
    await client.send_message(server, fmt.format(member, server))
    role = discord.utils.get(member.server.roles, name="Test Role")
    await client.add_roles(member, role)

    with open('users.json', 'r') as f:
        users = json.load(f)

    await k.update_data(users, member)

    with open('users.json', 'w') as f:
        json.dump(users, f)


@client.event
async def on_message(message):
    k = Karma(client)
    e = Emotions(client)
    with open('users.json', 'r') as f:
        users = json.load(f)
    for member in client.get_all_members():
        await update_data(users, member)
    with open('users.json', 'w') as f:
        json.dump(users, f)

    if not message.content.startswith('!'):
        await k.generate_karma(message)
        await e.generate_points(message)

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
    embed.set_footer(text="Author: Hatchet Jackk")
    await client.send_message(author, embed=embed)
    print('Artemis: Sent help to {0}'.format(author))


async def change_status():
    # Change Artemis' play status every 5 minutes
    await client.wait_until_ready()
    status_response = ['type !help',
                       'with 1\'s and 0\'s',
                       'with fellow humans']
    msg = cycle(status_response)
    while not client.is_closed:
        current_status = next(msg)
        await client.change_presence(game=discord.Game(name=current_status))
        await asyncio.sleep(60*5)


async def on_message_edit(before, after):
    fmt = '**{0.author}** edited their message:\n{1.content}'
    await client.send_message(after.channel, fmt.format(after, before))


async def jreader(f):
    with open(f, 'r') as f:
        data = json.load(f)
    return data


async def jwriter(data, f):
    with open(f, 'w') as f:
        json.dump(data, f)


async def update_data(users, user):
    if user.id not in users:
        users[user.id] = {}
        users[user.id]['karma'] = 0
        users[user.id]['todo'] = []


client.loop.create_task(change_status())


if __name__ == '__main__':
    for extension in extensions:
        try:
            client.load_extension(extension)
        except Exception as error:
            print('{0} cannot be loaded [{1}]'.format(extension, error))

    client.run(token)
