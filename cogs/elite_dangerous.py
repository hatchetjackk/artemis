import requests
import aiohttp
import json
from bs4 import BeautifulSoup
from artemis import load_db
from discord import Embed, Color
from math import sqrt
from datetime import datetime
from discord.ext import commands


class EliteDangerous:
    def __init__(self, client):
        self.client = client
        self.wanted_blacklist = ['Knights of Karma']

    @staticmethod
    async def fetch(session, url):
        async with session.get(url) as response:
            return await response.text()

    @commands.group()
    async def wanted(self, ctx):
        if ctx.guild.name in self.wanted_blacklist:
            return
        if ctx.invoked_subcommand is None:
            conn, c = await load_db()
            embed = Embed(title='Wanted CMDRs', color=Color.orange())
            c.execute("SELECT * FROM ed_wanted WHERE guild_id = (:guild_id)", {'guild_id': ctx.guild.id})
            wanted_commanders = c.fetchall()
            if len(wanted_commanders) < 1:
                embed.add_field(name='No CMDRs on the WANTED list.',
                                value='Nothing to see here.',
                                inline=False)
            else:
                for cmdr in wanted_commanders:
                    cmdr_name, reason, inara_page, guild_id, member_id = cmdr
                    fmt = (reason, inara_page)
                    embed.add_field(name=cmdr_name.title(),
                                    value='Reason: {}\n{}'.format(*fmt),
                                    inline=False)
            await ctx.send(embed=embed)

    @staticmethod
    async def get_pilot_information(cmdr_name):
        try:
            with open('files/credentials.json') as f:
                data = json.load(f)
            inara_api = data['inara']
            json_data = {
                "header": {
                    "appName": "Artemis_Bot",
                    "appVersion": "0.7",
                    "isDeveloped": True,
                    "APIkey": inara_api,
                    "commanderName": "Hatchet Jackk"
                },
                "events": [
                    {
                        "eventName": "getCommanderProfile",
                        "eventTimestamp": str(datetime.utcnow().isoformat()),
                        "eventData": {
                            "searchName": cmdr_name
                        }
                    }
                ]
            }
            json_string = json.dumps(json_data)
            url = 'https://inara.cz/inapi/v1/'
            r = requests.post(url, json_string)
            pilot_data = list(r.json()['events'])[0]
            pilot_page = pilot_data['eventData']['inaraURL']
            if pilot_page is None:
                return None
            return pilot_page
        except Exception as e:
            print('Get pilot information error', e)
            return None

    @wanted.group()
    async def add(self, ctx, *args):
        if ctx.guild.name == any(self.wanted_blacklist):
            return
        wanted_cmdr, reason = (value.strip() for value in ' '.join(args).split(','))
        inara_page = await self.get_pilot_information(wanted_cmdr)
        conn = await load_db()
        c = conn.cursor()
        with conn:
            c.execute("INSERT INTO ed_wanted VALUES(:cmdr_name, :reason, :inara_page, :guild_id, :member_id)",
                      {'cmdr_name': wanted_cmdr.lower(), 'reason': reason, 'inara_page': inara_page,
                       'guild_id': ctx.guild.id, 'member_id': ctx.author.id})
        embed = Embed(title='{} added to WANTED list'.format(wanted_cmdr.title()),
                      color=Color.red())
        await ctx.send(embed=embed)

    @wanted.group()
    async def remove(self, ctx, *, wanted_cmdr: str):
        if ctx.guild.name == any(self.wanted_blacklist):
            return
        conn = await load_db()
        c = conn.cursor()
        with conn:
            c.execute("DELETE FROM ed_wanted WHERE cmdr_name = (:cmdr_name) AND guild_id = (:guild_id)",
                      {'cmdr_name': wanted_cmdr.lower(), 'guild_id': ctx.guild.id})
        embed = Embed(title='{} removed from WANTED list'.format(wanted_cmdr.title()),
                      color=Color.orange())
        await ctx.send(embed=embed)

    @commands.command()
    async def faction(self, ctx, *, faction: str):
        async with aiohttp.ClientSession() as session:
            url = 'http://elitebgs.kodeblox.com/api/eddb/v3/factions?name={}'.format(faction)
            f = await self.fetch(session, url)
            values = json.loads(f)['docs'][0]
            faction_name = values['name']
            faction_id = values['id']
            government = values['government'].title()
            allegiance = values['allegiance'].title()
            player_faction = values['is_player_faction']
            last_update = values['updated_at']
            home_system_id = values['home_system_id']

            if home_system_id is not None:
                url = 'http://elitebgs.kodeblox.com/api/eddb/v3/systems?eddbid={}'.format(home_system_id)
                f = await self.fetch(session, url)
                values = json.loads(f)['docs'][0]
                home_system_name = values['name']
            else:
                home_system_name = 'None'
            fmt = (government, allegiance, player_faction, home_system_name)

            embed = Embed(title=faction_name,
                          color=Color.orange(),
                          description='Government: {}\n'
                                      'Allegiance: {}\n'
                                      'Player Faction: {}\n'
                                      'Home System: {}'.format(*fmt))

            if faction_id is not None:
                url = 'https://eddb.io/faction/{}'.format(faction_id)
                f = await self.fetch(session, url)
                soup = BeautifulSoup(f, 'lxml')
                faction_system_information = soup.findAll('tr', class_='systemRow')
                for system in faction_system_information:
                    # print(system)
                    # print([value for value in system.findAll('span')])
                    faction_system_name = system.find('a').contents[0]
                    faction_system_state = [value for value in system.findAll('span')[3]]
                    faction_system_pop = [value for value in system.findAll('span')[5]]
                    faction_system_sec = [value for value in system.findAll('span')[1]]
                    faction_system_power = [value for value in system.findAll('span')[7]]
                    faction_system_state = 'State: {}'.format(faction_system_state[0])
                    faction_system_pop = 'Population: {}'.format(faction_system_pop[0])
                    faction_system_sec = 'Security:  {}'.format(faction_system_sec[0])
                    faction_system_power = 'Controlling Power:  {}'.format(faction_system_power[0])
                    fmt = (faction_system_state, faction_system_pop, faction_system_sec, faction_system_power)
                    embed.add_field(name=faction_system_name,
                                    value='\n'.join(fmt),
                                    inline=False)

            thumbs = {'Independent': 'https://i.imgur.com/r4d7tPt.png',
                      'Alliance': 'https://i.imgur.com/OWf0P6u.png',
                      'Empire': 'https://i.imgur.com/KTmp5MF.png',
                      'Federation': 'https://i.imgur.com/3oT7gr0.png',
                      'Pilots Federation': 'https://i.imgur.com/tshl8xE.png',
                      'Guardian': 'https://edassets.org/static/img/power-ethos/Covert.png'}
            embed.set_thumbnail(url=thumbs[allegiance])
            embed.set_footer(text='Last Updated: {}'.format(last_update))
            await ctx.send(embed=embed)

    @commands.command()
    async def system(self, ctx, *args):
        args = ' '.join(args).split(',')
        async with aiohttp.ClientSession() as session:
            if len(args) > 1:
                system, station_name = args[0].strip(), args[1].strip()
                url = 'https://www.edsm.net/api-system-v1/stations?sysname={}'.format(system)
                f = await self.fetch(session, url)
                values = json.loads(f)
                system = values['name']
                for station in values['stations']:
                    if station_name.lower() == station['name'].lower():
                        name = station['name']
                        controlling_faction = station['controllingFaction']['name']
                        allegiance = station['allegiance']
                        government = station['government']
                        economy = station['economy']
                        market = station['haveMarket']
                        shipyard = station['haveShipyard']
                        outfitting = station['haveOutfitting']
                        distance_from_star = round(station['distanceToArrival'])
                        station_type = station['type']
                        thumbs = {'Outpost': 'https://i.imgur.com/BRZu7co.png',
                                  'Orbis Starport': 'https://i.imgur.com/cBTdMoJ.png',
                                  'Coriolis Starport': 'https://i.imgur.com/4PYsZs9.png',
                                  'Planetary Outpost': 'https://i.imgur.com/xTderZC.png',
                                  'Planetary Settlement': 'https://i.imgur.com/xTderZC.png',
                                  'Ocellus Starport': 'https://i.imgur.com/xTderZC.png',
                                  'Mega ship': 'https://i.imgur.com/HZXRqFG.png'}
                        faction_abbr = ''.join([word[0] for word in controlling_faction.split(' ')])
                        fmt = (station_type, controlling_faction, faction_abbr, government,
                               allegiance, economy, market, shipyard, outfitting)
                        embed = Embed(title='{}, {}'.format(name, system),
                                      color=Color.orange(),
                                      description='Station Type: {}\n'
                                                  'Controlling Faction: {} ({})\n'
                                                  'Government: {}\n'
                                                  'Allegiance: {}\n'
                                                  'Economy: {}\n'
                                                  'Market: {}\n'
                                                  'Shipyard: {}\n'
                                                  'Outfitting: {}'.format(*fmt))
                        thumbnail = 'https://edassets.org/static/img/stations/Outpost.png'
                        if station_type in thumbs:
                            thumbnail = thumbs[station_type]
                        embed.set_thumbnail(url=thumbnail)
                        embed.set_footer(text='Distance from arrival star: {} LS'.format(distance_from_star))
                        await ctx.send(embed=embed)
                        return
            else:
                try:
                    system = args[0].strip()
                    url = 'https://www.edsm.net/api-v1/system?sysname={}&coords=1&showInformation=1&showPrimaryStar=1'.format(system)
                    f = await self.fetch(session, url)
                    system_data = json.loads(f)
                    system_name = system_data['name']
                    system_information = ''
                    allegiance = 'Independent'
                    if len(system_data['information']) > 0:
                        allegiance = system_data['information']['allegiance']
                        faction = system_data['information']['faction']
                        government = system_data['information']['government']
                        if 'factionState' not in system_data['information']:
                            faction_state = None
                        else:
                            faction_state = system_data['information']['factionState']
                        faction_abbr = ''.join([word[0] for word in faction.split(' ')])
                        primary_start_scoopable = system_data['primaryStar']['isScoopable']
                        fmt = (faction, faction_abbr, government, faction_state, allegiance, primary_start_scoopable)
                        system_information = '**Faction**: {} ({})\n' \
                                             '**Government**: {}\n' \
                                             '**State**: {}\n' \
                                             '**Allegiance**: {}\n' \
                                             '**Primary Star Scoopable**: {}'.format(*fmt)
                    embed = Embed(title=system_name,
                                  color=Color.orange(),
                                  description=system_information)
                    url = 'https://www.edsm.net/api-system-v1/stations?sysname={}'.format(system)
                    f = await self.fetch(session, url)
                    stations_data = json.loads(f)
                    for station in stations_data['stations']:
                        station_name = station['name']
                        controlling_faction = station['controllingFaction']['name']
                        faction_abbreviation = ''.join([word[0] for word in controlling_faction.split(' ')])
                        options = []
                        if station['haveShipyard']:
                            options.append('shipyard')
                        if station['haveMarket']:
                            options.append('market')
                        if station['haveOutfitting']:
                            options.append('outfitting')
                        allegiances = {'Alliance': '<:alliancew:511914466498183178>',
                                       'Federation': '<:federationw:511911861026029579>',
                                       'Empire': '<:empirew:511914466418360331',
                                       'Independent': '<:independentw:511915084612632586>',
                                       'Pilots Federation': '<:pilots_federationw:511916795641331732>'}
                        all_logo = ''
                        if station['allegiance'] in allegiances:
                            all_logo = allegiances[station['allegiance']]
                        fmt = (all_logo, station_name, controlling_faction, faction_abbreviation)
                        embed.add_field(name='{} {} ◆ {} ({})'.format(*fmt),
                                        value='→ Services: {}'.format(', '.join(options)),
                                        inline=False)
                    thumbs = {'Independent': 'https://i.imgur.com/r4d7tPt.png',
                              'Alliance': 'https://i.imgur.com/OWf0P6u.png',
                              'Empire': 'https://i.imgur.com/KTmp5MF.png',
                              'Federation': 'https://i.imgur.com/3oT7gr0.png',
                              'Pilots Federation': 'https://i.imgur.com/tshl8xE.png',
                              'Guardian': 'https://edassets.org/static/img/power-ethos/Covert.png'}
                    embed.set_footer(text='Use system {}, <station name> for more details'.format(system_name))
                    embed.set_thumbnail(url=thumbs[allegiance])
                    await ctx.send(embed=embed)
                except Exception as e:
                    print(e)
                    raise

    @commands.command()
    async def dist(self, ctx, *args):
        async with aiohttp.ClientSession() as session:
            systems = ' '.join(args).split(',')
            system1, system2 = (systems[0].strip(), systems[1].strip())
            system1_fetch = await self.fetch(session, 'http://www.edsm.net/api-v1/system?sysname=' + system1 + '&coords=1')
            system2_fetch = await self.fetch(session, 'http://www.edsm.net/api-v1/system?sysname=' + system2 + '&coords=1')

            system1_json = json.loads(system1_fetch)
            system2_json = json.loads(system2_fetch)

            system1_name = system1_json['name']
            x1 = system1_json['coords']['x']
            y1 = system1_json['coords']['y']
            z1 = system1_json['coords']['z']

            system2_name = system2_json['name']
            x2 = system2_json['coords']['x']
            y2 = system2_json['coords']['y']
            z2 = system2_json['coords']['z']

            x = x2 - x1
            y = y2 - y1
            z = z2 - z1

            distance = round(sqrt(x ** 2 + y ** 2 + z ** 2) * 100) / 100

            courier = '<:courier:511301675198447616>'

            embed = Embed(
                description='{} {} {}: {} LY'.format(system1_name, courier, system2_name, distance),
                color=Color.blue())
            await ctx.send(embed=embed)

    @commands.command(aliases=['cmdr', 'CMDR'])
    async def pilot(self, ctx, *, pilot_name: str):
        try:
            with open('files/credentials.json') as f:
                data = json.load(f)
            json_data = {
                "header": {
                    "appName": "Artemis_Bot",
                    "appVersion": "0.7",
                    "isDeveloped": True,
                    "APIkey": data['inara'],
                    "commanderName": "Hatchet Jackk"
                },
                "events": [
                    {
                        "eventName": "getCommanderProfile",
                        "eventTimestamp": str(datetime.utcnow().isoformat()),
                        "eventData": {
                            "searchName": pilot_name
                        }
                    }
                ]
            }
            json_string = json.dumps(json_data)
            url = 'https://inara.cz/inapi/v1/'
            r = requests.post(url, json_string)
            pilot_data = list(r.json()['events'])[0]
            pilot_name = pilot_data['eventData']['commanderName']

            # get wing information
            if 'commanderWing' in pilot_data['eventData']:
                wing_name = pilot_data['eventData']['commanderWing']['wingName']
                wing_role = pilot_data['eventData']['commanderWing']['wingMemberRank']
            else:
                wing_name = 'No Wing'
                wing_role = 'No Role'
            preferred_role = pilot_data['eventData']['preferredGameRole']
            pilot_page = pilot_data['eventData']['inaraURL']

            # get pilot data by scraping pilot_page
            r = requests.get(pilot_page)
            soup = BeautifulSoup(r.content, 'lxml')
            table = soup.find('table', class_='pfl')
            table_data = []
            current_ship, ship_id, allegiance, credit_bal = '', '', '', ''
            pilot_information = table.find_all('tr')
            for row in pilot_information:
                cols = [value.text.strip() for value in row.find_all('td') if 'CMDR' not in value]
                table_data.append([value for value in cols if value])
            # remove cmdr from list
            del table_data[0]
            for value in table_data:
                if value[0].startswith('Registered ship name'):
                    current_ship = value[0].replace('Registered ship name', '')
                if value[0].startswith('Registered ship ID'):
                    ship_id = value[0].replace('Registered ship ID', '')
                if value[2].startswith('Credit Balance'):
                    credit_bal = value[2].replace('Credit Balance', '')
                if value[1].startswith('Allegiance'):
                    allegiance = value[1].replace('Allegiance', '')

            # get rank data
            rank_table_data = []
            rank_information = soup.findAll('div', class_='mainblock subblock textcenter')
            for rank in rank_information[0]:
                span = rank.find_all('span')
                span = [value.text.strip() for value in span]
                if span[0] == wing_name:
                    pass
                else:
                    rank_text = '{}: {}'.format(span[0], span[1])
                    rank_table_data.append(rank_text)
            action_ranks = '\n'.join(rank_table_data)

            # get allegiance data
            allegiance_table_data = []
            for value in rank_information[1]:
                span = [value.text.strip() for value in value.find_all('span')]
                allegiance_table_data.append('{}: {}'.format(span[0], span[1]))
            allegiance_ranks = '\n'.join(allegiance_table_data)

            fmt = (wing_name, wing_role.title(), preferred_role, allegiance, credit_bal, current_ship, ship_id,
                   action_ranks, allegiance_ranks, pilot_page)

            pilot_info = Embed(title='CMDR {}'.format(pilot_name),
                               color=Color.orange(),
                               description='**{}**, *{}*\n'
                                           '{}\n'
                                           'Allegiance: {}\n'
                                           'Balance: {}\n'
                                           'Current Ship: {} ({})\n\n'
                                           '__Ranks__\n'
                                           '{}\n\n'
                                           '__Reputation__\n'
                                           '{}\n\n'
                                           '{}'.format(*fmt))

            pilot_info.set_thumbnail(url='https://inara.cz/images/weblogo2.png')
            if 'avatarImageURL' in pilot_data['eventData']:
                pilot_info.set_thumbnail(url=pilot_data['eventData']['avatarImageURL'])
            await ctx.send(embed=pilot_info)

        except Exception as e:
            await ctx.send('Pilot not found.')
            print(e)
            raise


def setup(client):
    client.add_cog(EliteDangerous(client))
