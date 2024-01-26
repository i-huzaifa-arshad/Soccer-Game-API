from django.db.models.signals import pre_delete, post_delete, pre_save, post_save
from django.dispatch import receiver
from .models import *


# For Custom User Model

"""
To delete all teams associated with the user 
when he is deleted from admin panel or url
"""

@receiver(pre_delete, sender=CustomUser)
def delete_associated_team(sender, instance, **kwargs):
    if hasattr(instance, 'team'):
        instance.team.delete()

# For Player Model

''' 
To update player country from admin panel and 
reflect this change to all places
'''

@receiver(pre_save, sender=Player)
def update_player_country(sender, instance, **kwargs):
    if instance.pk: 
        try:
            old_player = Player.objects.get(pk=instance.pk)
            if old_player.country != instance.country:
                TransferList.objects.filter(player=old_player).update(player=instance)
                MarketList.objects.filter(transfer_list__player=old_player).update(country=instance.country)
        except Player.DoesNotExist:
            pass

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

