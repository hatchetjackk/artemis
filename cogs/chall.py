import json
import requests
import asyncio
import sqlite3
from datetime import datetime
from artemis import load_db
from collections import OrderedDict, defaultdict
from discord import Embed, Color, utils
from discord.ext import commands

with open('files/credentials.json') as f:
    challonge_data = json.load(f)
username = challonge_data['challonge']['username']
api = challonge_data['challonge']['API']
thumb = challonge_data['challonge']['thumb']


class Chall(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.color_alert = Color.orange()
        self.color_info = Color.dark_blue()
        self.color_help = Color.dark_green()

    @commands.group(aliases=['chall', 'challonge'])
    async def tourney(self, ctx):
        if ctx.invoked_subcommand is None:
            pass

    @tourney.group()
    async def help(self, ctx):
        embed = await self.msg(
            color=self.color_help,
            title='Challonge Help',
            thumb_url=self.client.user.avatar_url,
            msg='`chall index` View all tournaments\n'
                '`chall show [id]` Show details about a tournament\n'
                '`chall join [id] [username]` Join a tournament'
        )
        await ctx.send(embed=embed)

    @tourney.group()
    async def index(self, ctx):
        try:
            r = requests.get('https://{0}:{1}@api.challonge.com/v1/tournaments.json?subdomain=lm'.format(username, api))
            tournaments = json.loads(r.content)
            embed_messages = {}
            for tournament in tournaments:
                name = tournament['tournament']['name'].upper()
                state = tournament['tournament']['state']
                style = tournament['tournament']['tournament_type']
                sign_up = tournament['tournament']['sign_up_url']
                if sign_up is None:
                    sign_up = 'No sign up page'
                game = tournament['tournament']['game_name']
                if game is None:
                    game = 'No Game Selected'
                num_participants = tournament['tournament']['participants_count']
                tourney_id = tournament['tournament']['id']
                args = (sign_up, style.title(), num_participants, tourney_id)
                embed_messages[tourney_id] = {
                    'name': '{0} - {1} ({2})'.format(name, game, state),
                    'value': '{}\n{}\nPlayers: {}\nid: *{}*'.format(*args)
                }

            embed = await self.multi_msg(
                color=self.color_info,
                title='Challonge Tournaments',
                thumb_url=thumb,
                messages=embed_messages
            )
            await ctx.send(embed=embed)
        except Exception as e:
            print('An error occurred when retrieving tournament data: {}'.format(e))

    @tourney.group()
    async def show(self, ctx, tourney_id):
        try:
            # get the challonge api
            r = requests.get('https://{}:{}@api.challonge.com/v1/tournaments/'
                             '{}.json?subdomain=lm&include_participants=1'.format(username, api, tourney_id))

            # parse api data into meaningful variables
            tournament = json.loads(r.content)
            name = tournament['tournament']['name'].upper()
            state = tournament['tournament']['state']
            style = tournament['tournament']['tournament_type'].title()
            sign_up = tournament['tournament']['sign_up_url']
            date_object = tournament['tournament']['start_at']
            tourney_id = tournament['tournament']['id']
            date, time = date_object.split('T')
            if sign_up is None:
                sign_up = 'No sign up page'
            game = tournament['tournament']['game_name']
            if game is None:
                game = 'No Game Selected'

            # parse players into a meaningful dictionary
            seeded_players = {}
            final_standings = defaultdict(list)
            for player in tournament['tournament']['participants']:
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
            embed_messages = {
                'default_values': {
                    'name': 'Status: {0}\nScheduled for {1}'.format(state, date),
                    'value': '{0}\n{1}\nTourney ID: *{2}*'.format(sign_up, style, tourney_id)
                }
            }

            # generate message based on state
            if len(seeded_players) > 0 and state != 'complete':
                embed_messages[tourney_id] = {
                    'name': 'Players (by seed)',
                    'value': '\n'.join('{0}: {1}'.format(seed, player) for seed, player in sorted_seed.items())
                }
            else:
                standings = ['{}: {}'.format(place, ', '.join(player)) for place, player in sorted_standings.items()]
                embed_messages[tourney_id] = {
                    'name': 'Final Results',
                    'value': '\n'.join(standings)
                }
            embed = await self.multi_msg(
                color=self.color_info,
                title='{0} - {1}'.format(name, game),
                thumb_url=thumb,
                messages=embed_messages
            )
            await ctx.send(embed=embed)
        except Exception as e:
            print('An error occurred when showing challonge tourney {}: {}'.format(tourney_id, e))

    @tourney.group()
    async def join(self, ctx, tourney_id, challonge_name):
        try:
            url = 'https://{}:{}@api.challonge.com/v1/tournaments/{}/participants.json' \
                  '?subdomain=lm&participant[challonge_username]={}'.format(username, api, tourney_id, challonge_name)
            r = requests.post(url)
            participant = json.loads(r.content)

            r = requests.get(
                'https://{}:{}@api.challonge.com/v1/tournaments/'
                '{}.json?subdomain=lm&include_participants=1'.format(username, api, tourney_id))
            tournament = json.loads(r.content)
            name = tournament['tournament']['name']
            state = tournament['tournament']['state']
            style = tournament['tournament']['tournament_type']
            sign_up = tournament['tournament']['sign_up_url']
            if sign_up is None:
                sign_up = 'No sign up page'
            participants = tournament['tournament']['participants_count']
            game = tournament['tournament']['game_name']
            if game is None:
                game = 'No Game Selected'

            for key, value in participant.items():
                player = value['challonge_username']
                embed = Embed(title='{} joined {}'.format(player, name.title()), color=Color.blue())
                args = (sign_up, style.title(), participants, tourney_id)
                fmt = '{}\n{}\nPlayers: {}\nid: *{}*'.format(*args)
                embed.add_field(name='{} - {} {}'.format(name.title(), game, '({})'.format(state)),
                                inline=False,
                                value=fmt)
                embed.set_thumbnail(url='https://s3.amazonaws.com/challonge_app/organizations/images/000/094/501/'
                                        'xlarge/redacted.png?1549047416')
                await ctx.send(embed=embed)
        except Exception as e:
            print(e)

    async def check_challonge(self):
        await self.client.wait_until_ready()
        while not self.client.is_closed():
            await self.check_for_new_events()
            await self.check_for_removed_events()
            await self.check_for_new_participants()
            await self.check_tournament_countdown()
            await asyncio.sleep(60)

    async def get_challonge_channels(self):
        challonge_channels = []
        for guild in self.client.guilds:
            challonge_channel = utils.get(guild.channels, name='challonge_notifications')
            if challonge_channel is not None:
                challonge_channels.append(challonge_channel)
        return challonge_channels

    async def check_for_new_participants(self):
        try:
            conn, c = await load_db()
            c.execute("SELECT * FROM tournament_members")
            tournament_members = c.fetchall()
            c.execute("SELECT * FROM tournament_list")
            tournament_list = c.fetchall()
            for tournament in tournament_list:
                tourney_id, name, one_week_notify, one_day_notify = tournament
                url = 'https://{}:{}@api.challonge.com/v1/tournaments/{}/participants.json'
                r = requests.get(url.format(username, api, tourney_id))
                participants = json.loads(r.content)
                for participant in participants:
                    for k, v in participant.items():
                        members = [member for tournament_id, member
                                   in tournament_members
                                   if tournament_id == int(tourney_id)]
                        if v['id'] not in members:
                            user = v['challonge_username']
                            if user is None:
                                user = v['name']
                            with conn:
                                c.execute("INSERT INTO tournament_members VALUES (:id, :member_id)",
                                          {'id': tourney_id, 'member_id': v['id']})
                            embed = Embed(color=Color.blue())
                            embed.add_field(name=name.upper(),
                                            value='"{}" has signed up!'.format(user))
                            embed.set_thumbnail(url='https://s3.amazonaws.com/challonge_app/organizations/images/'
                                                    '000/094/501/xlarge/redacted.png?1549047416')
                            challonge_channels = await self.get_challonge_channels()
                            for challonge_channel in challonge_channels:
                                await challonge_channel.send(embed=embed)
        except sqlite3.Error as e:
            print('Check for new participants', e)
            pass

    async def check_for_removed_events(self):
        try:
            conn, c = await load_db()
            c.execute("SELECT * FROM tournament_list")
            tournament_database = c.fetchall()
            r = requests.get('https://{}:{}@api.challonge.com/v1/tournaments.json?subdomain=lm'.format(username, api))
            challonge_tournaments = [str(tournament['tournament']['id']) for tournament in json.loads(r.content)]
            for row in tournament_database:
                db_id, name, one_week_notify, one_day_notify = row
                if db_id not in challonge_tournaments:
                    with conn:
                        c.execute("DELETE FROM tournament_list WHERE id = (:id)", {'id': db_id})

                    embed = Embed(color=Color.red())
                    embed.add_field(name='A Challonge Event has been removed',
                                    value=name.title())
                    embed.set_thumbnail(url='https://s3.amazonaws.com/challonge_app/organizations/images/'
                                            '000/094/501/xlarge/redacted.png?1549047416')
                    challonge_channels = await self.get_challonge_channels()
                    for challonge_channel in challonge_channels:
                        await challonge_channel.send(embed=embed)
                    print('A Challonge Event has been removed: {}'.format(name.upper()))
        except sqlite3.Error as e:
            print('Check for removed events', e)
            pass

    async def check_for_new_events(self):
        try:
            conn, c = await load_db()
            c.execute("SELECT * FROM tournament_list")
            tournament_database = c.fetchall()
            r = requests.get('https://{}:{}@api.challonge.com/v1/tournaments.json?subdomain=lm'.format(username, api))
            challonge_tournaments = json.loads(r.content)
            for tournament in challonge_tournaments:
                name = tournament['tournament']['name']
                tournament_id = tournament['tournament']['id']
                date_object = tournament['tournament']['start_at']
                if date_object is not None:
                    date, time = date_object.split('T')
                else:
                    date = 'No date currently selected'
                sign_up = tournament['tournament']['sign_up_url']
                if sign_up is None:
                    sign_up = 'No Sign Up Page yet'
                if tournament_id not in tournament_database:
                    with conn:
                        c.execute("INSERT INTO tournament_list VALUES (:id, :name, :one_week_notify, :one_day_notify)",
                                  {'id': tournament_id, 'name': name, 'one_week_notify': None, 'one_day_notify': None})
                    embed = Embed(color=Color.blue())
                    embed.set_thumbnail(url='https://s3.amazonaws.com/challonge_app/organizations/images/'
                                            '000/094/501/xlarge/redacted.png?1549047416')
                    embed.add_field(name='A new Challonge event has been created!',
                                    value='Event Name: {}\n'
                                          'Date: {}\n'
                                          'Sign Up Here: {}'.format(name.upper(), date, sign_up),
                                    inline=False)
                    embed.set_thumbnail(url='https://s3.amazonaws.com/challonge_app/organizations/images/'
                                            '000/094/501/xlarge/redacted.png?1549047416')
                    challonge_channels = await self.get_challonge_channels()
                    for challonge_channel in challonge_channels:
                        await challonge_channel.send(embed=embed)
                    print('A new Challonge Event has been created: {}'.format(name.title()))
        except sqlite3.Error:
            pass

    async def check_tournament_countdown(self):
        try:
            conn, c = await load_db()
            r = requests.get('https://{}:{}@api.challonge.com/v1/tournaments.json?subdomain=lm'.format(username, api))
            challonge_tournaments = json.loads(r.content)
            for tournament in challonge_tournaments:
                start_at = tournament['tournament']['start_at'].split('.')[0]
                tourney_id = tournament['tournament']['id']
                name = tournament['tournament']['name']
                if start_at is not None:
                    start_at = datetime.strptime(start_at, '%Y-%m-%dT%H:%M:%S')
                    time_until_start = start_at - datetime.now()
                    days_full, time = time_until_start.__str__().split(',')
                    days = days_full.split()[0]
                    embed = Embed(title='{} is {} away!'.format(name, days_full), color=Color.blue())
                    embed.add_field(name='Remember to sign up!', value=tournament['tournament']['sign_up_url'])
                    challonge_channels = await self.get_challonge_channels()
                    if int(days) == 7:
                        c.execute("SELECT one_week_notify FROM tournament_list WHERE id = (:id)", {'id': tourney_id})
                        if c.fetchone()[0] != 1:
                            with conn:
                                c.execute("UPDATE tournament_list SET one_week_notify=1 WHERE id = (:id)",
                                          {'id': tourney_id})
                            for challonge_channel in challonge_channels:
                                await challonge_channel.send(embed=embed)
                    elif int(days) == 1:
                        c.execute("SELECT one_day_notify FROM tournament_list WHERE id = (:id)", {'id': tourney_id})
                        if c.fetchone()[0] != 1:
                            with conn:
                                c.execute("UPDATE tournament_list SET one_day_notify=1 WHERE id = (:id)",
                                          {'id': tourney_id})
                            for challonge_channel in challonge_channels:
                                await challonge_channel.send(embed=embed)
        except sqlite3.Error as e:
            print('Check tournament countdown', e)
            pass

    @staticmethod
    async def msg(color=Color.dark_grey(), title='Alert', thumb_url=None, msg=None):
        embed = Embed(color=color)
        if thumb_url is not None:
            embed.set_thumbnail(url=thumb_url)
        embed.add_field(name=title, value=msg, inline=False)
        return embed

    @staticmethod
    async def multi_msg(color=Color.dark_grey(), title='Alert', thumb_url=None, messages=None):
        embed = Embed(color=color, title=title)
        if thumb_url is not None:
            embed.set_thumbnail(url=thumb_url)
        for key, value in messages.items():
            embed.add_field(name=value['name'], value=value['value'], inline=False)
        return embed

    @staticmethod
    async def format_time(datetime_string):
        datetime_object = datetime.strptime(datetime_string, '%Y-%m-%d %H:%M:%S')
        dt_full = datetime_object.strftime("%Y-%m-%d %H:%M:%S")
        return dt_full


def setup(client):
    chall = Chall(client)
    client.add_cog(chall)
    client.loop.create_task(chall.check_challonge())
