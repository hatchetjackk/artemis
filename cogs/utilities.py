import sqlite3
import json
import discord
from datetime import datetime

# generate helpful colors for embeds
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
    async with session.get(url) as response:
        return await response.text()


async def post(session, url, payload):
    async with session.post(url, json=payload) as response:
        return await response.text()


async def err_embed(color=color_alert, url=None, title='Alert', thumb_url=None, name=None, value=None, channel=None,
                    delete_after=None):
    """
    generate an embed and send it to the spam channel if possible, otherwise send it to the specified channel.
    These are high priority alerts that should be displayed whether the spam channel exists or not
    :param color:
    :param url:
    :param title:
    :param thumb_url:
    :param name:
    :param value:
    :param channel:
    :param delete_after:
    :return:
    """

    embed = discord.Embed(color=color, title=title, url=url)
    if thumb_url is not None:
        embed.set_thumbnail(url=thumb_url)
    embed.add_field(name=name, value=value, inline=False)
    spam_channel_id = await get_spam_channel(channel.guild.id)
    if spam_channel_id is not None:
        spam_channel = channel.guild.get_channel(spam_channel_id)
        await spam_channel.send(embed=embed)
    else:
        await channel.send(embed=embed, delete_after=delete_after)
    print(f'[{datetime.now()}] {value}')


async def alert_embed(color=color_alert, url=None, title='Alert', thumb_url=None, name=None, value=None, obj=None,
                      delete_after=None):
    """
    generate and embed and send it to the spam channel. If the spam channel does not exist, drop the message.
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
            # name = name.replace('l', 'w')
            # value = value.replace('l', 'w')
            embed.add_field(name=name, value=value, inline=False)
        if footer is not None:
            embed.set_footer(text=footer)
        await channel.send(embed=embed,delete_after=delete_after)
    except Exception as e:
        print(f'An unexpected error occurred when processing a single-message embed: {e}')


async def get_spam_channel(guild_id):
    conn, c = await load_db()
    c.execute("SELECT spam FROM guilds WHERE id = (:id)", {'id': guild_id})
    spam_channel_id = c.fetchone()[0]
    return spam_channel_id


async def load_db():
    conn = sqlite3.connect('files/artemis.db')
    curs = conn.cursor()
    return conn, curs


async def load_json(load_file):
    with open('files/{}.json'.format(load_file)) as g:
        data = json.load(g)
    return data


async def dump_json(dump_file, data):
    with open('files/{}.json'.format(dump_file), 'w') as g:
        json.dump(data, g, indent=2)


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
