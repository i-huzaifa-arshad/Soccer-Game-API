from .models import Team, Player, TransferList, MarketList
import random
from faker import Faker
import pycountry
from random import randint
from decimal import Decimal
from rest_framework import status
from rest_framework.response import Response
from django.contrib.admin import SimpleListFilter


"""
Helper function for system to generate player data
automatically when user signups from url or admin
creates new user from the admin panel
"""

fake = Faker()
COUNTRIES = [country.name for country in pycountry.countries]


def user_register_create_team_and_players(user, team_name, team_country):
    team = Team.objects.create(owner=user, name=team_name, country=team_country)
    positions = (
        ["Goalkeeper"] * 3 + ["Defender"] * 6 + ["Midfielder"] * 6 + ["Attacker"] * 5
    )
    for position in positions:
        player = Player.objects.create(
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            country=random.choice(COUNTRIES),
            age=random.randint(18, 40),
            position=position,
            team=team,
        )
        team.players.add(player)
        # Calculating team_value (combined player market value)
        team.team_value += player.market_value
    # Calculating team final_value (team_value + team_budget)
    team.final_value = team.team_value + team.budget
    team.save()


"""
Helper function to show full name of players when a user
list players for selling on transfer list from url
"""


def transfer_list_name_instead_of_id(instance):
    data = {}
    data["player"] = instance.player.first_name + " " + instance.player.last_name
    data["asking_price"] = f"$ {instance.asking_price}"
    return data


"""
Helper Function for Market List Serializer
"""


def market_list_serializer_helper(obj):
    data = {}
    data["player_name"] = (
        f"{obj.transfer_list.player.first_name} {obj.transfer_list.player.last_name}"
    )
    data["player_country"] = obj.transfer_list.player.country
    data["team_name"] = obj.transfer_list.player.team.name
    data["position"] = obj.transfer_list.player.position
    data["asking_price"] = f"$ {obj.transfer_list.asking_price}"
    return data


"""
Helper function for Buy Player View Calculations
"""


def buy_player(serializer, username):
    player = serializer.validated_data["player"]
    buyer_team = Team.objects.get(owner__username=username)
    seller_team = player.team

    # Get the asking price from the TransferList
    asking_price = TransferList.objects.get(player=player).asking_price

    # Check if the price provided by the user matches the asking price
    if serializer.validated_data["price"] < asking_price:
        return Response(
            {
                "status": "Warning",
                "message": "The current price is *less* than asking price.",
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    elif serializer.validated_data["price"] > asking_price:
        return Response(
            {
                "status": "Warning",
                "message": "The current price is *more* than asking price.",
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Update team budgets
    buyer_team.budget -= serializer.validated_data["price"]
    seller_team.budget += serializer.validated_data["price"]

    # Increase player value by a random percentage between 10 and 100
    increase_percentage = Decimal(randint(10, 100)) / 100
    player.market_value *= 1 + increase_percentage

    # Update teams and player
    player.team = buyer_team  # Set the player's team to the buyer team
    player.listing_status = "Not Listed"
    player.save()

    # Update the Buyer team_value and final_value
    buyer_team.team_value += player.market_value
    buyer_team.final_value = buyer_team.team_value + buyer_team.budget
    buyer_team.save()

    # Update the Seller team_value and final_value
    seller_team.team_value -= player.market_value
    seller_team.final_value = seller_team.team_value + seller_team.budget
    seller_team.save()

    # Remove player from TransferList and MarketList
    TransferList.objects.filter(player=player).delete()
    MarketList.objects.filter(transfer_list__player=player).delete()

    return Response(
        {
            "status": "Success",
            "message": f"Congratulations *{username}*, you successfully bought *{player.first_name} {player.last_name}*.",
        },
        status=status.HTTP_200_OK,
    )


"""
Helper Class for Market List Admin
Country Filter
"""


class CountryFilter(SimpleListFilter):
    title = "country"
    parameter_name = "country"

    def lookups(self, request, model_admin):
        countries = set(
            [cn.transfer_list.player.country for cn in model_admin.model.objects.all()]
        )
        return [(cn, cn) for cn in countries]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(transfer_list__player__country=self.value())
