import requests
import json
import aiohttp
import html5lib
import lxml
from bs4 import BeautifulSoup
from artemis import load_json
from discord import Embed, Color
from math import sqrt
from datetime import datetime
from discord.ext import commands


class EliteDangerous:
    def __init__(self, client):
        self.client = client

    @staticmethod
    async def fetch(session, url):
        async with session.get(url) as response:
            return await response.text()

    @commands.command()
    async def faction(self, ctx, *args):
        faction = ' '.join(args)
        url = 'http://elitebgs.kodeblox.com/api/eddb/v3/factions?name={}'.format(faction)
        r = requests.get(url)
        values = list(r.json()['docs'])[0]
        faction_name = values['name']
        government = values['government'].title()
        allegiance = values['allegiance'].title()
        player_faction = values['is_player_faction']
        last_update = values['updated_at']
        home_system_id = values['home_system_id']
        if home_system_id is not None:
            url = 'http://elitebgs.kodeblox.com/api/eddb/v3/systems?eddbid={}'.format(home_system_id)
            r = requests.get(url)
            values = list(r.json()['docs'])[0]
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
        thumbs = {'Independent': 'https://edassets.org/static/img/squadrons/independent-power.png',
                  'Alliance': 'https://edassets.org/static/img/factions/Alliance.png',
                  'Empire': 'https://edassets.org/static/img/factions/Empire.png',
                  'Federation': 'https://edassets.org/static/img/factions/Federation.png',
                  'Pilots Federation': 'https://edassets.org/static/img/pilots-federation/rank-9.png',
                  'Guardian': 'https://edassets.org/static/img/power-ethos/Covert.png'}
        embed.set_thumbnail(url=thumbs[allegiance])
        embed.set_footer(text='Last Updated: {}'.format(last_update))
        await ctx.send(embed=embed)

    @commands.command()
    async def system(self, ctx, *args):
        args = ' '.join(args).split(',')
        if len(args) > 1:
            system, station_name = args[0].strip(), args[1].strip()
            url = 'https://www.edsm.net/api-system-v1/stations?sysname={}'.format(system)
            stations_data = requests.get(url)
            stations_data = json.loads(stations_data.text)
            system = stations_data['name']
            for station in stations_data['stations']:
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
                    thumbs = {'Outpost': 'https://edassets.org/static/img/stations/Outpost.png',
                              'Orbis Starport': 'https://edassets.org/static/img/stations/Orbis_sm.png',
                              'Coriolis Starport': 'https://edassets.org/static/img/stations/Coriolis_sm.png',
                              'Planetary Outpost': 'https://edassets.org/static/img/settlements/surface_port_pm.png',
                              'Planetary Settlement': 'https://edassets.org/static/img/settlements/settlement_pm.png',
                              'Ocellus Starport': 'https://edassets.org/static/img/stations/Ocellus.png',
                              'Mega ship': 'https://edassets.org/static/img/stations/Mega-Ship_Icon.png'}
                    fmt = (station_type, controlling_faction, government,
                           allegiance, economy, market, shipyard, outfitting)
                    embed = Embed(title='{}, {}'.format(name, system),
                                  color=Color.orange(),
                                  description='Station Type: {}\n'
                                              'Controlling Faction: {}\n'
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
                system_data = requests.get(url)
                system_name = system_data.json()['name']
                coordinates = (system_data.json()['coords']['x'],
                               system_data.json()['coords']['y'],
                               system_data.json()['coords']['z'])
                system_information = ''
                allegiance = 'Independent'
                if len(system_data.json()['information']) > 0:
                    allegiance = system_data.json()['information']['allegiance']
                    faction = system_data.json()['information']['faction']
                    government = system_data.json()['information']['government']
                    if 'factionState' not in system_data.json()['information']:
                        faction_state = None
                    else:
                        faction_state = system_data.json()['information']['factionState']
                    primary_start_scoopable = system_data.json()['primaryStar']['isScoopable']
                    fmt = (faction, government, faction_state, allegiance, primary_start_scoopable)
                    system_information = '**Faction**: {}\n' \
                                         '**Government**: {}\n' \
                                         '**State**: {}\n' \
                                         '**Allegiance**: {}\n' \
                                         '**Primary Star Scoopable**: {}'.format(*fmt)

                url = 'https://www.edsm.net/api-system-v1/stations?sysname={}'.format(system)
                stations_data = requests.get(url)
                stations_data = json.loads(stations_data.text)
                # print(stations_data)
                s, o, m = '', '', ''
                stations = []
                for station in stations_data['stations']:
                    station_name = station['name']
                    controlling_faction = station['controllingFaction']['name']
                    faction_abbreviation = ''.join([word[0] for word in controlling_faction.split(' ')])
                    if station['haveShipyard']:
                        s = 's'
                    if station['haveMarket']:
                        m = 'm'
                    if station['haveOutfitting']:
                        o = 'o'

                    fmt = (station_name, ''.join(s+m+o), faction_abbreviation)
                    stations.append('{}  [*{}*] - *{}*'.format(*fmt))

                stations_information = ''
                if len(stations) > 0:
                    stations_information = '**Stations**: \n{}'.format('\n'.join(stations))
                embed = Embed(title=system_name,
                              color=Color.orange(),
                              description='{}\n\n{}'.format(system_information, stations_information))
                embed.set_footer(text='x: {}, y: {}, z: {}'.format(*coordinates))
                thumbs = {'Independent': 'https://edassets.org/static/img/squadrons/independent-power.png',
                          'Alliance': 'https://edassets.org/static/img/factions/Alliance.png',
                          'Empire': 'https://edassets.org/static/img/factions/Empire.png',
                          'Federation': 'https://edassets.org/static/img/factions/Federation.png',
                          'Pilots Federation': 'https://edassets.org/static/img/pilots-federation/rank-9.png',
                          'Guardian': 'https://edassets.org/static/img/power-ethos/Covert.png'}
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
    async def pilot(self, ctx, *args):
        try:
            user_input = ' '.join(args).split(',')
            pilot_name = user_input[0].strip()
            data = await load_json('credentials')
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
