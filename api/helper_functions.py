from .models import *
import random
from faker import Faker

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
