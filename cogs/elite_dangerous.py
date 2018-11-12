import requests
import json
import aiohttp
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
                    distance_from_star = station['distanceToArrival']
                    station_type = station['type']
                    thumbs = {'Outpost': 'https://edassets.org/static/img/stations/Outpost.png',
                              'Orbis Starport': 'https://edassets.org/static/img/stations/Orbis_sm.png',
                              'Coriolis Starport': 'https://edassets.org/static/img/stations/Coriolis_sm.png'}
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
                    embed.set_thumbnail(url=thumbs[station_type])
                    embed.set_footer(text='Distance from star: {} LS'.format(distance_from_star))
                    await ctx.send(embed=embed)
                    return
        else:
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
                faction_state = system_data.json()['information']['factionState']
                primary_start_scoopable = system_data.json()['primaryStar']['isScoopable']
                fmt = (faction, faction_state, allegiance, primary_start_scoopable)
                system_information = '**Faction**: {}\n' \
                                     '**State**: {}\n' \
                                     '**Allegiance**: {}\n' \
                                     '**Primary Star Scoopable**: {}'.format(*fmt)

            url = 'https://www.edsm.net/api-system-v1/stations?sysname={}'.format(system)
            stations_data = requests.get(url)
            stations_data = json.loads(stations_data.text)
            stations = ['{} - *{}*'.format(station['name'], station['controllingFaction']['name']) for station in stations_data['stations']]
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
                      'Federation': 'https://edassets.org/static/img/factions/Federation.png'}
            embed.set_thumbnail(url=thumbs[allegiance])
            await ctx.send(embed=embed)

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

    @commands.command()
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
                    "APIkey": inara_api
                    },
                "events": [{
                    "eventName": "getCommanderProfile",
                    "eventTimestamp": str(datetime.utcnow().isoformat()),
                    "eventData": {
                        "searchName": pilot_name
                    }
                }]
            }
            json_string = json.dumps(json_data)
            url = 'https://inara.cz/inapi/v1/'
            r = requests.post(url, json_string)
            print(r.status_code, r.reason)
            print(r.text)
        except Exception as e:
            print(e)


def setup(client):
    client.add_cog(EliteDangerous(client))
