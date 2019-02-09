#! python3.6
import os
import random
import discord
import json
import sqlite3
import logging
from datetime import datetime
from discord.ext import commands
from discord.ext.commands import CommandNotFound

logging.basicConfig(filename='files/artemis.log', format='%(asctime)s %(message)s', level=logging.INFO)
logging.info('Starting')


# noinspection PyUnusedLocal
async def prefix(bot, message):
    conn, c = await load_db()
    c.execute("SELECT prefix FROM guilds WHERE id = (:id)", {'id': message.guild.id})
    bot_prefix = c.fetchone()[0]
    return bot_prefix
client = commands.Bot(command_prefix=prefix)
client.remove_command('help')


@client.event
async def on_ready():
    print("{0:<15} {1}".format("Logged in as", client.user.name))
    print("{0:<15} {1}".format("Client", client.user.id))
    print('{0:<15} {1}'.format('Discord.py', discord.__version__))
    print("---------------------------------------")
    print("[{}] Artemis is online.".format(datetime.now()))
    await build_db_tables()


@client.event
async def on_resumed():
    now = datetime.now()
    message = '[{0}] Artemis is back online.'.format(now)
    print(message)


# noinspection PyShadowingNames
@client.event
async def on_command_error(ctx, error):
    if isinstance(error, CommandNotFound):
        conn, c = await load_db()
        c.execute("SELECT response FROM bot_responses WHERE message_type = 'error_response'")
        error_response = [value[0] for value in c.fetchall()]
        await ctx.send(random.choice(error_response))


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


if __name__ == '__main__':
    for extension in [f.replace('.py', '') for f in os.listdir('cogs/') if not f.startswith('_')]:
        try:
            client.load_extension('cogs.' + extension)
        except Exception as e:
            print('[{}] {} cannot be loaded: {}'.format(datetime.now(), extension, e))
    with open('files/credentials.json', 'r') as f:
        credentials = json.load(f)
    client.run(credentials['token'])

