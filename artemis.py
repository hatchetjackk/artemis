#! python3

import discord
import asyncio
import datetime
import random
import karma
import os
import json
import credentials
from itertools import cycle
from discord.ext import commands

token = credentials.tkn()
client = commands.Bot(command_prefix='!')
os.chdir(credentials.home_dir())
client.remove_command('help')
extensions = ['mod', 'karma']


# def username_formatter(username):
#     user1 = '<@!{0}>'.format(username)
#     user2 = '<@{0}>'.format(username)
#     return user1, user2


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
    channel_id = discord.Object(id="477966302871289866")
    await client.send_message(channel_id, random.choice(responses))


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
    server = member.server
    fmt = ["Welcome {0.mention} to {1.name}.\nPlease make yourself at home."]
    await client.send_message(server, fmt.format(member, server))
    role = discord.utils.get(member.server.roles, name="Test Role")
    await client.add_roles(member, role)

    with open('users.json', 'r') as f:
        users = json.load(f)

    await karma.Karma.update_data(users, member)

    with open('users.json', 'w') as f:
        json.dump(users, f)


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
              "Ex: 'Thanks @Hatchet Jackk#4501!",
        inline=False)
    embed.add_field(name="!ping", value="Return pong", inline=False)
    embed.add_field(name="!roll", value="Roll NdN dice", inline=False)
    embed.add_field(name="!karma <user>", value="Check your or another <user>'s current level of karma", inline=False)
    embed.add_field(name='!hello', value='Say hi to Artemis!')
    embed.add_field(name="!status", value="Check Artemis' status", inline=False)
    embed.set_footer(text="Author: Hatchet Jackk")
    embed.set_footer(text='Base: Python3')
    await client.send_message(author, embed=embed)


@client.command(pass_context=True)
async def hello(ctx):
    responses = ["Hi, {0.author.mention}!",
                 "Ahoy, {0.author.mention}!",
                 "Hey there, {0.author.mention}!",
                 "*[insert traditional greeting here]*",
                 "*0100100001000101010011000100110001001111*\nAhem, I mean: hello!",
                 "Hello. Fine weather we're having.",
                 "Hello, fellow human!"]
    msg = random.choice(responses).format(ctx.message)
    await client.send_message(ctx.message.channel, msg)


@client.command(pass_context=True)
async def status(ctx):
    responses = ["Artemis is ok!",
                 "Artemis is currently online.",
                 ":thumbsup:",
                 "No problems, at the moment."]
    await client.send_message(ctx.message.channel, random.choice(responses))


@client.command(pass_context=True)
async def test(ctx):
    counter = 0
    tmp = await client.send_message(ctx.message.channel, "Calculating messages...")
    async for log in client.logs_from(ctx.message.channel, limit=100):
        if log.author == ctx.message.author:
            counter += 1
    await client.edit_message(tmp, "You have {0} messages.".format(counter))


@client.command()
async def ping():
    print("ping/pong")
    await client.say(':ping_pong: Pong')


@client.command()
async def roll(dice: str):
    try:
        rolls, limit = map(int, dice.split('d'))
        print(rolls, limit)
    except Exception as e:
        print(e)
        await client.say('Please use the format "NdN" when rolling dice. Thanks!')
        return
    result = ', '.join(str(random.randint(1, limit)) for value in range(rolls))
    await client.say(result)


# @client.command(pass_context=True)
# async def clear(ctx, amount=2):
#     channel = ctx.message.channel
#     messages = []
#     async for message in client.logs_from(channel, limit=int(amount)):
#         messages.append(message)
#     await client.delete_messages(messages)


# @client.command()
# async def displayembed():
#     # hex colors
#     # int(767,a76, 16)
#     embed = discord.Embed(
#         title="Title",
#         description="Description",
#         color=discord.Color.blue()
#     )
#     embed.set_footer(text="Footer")
#     embed.set_image(url="http://promoboxx.com/compare/images/broken_robot.png")
#     embed.set_thumbnail(url="http://promoboxx.com/compare/images/broken_robot.png")
#     embed.set_author(name="Author Name", icon_url="http://promoboxx.com/compare/images/broken_robot.png")
#     embed.add_field(name="Field Name", value="Field Value", inline=False)
#     await client.say(embed=embed)


@client.command(pass_context=True)
async def karma(ctx):
    """ Check karma points """
    user = ctx.message.author.id
    target = ctx.message.author
    message = ctx.message.content.split()
    members = [member for member in ctx.message.server.members]
    # check another user's karma
    for member in members:
        if member.mention in message:
            target = member.name
            user = member.id
            with open('users.json', 'r') as f:
                users = json.load(f)
                if user in users:
                    points = users[user]['karma']
                    await client.send_message(ctx.message.channel, '{0} has {1} karma.'.format(target, points))
                    return
    # check message author's karma
    with open('users.json', 'r') as f:
        users = json.load(f)
        if user in users:
            points = users[user]['karma']
            await client.send_message(ctx.message.channel, 'You have {1} karma.'.format(target, points))


@client.command()
async def leaderboard():
    """ todo make karma leaderboard with embed """
    pass


@client.command()
async def arena():
    """ todo make duel arena """
    pass


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


async def karma_test():
    # Change Artemis' play status every 5 minutes
    await client.wait_until_ready()
    while not client.is_closed:
        await client.send_message(discord.Object(id="477966302871289866"), "thanks <@193416878717140992>")
        await asyncio.sleep(2)
        await client.send_message(discord.Object(id="477966302871289866"), "thanks <@355055661303988225>")
        await asyncio.sleep(2)

client.loop.create_task(change_status())
# client.loop.create_task(karma_test())

if __name__ == '__main__':
    for extension in extensions:
        try:
            client.load_extension(extension)
        except Exception as error:
            print('{0} cannot be loaded [{1}]'.format(extension, error))

    client.run(token)
