#! python3
import os
import discord
import json
import datetime
import sqlite3
import logging
from discord.ext import commands


logging.basicConfig(filename='files/artemis.log', format='%(asctime)s %(message)s', level=logging.INFO)
logging.info('Starting')


# noinspection PyUnusedLocal
async def prefix(bot, message):
    conn, c = await load_db()
    c.execute("SELECT prefix FROM guilds WHERE id = (?)", (message.guild.id,))
    bot_prefix = c.fetchone()[0]
    return bot_prefix

client = commands.Bot(command_prefix=prefix)
client.remove_command('help')


@client.event
async def on_ready():
    now = datetime.datetime.now()
    print("{0:<15} {1}".format("Logged in as", client.user.name))
    print("{0:<15} {1}".format("Client", client.user.id))
    print('{0:<15} {1}'.format('Discord.py', discord.__version__))
    print("---------------------------------------")
    print("[{0}] Artemis is online.".format(now))


@client.event
async def on_resumed():
    now = datetime.datetime.now()
    message = '[{0}] Artemis is back online.'.format(now)
    print(message)


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

if __name__ == '__main__':
    for extension in [f.replace('.py', '') for f in os.listdir('cogs/') if f != '__init__.py' and f != '__pycache__']:
        try:
            client.load_extension('cogs.' + extension)
        except Exception as error:
            print('{0} cannot be loaded [{1}]'.format(extension, error))
    with open('files/credentials.json', 'r') as f:
        credentials = json.load(f)
    client.run(credentials['token'])
