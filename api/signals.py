from django.db.models.signals import pre_delete, post_delete
from django.dispatch import receiver
from .models import *


# For Team Model

"""
To delete all players when User or Team is deleted via 
admin panel or user is deleted from url.
"""

@receiver(pre_delete, sender=Team)
def delete_players(sender, instance, **kwargs):
    instance.players.all().delete()

# For Market List Model
    
"""
To delete players from Market list from admin panel
will automatically remove them from transfer list as
well and change listing status back to Not Listed
"""
        
@receiver(post_delete, sender=MarketList)
def delete_players(sender, instance, **kwargs):
    player = instance.transfer_list.player
    player.listing_status = 'Not Listed'
    player.save()
    instance.transfer_list.delete()