import json
import sqlite3
# import aiosqlite
from datetime import datetime

import discord

# generate helpful colors forda embeds
color_alert = discord.Color.red()
color_info = discord.Color.blue()
color_help = discord.Color.green()
color_empty = discord.Color.dark_grey()
color_elite = discord.Color.orange()

with open('files/credentials.json') as f:
    credentials = json.load(f)
username = credentials['challonge']['username']
api = credentials['challonge']['API']
thumb = credentials['challonge']['thumb']
inara_api = credentials['inara']


async def fetch(session, url):
    """

    :param session:
    :param url:
    :return:
    """
    async with session.get(url) as response:
        return await response.text()


async def post(session, url, payload):
    """

    :param session:
    :param url:
    :param payload:
    :return:
    """
    async with session.post(url, json=payload) as response:
        return await response.text()


async def err_embed(color=color_alert, url=None, title='Error', thumb_url=None, name=None, value=None, channel=None,
                    delete_after=None):
    """
    generate an embed and send it to the current channel if possible, otherwise send it to the spam channel.
    These are high priority alerts that should be displayed whether the spam channel exists or not
    :param color: typically orange but can be overridden
    :param url: an url to link in the title if necessary
    :param title: the title for the embed.
    :param thumb_url: an image that can be displayed
    :param name: mandatory context displayed above value. /u200b can be passed for an empty value
    :param value: mandatory body of the embed.
    :param channel: the channel that the embed should be displayed in. Typically spam
    :param delete_after: Delete the embed after n seconds.
    :return:
    """

    embed = discord.Embed(color=color, title=title, url=url)
    if thumb_url is not None:
        embed.set_thumbnail(url=thumb_url)
    embed.add_field(name=name, value=value, inline=False)
    spam_channel_id = await get_spam_channel(channel.guild.id)
    if channel is not None:
        await channel.send(embed=embed, delete_after=delete_after)
    elif spam_channel_id is not None:
        spam_channel = channel.guild.get_channel(spam_channel_id)
        await spam_channel.send(embed=embed)
    else:
        pass
    print(f'[{datetime.now()}] An error was caught in {channel.name}. {name}: {value}')


async def alert_embed(color=color_alert, url=None, title='Alert', thumb_url=None, name=None, value=None, obj=None,
                      delete_after=None):
    """
    generate an embed and send it to the spam channel. If the spam channel does not exist, drop the message.
    These types of embeds are best for general botspam (message edits, deletes, user joins, etc)

    :param color:
    :param url:
    :param title:
    :param thumb_url:
    :param name:
    :param value:
    :param obj: An object in the function (ie ctx, member)
    :param delete_after:
    :return:
    """

    spam_channel_id = await get_spam_channel(obj.guild.id)
    if spam_channel_id is not None:
        spam_channel = obj.guild.get_channel(spam_channel_id)
        embed = discord.Embed(color=color, title=title, url=url)
        if thumb_url is not None:
            embed.set_thumbnail(url=thumb_url)
        embed.add_field(name=name, value=value, inline=False)
        await spam_channel.send(embed=embed, delete_after=delete_after)
    print(f'[{datetime.now()}] An error was caught. {name}: {value}')


async def multi_embed(color=color_info, url=None, title=None, description=None, thumb_url=None, messages=None,
                      channel=None, footer=None, delete_after=None):
    """
    Send multiple messages in a single embed. These are typically informative embeds resulting from user interactions.

    :param color: change the color of the embed
    :param url: give the embed title a named link
    :param title: embed title
    :param description: embed description
    :param thumb_url: add a thumb image to the embed
    :param messages: messages must be a list consisting of [[name, value], [name, value]...]
    :param channel: the channel that the embed posts to. Typically ctx
    :param footer: Text that appears at the bottom of the embed
    :param delete_after:
    :return:
    """
    # title = title.replace('l', 'w')
    # description = description.replace('l', 'w')

    try:
        embed = discord.Embed(color=color, title=title, url=url, description=description)
        if thumb_url is not None:
            embed.set_thumbnail(url=thumb_url)
        if footer is not None:
            embed.set_footer(text=footer)
        for msg in messages:
            name, value = msg
            # name = name.replace('l', 'w')
            # value = value.replace('l', 'w')
            embed.add_field(name=name, value=value, inline=False)
        await channel.send(embed=embed, delete_after=delete_after)
    except Exception as e:
        print(f'An unexpected error occurred when processing a multi-message embed: {e}')


async def single_embed(color=color_info, url=None, title=None, thumb_url=None, name=None, value=None, channel=None,
                       description=None, footer=None, delete_after=None):
    """
    :param color:
    :param url:
    :param title:
    :param thumb_url:
    :param name:
    :param value:
    :param channel:
    :param description:
    :param footer:
    :param delete_after:
    :return:
    """
    # title = title.replace('l', 'w')
    # description = description.replace('l', 'w')
    try:
        embed = discord.Embed(color=color, title=title, url=url, description=description)
        if thumb_url is not None:
            embed.set_thumbnail(url=thumb_url)
        if name is not None and value is not None:
            embed.add_field(name=name, value=value, inline=False)
        if footer is not None:
            embed.set_footer(text=footer)
        await channel.send(embed=embed, delete_after=delete_after)
    except Exception as e:
        print(f'An unexpected error occurred when processing a single-message embed: {e}')


