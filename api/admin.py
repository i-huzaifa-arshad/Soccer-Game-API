from django.contrib import admin
from .models import *
from .customadmin import * 

# Register models
    
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Team, TeamAdmin)
admin.site.register(Player, PlayerAdmin)
admin.site.register(TransferList, TransferListAdmin)
admin.site.register(MarketList, MarketListAdmin)
