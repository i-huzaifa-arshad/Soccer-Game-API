from django.contrib import admin
from .models import *
from faker import Faker
import random

"""Customization of the admin panel"""

# Customize User admin page

fake = Faker()
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'name', 'email')
    search_fields = ("username",)

    # To automatically generate players data when admin add a new user from admin panel
     
    def save_model(self, request, obj, form, change):
        if not change or not obj.pk:
            obj.set_password(obj.password)
            obj.save()
            if obj.team_name and obj.team_country:
                team = Team.objects.create(owner=obj, name=obj.team_name, country=obj.team_country)

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
        else:
            if obj.pk:
                orig_obj = CustomUser.objects.get(pk=obj.pk)
                if obj.password != orig_obj.password:
                    obj.set_password(obj.password)
            obj.save()


# Customize Player admin page
    
class PlayerAdmin(admin.ModelAdmin):
    def teams(self, obj):
        return ", ".join([team.name for team in obj.team_set.all()])
    teams.short_description = 'Team Name'
    list_display = ('first_name', 'last_name', 'teams', 'listing_status')
    search_fields = ("first_name",)
    list_filter = ('team__name', 'listing_status',)

# Customize Teams admin page
    
class TeamAdmin(admin.ModelAdmin):

    def owner_name(self, obj):
        return obj.owner.name
    owner_name.short_description = 'Owner Name'

    def team_name(self, obj):
        return obj.name
    team_name.short_description = 'Team Name'

    list_display = ('team_name', 'owner_name')
    search_fields = ('name',)

# Customize Player Transfer admin page

class TransferListAdmin(admin.ModelAdmin):

    def player_name(self, obj):
        return f'{obj.player.first_name} {obj.player.last_name}'
    player_name.short_description = 'Player Name'

    def team_name(self, obj):
        team = obj.player.team_set.first()
        return team.name if team else None
    team_name.short_description = 'Team Name'

    def price(self, obj):
        return f'$ {obj.asking_price}'
    price.short_description = 'Asking Price'

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        
        # Create a MarketList entry for the player
        MarketList.objects.create(transfer_list=obj)

    list_display = ('player_name', 'team_name', 'price')
    list_filter = ('player__team__name',)

# Customize Market List admin Page

class MarketListAdmin(admin.ModelAdmin):
    def player_name(self, obj):
        return f'{obj.transfer_list.player.first_name} {obj.transfer_list.player.last_name}'
    player_name.short_description = 'Player Name'

    def price(self, obj):
        return f'$ {obj.transfer_list.asking_price}'
    price.short_description = 'Asking Price'

    def team_name(self, obj):
        return obj.transfer_list.player.team_set.first().name if obj.transfer_list.player.team_set.exists() else None
    team_name.short_description = 'Team Name'

    def country(self, obj):
        return obj.transfer_list.player.country
    country.short_description = 'Country'

    list_display = ('player_name', 'price', 'team_name', 'country')
    list_filter = ('transfer_list__player__team__name', 'country',)

