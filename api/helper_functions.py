from .models import *
import random
from faker import Faker
from random import randint
from decimal import Decimal

""" 
Helper function for system to generate player data
automatically when user signups from url or admin
creates new user from the admin panel
"""

fake = Faker()

def user_register_create_team_and_players(user, team_name, team_country):
    team = Team.objects.create(owner=user, name=team_name, country=team_country)
    positions = ['Goalkeeper']*3 + ['Defender']*6 + ['Midfielder']*6 + ['Attacker']*5
    for position in positions:
        player = Player.objects.create( 
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            country=random.choice(COUNTRIES),
            age=random.randint(18, 40),
            position=position
        )
        team.players.add(player)
    team.save()

"""
Helper function to show full name of players when a user
list players for selling on transfer list from url
"""

def transfer_list_name_instead_of_id(instance):
    data = {}
    data['player'] = instance.player.first_name + ' ' + instance.player.last_name
    data['asking_price'] = f'$ {instance.asking_price}'
    return data
    

"""
Helper Function for Market List Serializer
"""

def market_list_serializer_helper(obj):
    data = {}
    data['player_name'] = f'{obj.transfer_list.player.first_name} {obj.transfer_list.player.last_name}'
    data['player_country'] = obj.transfer_list.player.country
    data['team_name'] = obj.transfer_list.player.team_set.first().name if obj.transfer_list.player.team_set.exists() else None
    data['asking_price'] = f"$ {obj.transfer_list.asking_price}"
    return data

"""
Helper function for Buy Player View
"""

def buy_player(serializer, username):
    player = serializer.validated_data['player']
    buyer_team = Team.objects.get(owner__username=username)
    seller_team = player.team_set.first()

    # Get the asking price from the TransferList
    asking_price = TransferList.objects.get(player=player).asking_price

    # Check if the price provided by the user matches the asking price
    if serializer.validated_data['price'] < asking_price:
        return ('Warning', 'Price must be equal. The current price is less than asking price.')
    elif serializer.validated_data['price'] > asking_price:
        return ('Warning', 'Price must be equal. The current price is more than asking price.')

    # Update team budgets
    buyer_team.budget -= serializer.validated_data['price']
    seller_team.budget += serializer.validated_data['price']

    # Increase player value by a random percentage between 10 and 100
    increase_percentage = Decimal(randint(10, 100)) / 100
    player.market_value *= (1 + increase_percentage)

    # Update teams and player
    buyer_team.players.add(player)
    seller_team.players.remove(player)
    player.listing_status = 'Not Listed'
    player.save()
    buyer_team.save()
    seller_team.save()

    # Remove player from TransferList and MarketList
    TransferList.objects.filter(player=player).delete()
    MarketList.objects.filter(transfer_list__player=player).delete()

    return ('Success', f'Congratulations *{username}*, you successfully bought *{player.first_name} {player.last_name}*.')
