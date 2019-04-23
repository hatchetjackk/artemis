import aiohttp
import json
import cogs.utilities as utilities
from bs4 import BeautifulSoup
from math import sqrt
from datetime import datetime
from discord.ext import commands


class EliteDangerous(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.wanted_blacklist = ['Knights of Karma']

    @commands.group(aliases=['ed'])
    async def elite(self, ctx):
        if ctx.invoked_subcommand is None:
            await utilities.single_embed(
                color=utilities.color_alert,
                title='Try `elite help` for more options.',
                channel=ctx
            )

    @elite.group()
    async def help(self, ctx):
        await utilities.single_embed(
            channel=ctx,
            color=utilities.color_help,
            name='Elite Help',
            value='`elite help` This menu!\n'
                  '`wanted` List Wanted CMDRs for this guild\n'
                  '`wanted add` Add a CMDR to the Wanted list\n'
                  '`wanted remove [cmdr]` Remove a CMDR from the Wanted list\n'
                  '`faction [faction_name]` Get details about a faction\n'
                  '`system [system_name]` Get details about a system name\n'
                  '`dist [system1], [system2]` Get the distance between two systems\n'
                  '`cmdr [cmdr_name]` Get details about a CMDR (must be in INARA)')

    @commands.group()
    async def wanted(self, ctx):
        if ctx.guild.name in self.wanted_blacklist:
            return
        if ctx.invoked_subcommand is None:
            messages = []
            conn, c = await utilities.load_db()
            c.execute("SELECT * FROM ed_wanted WHERE guild_id = (:guild_id)", {'guild_id': ctx.guild.id})
            wanted_commanders = c.fetchall()
            if len(wanted_commanders) == 0:
                messages.append(['No CMDRs on the WANTED list.', 'Nothing to see here.'])
            else:
                for commander in wanted_commanders:
                    cmdr_name, reason, inara_page, guild_id, member_id = commander
                    messages.append([cmdr_name.title(), f'Reason: {reason}\n{inara_page}'])
            await utilities.multi_embed(
                color=utilities.color_elite,
                title='Wanted CMDRs',
                messages=messages,
                channel=ctx
            )

    @wanted.group()
    async def add(self, ctx):
        try:
            if ctx.guild.name == any(self.wanted_blacklist):
                return
            await utilities.single_embed(
                color=utilities.color_elite,
                name='Add a CMDR to the Wanted List',
                value='What is the CMDR\'s name?',
                channel=ctx
            )

            def check(m):
                return m.author == ctx.message.author and m.channel == ctx.channel
            msg = await self.client.wait_for('message', check=check)
            wanted_cmdr = msg.content
            await ctx.channel.purge(limit=2)

            await utilities.single_embed(
                color=utilities.color_elite,
                name='Add a CMDR to the Wanted List',
                value='Why are you adding them to the list?',
                channel=ctx
            )
            msg = await self.client.wait_for('message', check=check)
            reason = msg.content
            await ctx.channel.purge(limit=2)
            inara_page = await self.get_pilot_information(wanted_cmdr)
            if inara_page is None:
                inara_page = 'CMDR not found in INARA'
            conn, c = await utilities.load_db()
            with conn:
                c.execute("INSERT INTO ed_wanted VALUES(:cmdr_name, :reason, :inara_page, :guild_id, :member_id)",
                          {'cmdr_name': wanted_cmdr.lower(), 'reason': reason, 'inara_page': inara_page,
                           'guild_id': ctx.guild.id, 'member_id': ctx.author.id})
            await utilities.single_embed(
                color=utilities.color_elite,
                name=f'{wanted_cmdr.title()} added to the Wanted List.',
                value='View the list with `wanted`.',
                channel=ctx
            )
        except Exception as e:
            await utilities.err_embed(
                name=f'An unexpected error occurred when adding a CMDR to the WANTED list', value=e, channel=ctx
            )
            raise

    @wanted.group(aliases=['delete', 'del'])
    async def remove(self, ctx, *, wanted_cmdr: str):
        # todo add check to see if the cmdr is in the database before trying to remove
        try:
            if ctx.guild.name == any(self.wanted_blacklist):
                return
            conn, c = await utilities.load_db()
            with conn:
                c.execute("DELETE FROM ed_wanted WHERE cmdr_name = (:cmdr_name) AND guild_id = (:guild_id)",
                          {'cmdr_name': wanted_cmdr.lower(), 'guild_id': ctx.guild.id})
            await utilities.single_embed(
                color=utilities.color_elite,
                title=f'{wanted_cmdr.title()} removed from WANTED list.',
                channel=ctx
            )
        except Exception as e:
            await utilities.err_embed(
                name='An error occurred when attempting to remove a CMDR from the Wanted List.',
                value = e,
                channel=ctx
            )

    @commands.command()
    async def faction(self, ctx, *, faction: str):
        await utilities.single_embed(
            color=utilities.color_elite,
            title='Please wait a moment while I gather faction data...',
            channel=ctx,
            delete_after=4
        )
        async with aiohttp.ClientSession() as session:
            try:
                url = f'http://elitebgs.kodeblox.com/api/eddb/v3/factions?name={faction}'
                f = await utilities.fetch(session, url)
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
                    f = await utilities.fetch(session, url)
                    values = json.loads(f)['docs'][0]
                    home_system_name = values['name']
                else:
                    home_system_name = 'None'
                fmt = (government, allegiance, player_faction, home_system_name)

                messages = []
                if faction_id is not None:
                    url = 'https://eddb.io/faction/{}'.format(faction_id)
                    f = await utilities.fetch(session, url)
                    soup = BeautifulSoup(f, 'lxml')
                    faction_system_information = soup.findAll('tr', class_='systemRow')
                    for system in faction_system_information:
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
                        messages.append([faction_system_name, '\n'.join(fmt)])

                thumbs = {'Independent': 'https://i.imgur.com/r4d7tPt.png',
                          'Alliance': 'https://i.imgur.com/OWf0P6u.png',
                          'Empire': 'https://i.imgur.com/KTmp5MF.png',
                          'Federation': 'https://i.imgur.com/3oT7gr0.png',
                          'Pilots Federation': 'https://i.imgur.com/tshl8xE.png',
                          'Guardian': 'https://edassets.org/static/img/power-ethos/Covert.png'}
                await utilities.multi_embed(
                    color=utilities.color_elite,
                    title=faction_name,
                    description='Government: {}\nAllegiance: {}\nPlayer Faction: {}\nHome System: {}'.format(*fmt),
                    messages=messages,
                    thumb_url=thumbs[allegiance],
                    channel=ctx,
                    footer=f'Last Updated: {last_update}'
                )
            except Exception as e:
                await utilities.single_embed(
                    color=utilities.color_alert,
                    title=f'Faction `{faction}` not found!',
                    description='Please check your spelling.',
                    channel=ctx
                )
                print(f'An error occurred when searching for faction {faction}: {e}')

    @commands.command()
    async def system(self, ctx, *args):
        await utilities.single_embed(
            color=utilities.color_elite,
            title='Please wait a moment while I gather system data...',
            channel=ctx,
            delete_after=4
        )
        args = ' '.join(args).split(',')
        async with aiohttp.ClientSession() as session:
            if len(args) > 1:
                system, station_name = args[0].strip(), args[1].strip()
                url = f'https://www.edsm.net/api-system-v1/stations?sysname={system}'
                f = await utilities.fetch(session, url)
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
                        thumb_url = 'https://edassets.org/static/img/stations/Outpost.png'
                        if station_type in thumbs:
                            thumb_url = thumbs[station_type]

                        await utilities.single_embed(
                            color=utilities.color_elite,
                            footer=f'Distance from arrival star: {distance_from_star} LS',
                            thumb_url=thumb_url,
                            channel=ctx,
                            title=f'{name}, {system}',
                            description='Station Type: {}\n'
                                        'Controlling Faction: {} ({})\n'
                                        'Government: {}\n'
                                        'Allegiance: {}\n'
                                        'Economy: {}\n'
                                        'Market: {}\n'
                                        'Shipyard: {}\n'
                                        'Outfitting: {}'.format(*fmt)
                        )
                        return
            else:
                try:
                    system = args[0].strip()
                    url = f'https://www.edsm.net/api-v1/system?sysname={system}' \
                        f'&coords=1&showInformation=1&showPrimaryStar=1'
                    f = await utilities.fetch(session, url)
                    system_data = json.loads(f)
                    system_name = system_data['name']
                    system_information = ''
                    allegiance = 'Independent'
                    if len(system_data['information']) > 0:
                        allegiance = system_data['information']['allegiance']
                        faction = system_data['information']['faction']
                        government = system_data['information']['government']
                        faction_state = system_data.get('information').get('factionState')
                        faction_abbr = ''.join([word[0] for word in faction.split(' ')])
                        primary_start_scoopable = system_data['primaryStar']['isScoopable']
                        fmt = (faction, faction_abbr, government, faction_state, allegiance, primary_start_scoopable)
                        system_information = '**Faction**: {} ({})\n' \
                                             '**Government**: {}\n' \
                                             '**State**: {}\n' \
                                             '**Allegiance**: {}\n' \
                                             '**Primary Star Scoopable**: {}'.format(*fmt)

                    messages = []
                    url = f'https://www.edsm.net/api-system-v1/stations?sysname={system}'
                    f = await utilities.fetch(session, url)
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
                        allegiances = {'Alliance': '[all]',
                                       'Federation': '[fed]',
                                       'Empire': '[emp]',
                                       'Independent': '[ind]',
                                       'Pilots Federation': '[plt]'}
                        allegiance_logo = ''
                        if station['allegiance'] in allegiances:
                            allegiance_logo = allegiances[station['allegiance']]
                        fmt = (allegiance_logo, station_name, controlling_faction, faction_abbreviation)
                        messages.append(['{} {} ◆ {} ({})'.format(*fmt), '→ Services: {}'.format(', '.join(options))])
                    thumbs = {'Independent': 'https://i.imgur.com/r4d7tPt.png',
                              'Alliance': 'https://i.imgur.com/OWf0P6u.png',
                              'Empire': 'https://i.imgur.com/KTmp5MF.png',
                              'Federation': 'https://i.imgur.com/3oT7gr0.png',
                              'Pilots Federation': 'https://i.imgur.com/tshl8xE.png',
                              'Guardian': 'https://edassets.org/static/img/power-ethos/Covert.png'}
                    await utilities.multi_embed(
                        color=utilities.color_elite,
                        channel=ctx,
                        thumb_url=thumbs[allegiance],
                        title=system_name,
                        description=system_information,
                        messages=messages,
                        footer=f'Use system [system_name] for more details.'
                    )
                except Exception as e:
                    await utilities.single_embed(
                        color=utilities.color_alert,
                        title=f'System `{system}` not found!',
                        description='Please check your spelling.',
                        channel=ctx
                    )
                    print(f'[{datetime.now()}] An error occurred when retrieving data for a system: {e}')
                    raise

    @commands.command(aliases=['dist', 'distance'])
    async def distance_calculator(self, ctx, *args):
        systems = ' '.join(args).split(',')
        system1, system2 = (systems[0].strip(), systems[1].strip())

        await utilities.single_embed(
            color=utilities.color_elite,
            title=f'Calculating distance between {system1.title()} and {system2.title()}',
            channel=ctx,
            delete_after=3
        )

        async with aiohttp.ClientSession() as session:
            url = 'http://www.edsm.net/api-v1/system?sysname={0}&coords=1'
            system1 = json.loads(await utilities.fetch(session, url.format(system1)))
            system2 = json.loads(await utilities.fetch(session, url.format(system2)))

            system1_name = system1['name']
            x1 = system1['coords']['x']
            y1 = system1['coords']['y']
            z1 = system1['coords']['z']

            system2_name = system2['name']
            x2 = system2['coords']['x']
            y2 = system2['coords']['y']
            z2 = system2['coords']['z']

            x = x2 - x1
            y = y2 - y1
            z = z2 - z1

            distance = round(sqrt(x ** 2 + y ** 2 + z ** 2) * 100) / 100

            await utilities.single_embed(
                color=utilities.color_elite,
                title=f':rocket: {system1_name} to {system2_name}: {distance} LY',
                channel=ctx
            )

    @commands.command(aliases=['cmdr', 'pilot'])
    async def pilot_information(self, ctx, *, pilot_name: str):
        await utilities.single_embed(
            color=utilities.color_elite,
            title='Please wait a moment while I gather CMDR data...',
            channel=ctx,
            delete_after=4
        )
        try:
            json_data = {
                "header": {
                    "appName": "Artemis_Bot",
                    "appVersion": "0.7",
                    "isDeveloped": True,
                    "APIkey": utilities.inara_api,
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
            async with aiohttp.ClientSession() as session:
                f = json.loads(await utilities.post(session, 'https://inara.cz/inapi/v1/', json_data))

                pilot_data = list(f['events'])[0]
                pilot_name = pilot_data['eventData']['commanderName']

                # get wing information
                if 'commanderWing' in pilot_data['eventData']:
                    wing_name = pilot_data['eventData']['commanderWing']['wingName']
                    wing_role = pilot_data['eventData']['commanderWing']['wingMemberRank']
                else:
                    wing_name = 'No Wing'
                    wing_role = 'No Role'
                try:
                    preferred_role = pilot_data['eventData']['preferredGameRole']
                except Exception as e:
                    print('An error occurred when retrieving preferred role for {}: {}'.format(pilot_name, e))
                    preferred_role = None
                pilot_page = pilot_data['eventData']['inaraURL']

                # get pilot data by scraping pilot_page
                r = await utilities.fetch(session, pilot_page)
                soup = BeautifulSoup(r, 'lxml')
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

                avatar = pilot_data.get('eventData').get('avatarImageURL')
                if avatar is None:
                    avatar = 'https://inara.cz/images/weblogo2.png'

                await utilities.single_embed(
                    color=utilities.color_elite,
                    title=f'CMDR {pilot_name}',
                    description=''
                    f'**{wing_name}**, *{wing_role.title()}*\n'
                    f'{preferred_role}\n'
                    f'Allegiance: {allegiance}\n'
                    f'Balance: {credit_bal}\n'
                    f'Current Ship: {current_ship} ({ship_id})\n'
                    f'\n'
                    f'__Ranks__\n'
                    f'{action_ranks}\n'
                    f'\n'
                    f'__Reputation__\n'
                    f'{allegiance_ranks}\n'
                    f'\n'
                    f'{pilot_page}',
                    channel=ctx,
                    thumb_url=avatar
                )

        except Exception as e:
            print(e)
            await utilities.single_embed(
                color=utilities.color_alert,
                title=f'Pilot "{pilot_name}" not found!',
                description='Please check your spelling.\n'
                            'It is possible this CMDR is not in INARA.',
                channel=ctx
            )
            raise

    @staticmethod
    async def get_pilot_information(cmdr_name):
        try:
            json_data = {
                "header": {
                    "appName": "Artemis_Bot",
                    "appVersion": "0.7",
                    "isDeveloped": True,
                    "APIkey": utilities.inara_api,
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
            async with aiohttp.ClientSession() as session:
                f = json.loads(await utilities.post(session, 'https://inara.cz/inapi/v1/', json_data))
                pilot_data = list(f['events'])[0]
                pilot_page = pilot_data['eventData']['inaraURL']
                if pilot_page is None:
                    return None
                return pilot_page
        except Exception as e:
            print('[{}] An error occurred when retrieving pilot information error: {}'.format(datetime.now(), e))
            return None


def setup(client):
    client.add_cog(EliteDangerous(client))
