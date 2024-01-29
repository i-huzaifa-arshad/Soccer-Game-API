from django.contrib import admin
from django import forms
from .models import *
from .helper import *

""" Customization of the admin panel """

# Customize User admin page

# A simple form to input user details

class CustomUserForm(forms.ModelForm):
    team_name = forms.CharField(max_length=100)
    team_country = forms.ChoiceField(choices=[(country.name, country.name) for country in pycountry.countries])

    class Meta:
        model = CustomUser
        fields = ['username', 'name', 
                  'email', 'password', 
                  'team_name', 'team_country'
                ]

class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'name', 'email')
    search_fields = ("username",)
    form = CustomUserForm

    def save_model(self, request, obj, form, change):
        team_name = form.cleaned_data.get('team_name')
        team_country = form.cleaned_data.get('team_country')
        if not change or not obj.pk:
            obj.set_password(obj.password)
            obj.save()
            if team_name and team_country:
                user_register_create_team_and_players(obj, team_name, team_country)
        else:
            if obj.pk:
                orig_obj = CustomUser.objects.get(pk=obj.pk)
                if obj.password != orig_obj.password:
                    obj.set_password(obj.password)
                obj.save()
                if team_name and team_country:
                    team = obj.team
                    team.name = team_name
                    team.country = team_country
                    team.save()


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

# Customize Player admin page

class PlayerAdmin(admin.ModelAdmin):
    def team(self, obj):
        return obj.team.name
    team.short_description = 'Team Name'

    list_display = ('first_name', 'last_name', 'team', 'position', 'listing_status')
    search_fields = ("first_name", 'position',)
    list_filter = ('team__name', 'listing_status',)

# Customize Player Transfer admin page
    
class TransferListAdmin(admin.ModelAdmin):
    def player_name(self, obj):
        return f'{obj.player.first_name} {obj.player.last_name}'
    player_name.short_description = 'Player Name'

    def team_name(self, obj):
        return obj.player.team.name
    team_name.short_description = 'Team Name'

    def position(self, obj):
        return obj.player.position
    position.short_description = 'Position'

    def country(self, obj):
        return obj.player.country
    country.short_description = 'Country'

    def price(self, obj):
        return f'$ {obj.asking_price}'
    price.short_description = 'Asking Price'

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        MarketList.objects.create(transfer_list=obj)

    '''
    To delete single player from transfer list and change 
    its listing status from "Listed" to "Not Listed"
    '''

    def delete_model(self, request, obj):
        player = obj.player
        player.listing_status = 'Not Listed'
        player.save()
        super().delete_model(request, obj)

    '''
    To delete multiple players from transfer list at once
    and change their listing status from "Listed" to "Not Listed"
    '''

    def delete_queryset(self, request, queryset):
        for obj in queryset:
            player = obj.player
            player.listing_status = 'Not Listed'
            player.save()
        super().delete_queryset(request, queryset)

    list_display = ('player_name', 'team_name', 'position', 'country', 'price')
    list_filter = ('player__team__name',)

# Customize Market List admin Page
    
class MarketListAdmin(admin.ModelAdmin):
    def player_name(self, obj):
        return f'{obj.transfer_list.player.first_name} {obj.transfer_list.player.last_name}'
    player_name.short_description = 'Player Name'

    def team_name(self, obj):
        return obj.transfer_list.player.team.name
    team_name.short_description = 'Team Name'

    def position(self, obj):
        return obj.transfer_list.player.position
    position.short_description = "Position"

    def country(self, obj):
        return obj.transfer_list.player.country
    country.short_description = 'Country'

    def price(self, obj):
        return f'$ {obj.transfer_list.asking_price}'
    price.short_description = 'Asking Price'

    list_display = ('player_name', 'team_name', 'position','country', 'price')

    '''
    Using the CountryFilter class from .helper to 
    show only countries of listed players
    '''
    
    list_filter = ('transfer_list__player__team__name', CountryFilter)  

