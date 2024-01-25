from django.contrib import admin
from .models import *
from .customadmin import * 

# Register models
    
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Player, PlayerAdmin)
admin.site.register(Team, TeamAdmin)
admin.site.register(TransferList, TransferListAdmin)
admin.site.register(MarketList, MarketListAdmin)
# admin.site.register(BuyList)

"""
Admin panel needs modifications. I can currently change the Player country only, and
it will be reflected everywhere. But I can't change the other data like listing_status.
It will change it if I see localhost:8000/user_details/#username, but this change won't
be reflected in Admin panel Transfer List and Market List.
"""