import json
import requests
import asyncio
import sqlite3
import discord
import cogs.utilities as utilities
from datetime import datetime
from collections import OrderedDict, defaultdict
from discord.ext import commands

with open('files/credentials.json') as f:
    challonge_data = json.load(f)
username = challonge_data['challonge']['username']
api = challonge_data['challonge']['API']
thumb = challonge_data['challonge']['thumb']


class Chall(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.group(aliases=['chall', 'challonge'])
    async def tourney(self, ctx):
        if ctx.invoked_subcommand is None:
            pass

    @tourney.group()
    async def help(self, ctx):
        embed = await utilities.embed_msg(
            color=utilities.color_help,
            thumb_url=self.client.user.avatar_url,
            msg=['Challonge Help',
                 '`chall index` View all tournaments\n'
                 '`chall show [id]` Show details about a tournament']
        )
        await ctx.send(embed=embed)

    @tourney.group()
    async def index(self, ctx):
        try:
            r = requests.get(f'https://{username}:{api}@api.challonge.com/v1/tournaments.json?subdomain=lm')
            tournaments = [value['tournament'] for value in json.loads(r.content)]
            embed_messages = []
            for tournament in tournaments:
                tourney_name = tournament['name'].upper()
                state = tournament['state']
                style = tournament['tournament_type']
                sign_up = tournament['sign_up_url']
                url = tournament['full_challonge_url']
                if sign_up is None:
                    sign_up = 'No sign up page'
                game = tournament['game_name']
                if game is None:
                    game = 'No Game Selected'
                num_participants = tournament['participants_count']
                tourney_id = tournament['id']
                args = (sign_up, url, style.title(), num_participants, tourney_id)
                name = f'{tourney_name} - {game} ({state})'
                if state != 'complete':
                    value = '[Sign Up]({0}) / [View]({1})\n{2}\nPlayers: {3}\nid: *{4}*'.format(*args)
                else:
                    value = '[View]({1})\n{2}\nPlayers: {3}\nid: *{4}*'.format(*args)
                embed_messages.append([name, value])

            embed = await utilities.multi_embed(
                color=utilities.color_info,
                title='Challonge Tournaments',
                thumb_url=thumb,
                messages=embed_messages
            )
            await ctx.send(embed=embed)
        except Exception as e:
            print(f'An error occurred when retrieving tournament data: {e}')
            raise

    @tourney.group()
    async def show(self, ctx, tourney_id):
        try:
            # get the challonge api
            r = requests.get(f'https://{username}:{api}@api.challonge.com/v1/'
                             f'tournaments/{tourney_id}.json?subdomain=lm&include_participants=1')

            # parse api data into meaningful variables
            tournament = json.loads(r.content).get('tournament')
            tourney_name = tournament.get('name').upper()
            state = tournament.get('state')
            style = tournament.get('tournament_type').title()
            sign_up = tournament.get('sign_up_url')
            url = tournament.get('full_challonge_url')
            date_object = tournament.get('start_at')
            tourney_id = tournament.get('id')
            date, time = date_object.split('T')
            if sign_up is None:
                sign_up = 'No sign up page'
            game = tournament.get('game_name')
            if game is None:
                game = 'No Game Selected'

            # parse players into a meaningful dictionary
            seeded_players = {}
            final_standings = defaultdict(list)
            for player in tournament.get('participants'):
                player = player['participant']
                if state == 'complete':
                    if player['name'] != '' and player['name'] is not None:
                        final_standings[player['final_rank']].append(player['name'])
                    else:
                        final_standings[player['final_rank']].append(player['challonge_username'])
                else:
                    if player['name'] != '' and player['name'] is not None:
                        seeded_players[player['seed']] = player['name']
                    else:
                        seeded_players[player['seed']] = player['challonge_username']

            # sort participants by standings or seed
            sorted_standings = OrderedDict(sorted(final_standings.items(), key=lambda x: x[0]))
            sorted_seed = OrderedDict(sorted(seeded_players.items(), key=lambda x: x[0]))

            name = f'Status: {state}\nScheduled for {date}'
            value = f'{style}\nTourney ID: *{id}*'
            if state != 'complete':
                value = f'[Sign Up]({sign_up}) / [View]({url})\n{style}\nTourney ID: *{tourney_id}*'
            embed_messages = [[name, value]]

            # generate message based on tourney state
            if len(seeded_players) > 0 and state != 'complete':
                name = 'Players (by seed)'
                value = '\n'.join('{0}: {1}'.format(seed, player) for seed, player in sorted_seed.items())
                embed_messages.append([name, value])
            else:
                standings = ['{0}: {1}'.format(place, ', '.join(player)) for place, player in sorted_standings.items()]
                name = 'Final Results'
                value = '\n'.join(standings)
                embed_messages.append([name, value])
            embed = await utilities.multi_embed(
                color=utilities.color_info,
                title=f'{tourney_name} - {game}',
                thumb_url=thumb,
                url=url,
                messages=embed_messages
            )
            await ctx.send(embed=embed)
        except Exception as e:
            print(f'An error occurred when showing challonge tourney {tourney_id}: {e}')

    async def check_for_challonge_changes(self):
        await self.client.wait_until_ready()
        while not self.client.is_closed():
            await self.check_for_new_events()
            await self.check_for_removed_events()
            await self.check_for_new_participants()
            await self.check_tournament_countdown()
            await asyncio.sleep(60)

    async def get_challonge_notification_channels(self):
        challonge_notification_channels = []
        for guild in self.client.guilds:
            channel = discord.utils.get(guild.channels, name='challonge_notifications')
            if channel is not None:
                challonge_notification_channels.append(channel)
        return challonge_notification_channels

    async def check_for_new_participants(self):
        try:
            conn, c = await utilities.load_db()
            c.execute("SELECT * FROM tournament_members")
            member_database = c.fetchall()

            c.execute("SELECT * FROM tournament_list")
            tournament_database = c.fetchall()

            messages = []
            for tournament in tournament_database:
                tournament_id, tournament_name, one_week_notify, one_day_notify = tournament
                tournament_members = [member_id for tid, member_id in member_database if tid == int(tournament_id)]

                chall_api = 'https://{}:{}@api.challonge.com/v1/tournaments/{}/participants.json'
                r = requests.get(chall_api.format(username, api, tournament_id))

                tournament_participants = [value['participant'] for value in json.loads(r.content)]
                for participant in tournament_participants:
                    if participant.get('id') not in tournament_members:
                        user = participant.get('challonge_username')
                        if user is None:
                            user = participant.get('name')
                        messages.append([tournament_name.upper(), f'"{user}" has signed up!'])
                        with conn:
                            c.execute("INSERT INTO tournament_members VALUES (:id, :member_id)",
                                      {'id': tournament_id, 'member_id': participant.get('id')})
            if len(messages) > 0:
                embed = await utilities.multi_embed(
                    color=self.color_info,
                    title='A New Challenger Approaches!',
                    thumb_url=thumb,
                    messages=messages
                )
                challonge_notification_channels = await self.get_challonge_notification_channels()
                for challonge_channel in challonge_notification_channels:
                    await challonge_channel.send(embed=embed)
        except sqlite3.Error as e:
            print(f'An sql error occurred when checking for new participants: {e}')
        except NameError as e:
            print(f'A NameError occurred when checking for new participants: {e}')
        except Exception as e:
            print(f'An unknown error occurred when checking for new participants: {e}')

    async def check_for_removed_events(self):
        try:
            conn, c = await utilities.load_db()
            c.execute("SELECT * FROM tournament_list")
            tournament_database = c.fetchall()
            r = requests.get('https://{}:{}@api.challonge.com/v1/tournaments.json?subdomain=lm'.format(username, api))
            challonge_tournaments = [str(tournament['tournament']['id']) for tournament in json.loads(r.content)]
            messages = []
            for tournament in tournament_database:
                tournament_id, tournament_name, one_week_notify, one_day_notify = tournament
                if tournament_id not in challonge_tournaments:
                    with conn:
                        c.execute("DELETE FROM tournament_list WHERE id = (:id)", {'id': tournament_id})
                    messages.append(['A Challonge Event Has Been Removed', tournament_name.title()])
            if len(messages) > 0:
                embed = await utilities.multi_embed(
                    color=self.color_info,
                    thumb_url=thumb,
                    messages=messages
                )
                challonge_notification_channels = await self.get_challonge_notification_channels()
                for challonge_channel in challonge_notification_channels:
                    await challonge_channel.send(embed=embed)
        except sqlite3.Error as e:
            print('An sql error occurred when checking for removed events: {}'.format(e))
        except Exception as e:
            print('An unknown error occurred when checking for removed events: {}'.format(e))

    async def check_for_new_events(self):
        try:
            conn, c = await utilities.load_db()
            c.execute("SELECT * FROM tournament_list")
            tournament_database = c.fetchall()
            r = requests.get(f'https://{username}:{api}@api.challonge.com/v1/tournaments.json?subdomain=lm')
            challonge_tournaments = [value['tournament'] for value in json.loads(r.content)]
            messages = []
            for tournament in challonge_tournaments:
                name = tournament.get('name')
                tournament_id = tournament.get('id')
                start_at = tournament.get('start_at')
                url = tournament.get('full_challonge_url')
                if start_at is not None:
                    date, time = start_at.split('T')
                else:
                    date = 'No date currently selected'
                sign_up_url = tournament.get('sign_up_url')
                if sign_up_url is None:
                    sign_up_url = 'No Sign Up Page yet'
                if tournament_id not in tournament_database:
                    with conn:
                        c.execute("INSERT INTO tournament_list VALUES (:id, :name, :one_week_notify, :one_day_notify)",
                                  {'id': tournament_id, 'name': name, 'one_week_notify': None, 'one_day_notify': None})
                    msg_name = 'A new Challonge event has been created!'
                    value = f'[{name.upper()}]({url})\nDate: {date}\n[Sign Up]({sign_up_url})'
                    messages.append([msg_name, value])
            if len(messages) > 0:
                embed = await utilities.multi_embed(
                    color=self.color_info,
                    thumb_url=thumb,
                    messages=messages
                )
                challonge_notification_channels = await self.get_challonge_notification_channels()
                for challonge_channel in challonge_notification_channels:
                    await challonge_channel.send(embed=embed)
        except sqlite3.Error:
            # print('An sql error occurred when checking for new events: {}'.format(e))
            pass
        except Exception as e:
            print(f'An unexpected error occurred when checking for new events: {e}')

    async def check_tournament_countdown(self):
        try:
            conn, c = await utilities.load_db()
            r = requests.get(f'https://{username}:{api}@api.challonge.com/v1/tournaments.json?subdomain=lm')
            challonge_tournaments = [value['tournament'] for value in json.loads(r.content)]
            for tournament in challonge_tournaments:
                start_at = tournament.get('start_at').split('.')[0]
                tourney_id = tournament.get('id')
                tournament_name = tournament.get('name')
                sign_up_url = tournament.get('sign_up_url')
                if start_at is not None:
                    start_at = datetime.strptime(start_at, '%Y-%m-%dT%H:%M:%S')
                    time_until_start = start_at - datetime.now()
                    days_full, time = time_until_start.__str__().split(',')
                    days = int(days_full.split()[0])
                    messages = []
                    name = f'{tournament_name} is {days} day away!'
                    if days != 1:
                        name = f'{tournament_name} is {days} days away!'
                    messages.append([name, f'Remember to [sign up]({sign_up_url})!'])
                    embed = await utilities.multi_embed(
                        color=self.color_info,
                        thumb_url=thumb,
                        title='A Tournament is Fast Approaching!',
                        messages=messages
                    )

                    if days == 7:
                        c.execute("SELECT one_week_notify FROM tournament_list WHERE id = (:id)", {'id': tourney_id})
                        if c.fetchone()[0] != 1:
                            with conn:
                                c.execute("UPDATE tournament_list SET one_week_notify=1 WHERE id = (:id)",
                                          {'id': tourney_id})
                            challonge_notification_channels = await self.get_challonge_notification_channels()
                            for challonge_channel in challonge_notification_channels:
                                await challonge_channel.send(embed=embed)

                    elif days == 1:
                        c.execute("SELECT one_day_notify FROM tournament_list WHERE id = (:id)", {'id': tourney_id})
                        if c.fetchone()[0] != 1:
                            with conn:
                                c.execute("UPDATE tournament_list SET one_day_notify=1 WHERE id = (:id)",
                                          {'id': tourney_id})
                            challonge_notification_channels = await self.get_challonge_notification_channels()
                            for challonge_channel in challonge_notification_channels:
                                await challonge_channel.send(embed=embed)
        except sqlite3.Error:
            pass
        except Exception as e:
            print(f'An unexpected error occurred when checking event countdowns: {e}')

    @staticmethod
    async def format_time(datetime_string):
        datetime_object = datetime.strptime(datetime_string, '%Y-%m-%d %H:%M:%S')
        dt_full = datetime_object.strftime("%Y-%m-%d %H:%M:%S")
        return dt_full


def setup(client):
    chall = Chall(client)
    client.add_cog(chall)
    client.loop.create_task(chall.check_for_challonge_changes())
