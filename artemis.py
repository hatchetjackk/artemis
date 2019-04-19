#! /usr/bin/python3
import json
import logging
import os
import random
from datetime import datetime

import discord
from discord.ext import commands
from discord.ext.commands import CommandNotFound

import cogs.utilities as utilities

logging.basicConfig(filename='files/artemis.log', format='%(asctime)s %(message)s', level=logging.INFO)
logging.info('Starting')
artemis_version = '0.9.0'


# noinspection PyUnusedLocal
async def prefix(bot, message):
    conn, c = await utilities.load_db()
    c.execute("SELECT prefix FROM guilds WHERE gid = (:gid)", {'gid': message.guild.id})
    bot_prefix = c.fetchone()[0]
    return bot_prefix
client = commands.Bot(command_prefix=prefix, case_insensitive=True)
client.remove_command('help')


@client.event
async def on_ready():
    print('---------------------------------------')
    print(f'{"Logged in as":<15} {client.user.name}{artemis_version}')
    print(f'{"Client":<15} {client.user.id}')
    print(f'{"Discordpy ver.":<15} {discord.__version__}')
    print('---------------------------------------')
    print(f'[{datetime.now()}] Artemis is online.')
    await utilities.build_db_tables()


@client.event
async def on_resumed():
    print(f'[{datetime.now()}] Artemis is back online.')


# noinspection PyShadowingNames
@client.event
async def on_command_error(ctx, error):
    if isinstance(error, CommandNotFound):
        conn, c = await utilities.load_db()
        c.execute("SELECT response FROM bot_responses WHERE message_type = 'error_response'")
        error_response = [value[0] for value in c.fetchall()]
        await utilities.single_embed(
            color=utilities.color_alert,
            title=random.choice(error_response),
            channel=ctx
        )


if __name__ == '__main__':
    ignore = ['database', '__init__', '__pycache__', 'utilities', 'events']
    cogs = [f.replace('.py', '') for f in os.listdir('cogs/') if f.replace('.py', '') not in ignore]
    for cog in cogs:
        try:
            print('Loading ' + cog)
            client.load_extension('cogs.' + cog)
        except discord.ClientException as e:
            print(e)
            pass
        except AttributeError as e:
            print('attribute error', cog, e)
            pass
        except Exception as e:
            print('exception:', cog, e)
            raise
            pass
    with open('files/credentials.json', 'r') as f:
        credentials = json.load(f)
    client.run(credentials['token'])
