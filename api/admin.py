from django.contrib import admin
from django.contrib.auth.models import Group
from .models import (CustomUser, Team, Player,
                     TransferList, MarketList)
from .customadmin import (CustomUserAdmin, TeamAdmin,
                          PlayerAdmin, TransferListAdmin,
                          MarketListAdmin)

# Register models

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Team, TeamAdmin)
admin.site.register(Player, PlayerAdmin)
admin.site.register(TransferList, TransferListAdmin)
admin.site.register(MarketList, MarketListAdmin)

# Unregister Groups

admin.site.unregister(Group)