async def get_spam_channel(guild_id):
    """
    :param guild_id:
    :return:
    """
    conn, c = await load_db()
    c.execute("SELECT spam FROM guilds WHERE gid = (:gid)", {'gid': guild_id})
    spam_channel_id = c.fetchone()[0]
    return spam_channel_id


async def load_db():
    conn = sqlite3.connect('files/artemis.db', detect_types=sqlite3.PARSE_DECLTYPES)
    curs = conn.cursor()
    return conn, curs


async def load_json(load_file):
    """

    :param load_file:
    :return:
    """
    with open('files/{}.json'.format(load_file)) as g:
        data = json.load(g)
    return data


async def dump_json(dump_file, data):
    """

    :param dump_file:
    :param data:
    :return:
    """
    with open('files/{}.json'.format(dump_file), 'w') as g:
        json.dump(data, g, indent=2)


async def new_guild_config(message, client):
    """

    :param message:
    :param client:
    :return:
    """
    # todo create function to give guild owners configuration menu
    # get mod role
    # get auto role
    # get welcome channel
    await single_embed(
        color=color_help,
        title='Welcome to the Artemis configuration screen!',
        description='Please be patient while we walk through the setup process. :heart:',
        channel=message.channel
    )
    # Find or ask for the spam channel
    # spam_channel = await configure_spam_channel(message, client)
    # welcome_channel = await configure_welcome_channel(message, client)
    # modrole = await configure_modrole(message, client)
    # autorole = await configure_autorole(message, client)


async def configure_spam_channel(message, client):
    """

    :param message:
    :param client:
    :return:
    """
    def check(m):
        return m.author == message.author and m.channel == message.channel
    spam = None
    for spam_channel in message.guild.channels:
        if spam_channel.name == 'botspam':
            spam = spam_channel
    if spam is None:
        await single_embed(
            color=color_help,
            title='First, we will find your bot spam channel!',
            description=f'It looks like you dont have a botspam channel.\n'
            'Would you like to add one for me to send all alerts to? [Y/n]',
            channel=message.channel
        )
        response = await client.wait_for('message', check=check)
        yes = ['yes', 'y']
        if response.content in yes:
            while True:
                await single_embed(
                    color=color_help,
                    title=f'What channel would you like me to use for alerts?\n'
                    f'You can enter `skip` to pass.',
                    channel=message.channel
                )
                response = await client.wait_for('message', check=check)
                if response.content == 'skip':
                    break
                elif response.content in message.guild.channels:
                    spam = response.content
                    await single_embed(
                        color=color_help,
                        title=f'Great! I will use {spam.mention} for all alerts.',
                        channel=message.channel
                    )
                    break
                else:
                    await single_embed(
                        color=color_help,
                        title=f'I could not find {response.content}. Please check your spelling.',
                        channel=message.channel
                    )
    else:
        await single_embed(
            color=color_help,
            title='First, we will find your bot spam channel!',
            description=f'It looks like you already have a {spam.name} channel.\n'
            'Would you like send all alerts to that channel? [Y/n]',
            channel=message.channel
        )
        response = await client.wait_for('message', check=check)
        yes = ['yes', 'y']
        if response.content in yes:
            await single_embed(
                color=color_help,
                title=f'Great! I will use {spam.mention} for all alerts.',
                channel=message.channel
            )
        else:
            while True:
                await single_embed(
                    color=color_help,
                    title=f'What channel would you like me to use for alerts?\n'
                    f'You can enter `skip` to pass.',
                    channel=message.channel
                )
                response = await client.wait_for('message', check=check)
                if response.content == 'skip':
                    break
                elif response.content in message.guild.channels:
                    spam = response.content
                    await single_embed(
                        color=color_help,
                        title=f'Great! I will use {spam.mention} for all alerts.',
                        channel=message.channel
                    )
                    break
                else:
                    await single_embed(
                        color=color_help,
                        title=f'I could not find {response.content}. Please check your spelling.',
                        channel=message.channel
                    )
    return spam


async def build_db_tables():
    conn, c = await load_db()
    with conn:
        try:
            c.execute(
                """
                CREATE TABLE IF NOT EXISTS members (
                id INTEGER,
                member_name TEXT,
                karma INTEGER,
                last_karma_given INTEGER,
                UNIQUE(id, member_name)
                )
                """
            )
        except sqlite3.OperationalError:
            raise
        except sqlite3.DatabaseError:
            raise

        try:
            c.execute(
                """CREATE TABLE IF NOT EXISTS guild_members (
                    id INTEGER,
                    guild TEXT,
                    member_id INTEGER,
                    member_name TEXT,
                    member_nick TEXT,
                    UNIQUE(id, guild, member_id)
                    )"""
            )
        except sqlite3.OperationalError:
            raise
        except sqlite3.DatabaseError:
            raise

        try:
            c.execute(
                """CREATE TABLE IF NOT EXISTS guilds (
                    id INTEGER UNIQUE,
                    guild TEXT,
                    mod_role TEXT,
                    autorole TEXT
                    prefix TEXT,
                    spam INTEGER,
                    thumbnail TEXT
                    )"""
            )
        except sqlite3.OperationalError:
            raise
        except sqlite3.DatabaseError:
            raise
