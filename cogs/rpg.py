import random
from artemis import load_json, dump_json
from discord import Embed, Color
from discord.ext import commands


class RPG:
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def equip(self, ctx, *, item: str):
        rpg = await load_json('rpg')
        users = await load_json('users')
        for key, value in rpg['weapons'].items():
            if item in value:
                users[str(ctx.author.id)]['equipped']['weapon'] = item
                await dump_json('users', users)
                equipped = Embed(description='You equipped the {}!'.format(item))
                await ctx.send(embed=equipped)
                return
        for key, value in rpg['armor'].items():
            if item in value:
                users[str(ctx.author.id)]['equipped']['armor'] = item
                await dump_json('users', users)
                equipped = Embed(description='You equipped the {}!'.format(item))
                await ctx.send(embed=equipped)
                return
        for key, value in rpg['acc.'].items():
            if item in value:
                users[str(ctx.author.id)]['equipped']['acc.'] = item
                await dump_json('users', users)
                equipped = Embed(description='You equipped the {}!'.format(item))
                await ctx.send(embed=equipped)
                return

    @commands.command()
    async def status(self, ctx, *args):
        target_name = await self.member_name(ctx.author)
        avatar = ctx.author.avatar_url
        target = ctx.author
        if len(args) > 0:
            target = ' '.join(args)
            for member in ctx.guild.members:
                member_name = await self.member_name(member)
                if member_name.lower() == target.lower() or member.mention == target:
                    target_name = await self.member_name(member)
                    avatar = member.avatar_url
                    target = member
                    break
        users = await load_json('users')
        rpg = await load_json('rpg')
        hp = users[str(target.id)]['health']['hp']
        weapon = (users[str(target.id)]['equipped']['weapon'])
        damage = ''
        for key, value in rpg['weapons'].items():
            if weapon in value:
                damage = '[{}d{}]'.format(value[weapon]['rolls'], value[weapon]['limit'])
        armor = users[str(target.id)]['equipped']['armor']
        accessory = users[str(target.id)]['equipped']['acc.']
        alignment = None
        if users[str(target.id)]['alignment'] is not None:
            alignment = users[str(target.id)]['alignment']
        inventory_description = []
        for key, value in users[str(target.id)]['inventory'].items():
            if type(value) is list:
                values = [x for x in value]
                inventory_description.append('‣ {}: [{}] *{}*'.format(key, values[0], values[1]))
            else:
                inventory_description.append('‣ {}: *{}*'.format(key, value))
        status = Embed(title='{} ({}/100)'.format(target_name, hp),
                       color=Color.dark_blue(),
                       description='*{}*\n'
                                   'Level: 0\n'
                                   'Exp to Next: 0\n\n'
                                   '**__Equipped__**\n'
                                   '**Weapon**: {} {}\n'
                                   '**Armor**: {}\n'
                                   '**Acc.**: {}\n\n'
                                   '**__Inventory__**\n'
                                   '{}'.format(alignment, weapon, damage, armor, accessory,
                                               '\n'.join(value for value in inventory_description)))
        status.set_thumbnail(url=avatar)
        await ctx.send(embed=status)

    @commands.command(aliases=['inv'])
    async def inventory(self, ctx):
        users = await load_json('users')
        inventory_description = []
        for key, value in users[str(ctx.author.id)]['inventory'].items():
            if type(value) is list:
                values = [x for x in value]
                inventory_description.append('‣ {}: [{}] *{}*'.format(key, values[0], values[1]))
            else:
                inventory_description.append('‣ {}: *{}*'.format(key, value))
        inventory = Embed(title='Your Inventory',
                          color=Color.dark_blue(),
                          description='\n'.join(value for value in inventory_description))
        inventory.set_thumbnail(url='http://darksouls3.wdfiles.com/local--files/image-set-equipment:valorheart/Valorheart.png')
        await ctx.send(embed=inventory)

    @commands.group()
    async def set(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send('Invoke set with `alignment` or `description`!')

    @set.command()
    async def alignment(self, ctx, *, alignment: str):
        alignment_list = ['lawful good', 'neutral good', 'chaotic good',
                          'lauwful neutral', 'true neutral', 'chaotic neutral',
                          'lawful evil', 'neutral evil', 'chaotic evil']
        if alignment.lower() in alignment_list:
            users = await load_json('users')
            users[str(ctx.author.id)].update({'alignment': alignment})
            await dump_json('users', users)
            embed = Embed(title='Your alignment is now {}'.format(alignment))
            await ctx.send(embed=embed, delete_after=5)
        else:
            embed = Embed(title='{} was not found in the alignment list.'.format(alignment))
            await ctx.send(embed=embed, delete_after=5)

    @commands.command()
    async def store(self, ctx):
        message = ctx.message
        channel = ctx.channel
        client = self.client
        emojis = ctx.guild.emojis
        print(emojis)

        def check(m):
            return m.author == message.author and m.channel == channel

        store = Embed(title='The General Store',
                      description='Buy everything from potions to weapons to armor!',
                      color=Color.blue())
        store.add_field(name='<:orangepotion:509130865759092750>POTIONS', value='\u200b', inline=False)
        store.add_field(name=':crossed_swords:WEAPONS', value='\u200b', inline=False)
        store.add_field(name='<:armor:509132689530552330>ARMOR/ARMOUR', value='\u200b', inline=False)
        store.set_footer(text='Choose an option or enter to `quit` to stop shopping.')
        store_message = await ctx.send(embed=store)
        msg = await client.wait_for('message', check=check, timeout=30)

        exit_shop = ['quit', 'stop', 'q']
        if msg.content.lower() in exit_shop:
            await store_message.delete()
            return

        potions = ['potion', 'potions', 'pots']
        if msg.content.lower() in potions:
            await store_message.delete()
            await self.store_potions(ctx)

        weapons = ['weapons', 'weapon', 'weps']
        if msg.content.lower() in weapons:
            await store_message.delete()
            await self.store_weapons(ctx)

    async def store_potions(self, ctx):
        rpg_data = await load_json('rpg')

        def check(m):
            return m.author == ctx.message.author and m.channel == ctx.channel

        store = Embed(description='<:orangepotion:509130865759092750>Potions, potions, potions!',
                      color=Color.blue())
        store.set_footer(text='Purchase a potion with `buy <item>`\n'
                              'or enter `quit` to exit the shop')
        for key, value in rpg_data['items']['potions'].items():
            item_cost = value['buy']
            item_description = value['description']
            store.add_field(name='{}: {}GP'.format(key.upper(), item_cost),
                            value=item_description,
                            inline=False)
        store_message = await ctx.send(embed=store)
        while True:
            msg = await self.client.wait_for('message', check=check)

            exit_shop = ['quit', 'stop', 'q']
            if msg.content.lower() in exit_shop:
                await store_message.delete()
                break

            elif msg.content.startswith('buy'):
                item = msg.content[4:]
                cost = rpg_data['items']['potions'][item]['buy']
                user_data = await load_json('users')

                # check if the user can afford the item then subtract the cost
                if user_data[str(ctx.author.id)]['inventory']['gold'] >= cost:
                    user_data[str(ctx.author.id)]['inventory']['gold'] -= cost

                    # if potion item does not exist in inventory, add it
                    for key, value in rpg_data['items']['potions'].items():
                        if key == item and key not in user_data[str(ctx.author.id)]['inventory']:
                            user_data[str(ctx.author.id)]['inventory'].update({item: 0})

                    # add one to the item
                    user_data[str(ctx.author.id)]['inventory'][item] += 1
                    await dump_json('users', user_data)
                    purchase = Embed(description='You purchased a {} potion for {}GP.'.format(item, cost))
                    await ctx.send(embed=purchase, delete_after=3)
                else:
                    purchase = Embed(description='You do not have enough gold to purchase a {} potion.'.format(item))
                    await ctx.send(embed=purchase, delete_after=3)
            else:
                error = Embed(description='Purchase a potion with `buy <item>`\n'
                                          'or enter `quit` to exit the shop')
                await ctx.send(embed=error, delete_after=3)

    async def store_weapons(self, ctx):
        rpg_data = await load_json('rpg')

        def check(m):
            return m.author == ctx.message.author and m.channel == ctx.channel

        store = Embed(description=':crossed_swords:Wars may be fought with weapons, but they are won by men!',
                      color=Color.blue())
        store.set_footer(text='Choose an option or enter to `quit` to stop shopping.')
        store.add_field(name='\n'.join([wep.upper() for wep in rpg_data['weapons']]),
                        value='\u200b')
        store_message = await ctx.send(embed=store)

        while True:
            msg = await self.client.wait_for('message', check=check)

            exit_shop = ['quit', 'stop', 'q']
            if msg.content.lower() in exit_shop:
                await store_message.delete()
                return

            elif msg.content.lower() in rpg_data['weapons']:
                selection = msg.content.lower()
                await store_message.delete()
                store = Embed(description=':crossed_swords: What are ya buyin\'?',
                              color=Color.blue())
                store.set_footer(text='Purchase a weapon with `buy <item>`\n'
                                      'or enter `quit` to exit the shop')
                for key, value in rpg_data['weapons'][selection].items():
                    item_cost = value['buy']
                    rolls = rpg_data['weapons'][selection][key]['rolls']
                    limit = rpg_data['weapons'][selection][key]['limit']
                    damage = '{}d{}'.format(rolls, limit)
                    item_description = value['description']
                    store.add_field(name='{}: {}GP'.format(key.upper(), item_cost),
                                    value='Damage: {}\n{}'.format(damage, item_description),
                                    inline=False)
                store_message = await ctx.send(embed=store)

                while True:
                    msg = await self.client.wait_for('message', check=check)

                    exit_shop = ['quit', 'stop', 'q']
                    if msg.content.lower() in exit_shop:
                        await store_message.delete()
                        return

                    elif msg.content.startswith('buy'):
                        item = msg.content[4:]
                        cost = rpg_data['weapons'][selection][item]['buy']
                        user_data = await load_json('users')
                        if user_data[str(ctx.author.id)]['inventory']['gold'] >= cost:
                            user_data[str(ctx.author.id)]['inventory']['gold'] -= cost
                            wep = rpg_data['weapons'][selection][item]
                            user_data[str(ctx.author.id)]['inventory'][item] = (
                                '{}d{}'.format(wep['rolls'], wep['limit']), wep['description'])
                            await dump_json('users', user_data)
                            purchase = Embed(description='You purchased a {} for {}GP.'.format(item, cost))
                            await ctx.send(embed=purchase, delete_after=3)
                            await store_message.delete()
                        else:
                            purchase = Embed(description='You do not have enough gold to purchase a {}.'.format(item))
                            await ctx.send(embed=purchase, delete_after=3)
                            await store_message.delete()
                    else:
                        error = Embed(description='Purchase a weapon with `buy <item>`\n'
                                                  'or enter `quit` to exit the shop')
                        await ctx.send(embed=error, delete_after=3)
            else:
                error = Embed(description='Select a category or enter `quit` to exit.')
                await ctx.send(embed=error, delete_after=3)

    @staticmethod
    async def calculate_health_potion(hp_regain):
        rolls = [random.randint(1, hp_regain[1]) for rolls in range(hp_regain[0])]
        return sum(rolls) + hp_regain[2]

    @staticmethod
    async def member_name(member):
        # grab author nick
        member_name = member.nick
        if member_name is None:
            member_name = member.name
        return member_name


def setup(client):
    client.add_cog(RPG(client))
