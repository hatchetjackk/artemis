import json
import requests
import asyncio
import sqlite3
from datetime import datetime
from artemis import load_db
from collections import OrderedDict
from discord import Embed, Color, utils
from discord.ext import commands

with open('files/credentials.json') as f:
    challonge_data = json.load(f)
username = challonge_data['challonge']['username']
api = challonge_data['challonge']['API']


class Chall:
    def __init__(self, client):
        self.client = client

    @commands.group(aliases=['chall'])
    async def tourney(self, ctx):
        if ctx.invoked_subcommand is None:
            pass

    @tourney.group()
    async def help(self, ctx):
        embed = Embed(color=Color.blue())
        embed.add_field(name='Challonge Help',
                        value='`chall index` View all tournaments\n'
                              '`chall show [id]` Show details about a tournament\n'
                              '`chall join [id] [username]` Join a tournament')
        await ctx.send(embed=embed)

    @tourney.group()
    async def index(self, ctx):
        try:
            embed = Embed(title='Tournaments', color=Color.blue())
            r = requests.get('https://{}:{}@api.challonge.com/v1/tournaments.json?subdomain=lm'.format(username, api))
            tournaments = json.loads(r.content)
            for tournament in tournaments:
                name = tournament['tournament']['name']
                state = tournament['tournament']['state']
                style = tournament['tournament']['tournament_type']
                sign_up = tournament['tournament']['sign_up_url']
                if sign_up is None:
                    sign_up = 'No sign up page'
                game = tournament['tournament']['game_name']
                if game is None:
                    game = 'No Game Selected'
                participants = tournament['tournament']['participants_count']
                tourney_id = tournament['tournament']['id']
                args = (sign_up, style.title(), participants, tourney_id)
                fmt = '{}\n{}\nPlayers: {}\nid: *{}*'.format(*args)
                embed.add_field(name='{} - {} {}'.format(name.title(), game, '({})'.format(state)),
                                inline=False,
                                value=fmt)
            await ctx.send(embed=embed)
        except Exception as e:
            print('An error occurred when retrieving tournament data: {}'.format(e))

    @tourney.group()
    async def show(self, ctx, tourney_id):
        try:
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
            game = tournament['tournament']['game_name']
            if game is None:
                game = 'No Game Selected'
            participants_dict = {}
            for player in tournament['tournament']['participants']:
                if player['participant']['name'] != '' and player['participant']['name'] is not None:
                    participants_dict[player['participant']['seed']] = player['participant']['name']
                else:
                    participants_dict[player['participant']['seed']] = player['participant']['challonge_username']
            sorted_participants = OrderedDict(sorted(participants_dict.items(), key=lambda x: x[0]))
            tourney_id = tournament['tournament']['id']
            args = (sign_up, style.title(), tourney_id)
            fmt = '{}\n{}\nid: *{}*'.format(*args)
            embed = Embed(title='{} - {}'.format(name.title(), game), color=Color.blue())
            embed.add_field(name='Status: {}'.format(state.title()), value=fmt, inline=False)
            if len(participants_dict) > 0:
                embed.add_field(name='Players (by seed)',
                                value='\n'.join('{}: {}'.format(seed, player) for seed, player in sorted_participants.items()),
                                inline=False)
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
                await ctx.send(embed=embed)
        except Exception as e:
            print(e)

    async def check_challonge(self):
        await self.client.wait_until_ready()
        while not self.client.is_closed():
            await asyncio.sleep(60)
            await self.check_for_new_events()
            await self.check_for_removed_events()
            await self.check_for_new_participants()

    async def check_for_new_participants(self):
        challonge_channel = utils.get(self.client.get_all_channels(), name='challonge_notifications')
        try:
            conn, c = await load_db()
            c.execute("SELECT * FROM tournament_members")
            tournament_members = c.fetchall()
            c.execute("SELECT * FROM tournament_list")
            tournament_list = c.fetchall()
            for tournament in tournament_list:
                tourney_id, name = tournament
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
                            embed.add_field(name=name.title(),
                                            value='"{}" has signed up!'.format(user))
                            await challonge_channel.send(embed=embed)
        except sqlite3.Error as e:
            print(e)

    async def check_for_removed_events(self):
        challonge_channel = utils.get(self.client.get_all_channels(), name='challonge_notifications')
        try:
            conn, c = await load_db()
            c.execute("SELECT * FROM tournament_list")
            tournament_database = c.fetchall()
            r = requests.get('https://{}:{}@api.challonge.com/v1/tournaments.json?subdomain=lm'.format(username, api))
            challonge_tournaments = [str(tournament['tournament']['id']) for tournament in json.loads(r.content)]
            for row in tournament_database:
                db_id, name = row
                if db_id not in challonge_tournaments:
                    with conn:
                        c.execute("DELETE FROM tournament_list WHERE id = (:id)", {'id': db_id})
                    embed = Embed(color=Color.red())
                    embed.add_field(name='A Challonge Event has been removed',
                                    value=name.title())
                    await challonge_channel.send(embed=embed)
                    print('A Challonge Event has been removed: {}'.format(name.title()))
        except sqlite3.Error as e:
            print(e)

    async def check_for_new_events(self):
        challonge_channel = utils.get(self.client.get_all_channels(), name='challonge_notifications')
        try:
            conn, c = await load_db()
            c.execute("SELECT * FROM tournament_list")
            tournament_database = c.fetchall()
            r = requests.get('https://{}:{}@api.challonge.com/v1/tournaments.json?subdomain=lm'.format(username, api))
            challonge_tournaments = json.loads(r.content)
            for tournament in challonge_tournaments:
                name = tournament['tournament']['name']
                tournament_id = tournament['tournament']['id']
                sign_up = tournament['tournament']['sign_up_url']
                if sign_up is None:
                    sign_up = 'No Sign Up Page yet'
                if tournament_id not in tournament_database:
                    with conn:
                        c.execute("INSERT INTO tournament_list VALUES (:id, :name)",
                                  {'id': tournament_id, 'name': name})
                    embed = Embed(color=Color.blue())
                    embed.add_field(name='A new Challonge event has been created!',
                                    value='{}\nSign Up Here: {}'.format(name.title(), sign_up),
                                    inline=False)
                    await challonge_channel.send(embed=embed)
                    print('A new Challonge Event has been created: {}'.format(name.title()))
        except sqlite3.Error:
            pass

    @staticmethod
    async def format_time(datetime_string):
        datetime_object = datetime.strptime(datetime_string, '%Y-%m-%d %H:%M:%S')
        dt_full = datetime_object.strftime("%Y-%m-%d %H:%M:%S")
        return dt_full


def setup(client):
    client.add_cog(Chall(client))
    client.loop.create_task(Chall(client).check_challonge())
