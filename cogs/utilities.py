import sqlite3
import json
import discord


color_alert = discord.Color.orange()
color_info = discord.Color.blue()
color_help = discord.Color.green()
color_empty = discord.Color.dark_grey()


async def multi_embed(color=color_empty, url=None, title='Alert', thumb_url=None, messages=None):
    try:
        embed = discord.Embed(color=color, title=title, url=url)
        if thumb_url is not None:
            embed.set_thumbnail(url=thumb_url)
        for msg in messages:
            name, value = msg
            embed.add_field(name=name, value=value, inline=False)
        return embed
    except Exception as e:
        print(f'An unexpected error occurred when processing a multi-message embed: {e}')


async def embed_msg(color=discord.Color.dark_grey(), title='Alert', thumb_url=None, name='\u200b', msg=None):
    embed = discord.Embed(color=color, title=title)
    if thumb_url is not None:
        embed.set_thumbnail(url=thumb_url)
    embed.add_field(name=name, value=msg, inline=False)
    return embed


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
                """CREATE TABLE IF NOT EXISTS members (
                    id INTEGER,
                    member_name TEXT,
                    karma INTEGER,
                    last_karma_given INTEGER,
                    UNIQUE(id, member_name)
                    )"""
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
