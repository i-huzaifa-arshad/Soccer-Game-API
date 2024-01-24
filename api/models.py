from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch import receiver
import pycountry
import uuid


# For making a custom user instead of using django's built-in user

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field is required...')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

# To generate random countries for a team when user user signup

COUNTRIES = [country.name for country in pycountry.countries]

class CustomUser(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=15, null=True) 
    name = models.CharField(max_length=20, null=True)
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    objects = CustomUserManager()

    # Adding Team Name and Country for user signup from admin panel

    team_name = models.CharField(max_length=100, null=True, blank=True)
    team_country = models.CharField(max_length=70, choices=[(country.name, country.name) for country in pycountry.countries], null=True, blank=True)

    USERNAME_FIELD = 'email' 
    
    # To delete all teams associated with this user

    def delete(self, *args, **kwargs):
        if hasattr(self, 'team'):
            self.team.delete()  
        super().delete(*args, **kwargs)
    
# Create Player Model
         
class Player(models.Model):

    POSITION_CHOICES = [
        ('Goalkeeper', 'Goalkeeper'),
        ('Defender', 'Defender'),
        ('Midfielder', 'Midfielder'),
        ('Attacker', 'Attacker'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    country = models.CharField(max_length=80, choices=[(country, country) for country in COUNTRIES])
    age = models.IntegerField()
    market_value = models.DecimalField(max_digits=10, decimal_places=2, default=1000000)

    position = models.CharField(max_length=15, choices=POSITION_CHOICES)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'
    
    # To update player country from admin panel
    def save(self, *args, **kwargs):
        # If the player exists and the country has changed
        if self.pk:
            try:
                old_player = Player.objects.get(pk=self.pk)
                if old_player.country != self.country:
                    # Update the player in the TransferList and MarketList models
                    TransferList.objects.filter(player=self).update(player=self)
                    MarketList.objects.filter(transfer_list__player=self).update(country=self.country)
            except Player.DoesNotExist:
                pass
        super().save(*args, **kwargs)

# Create Team model
    
class Team(models.Model):
    name = models.CharField(max_length=100)
    country = models.CharField(max_length=70, choices=[(country, country) for country in COUNTRIES])
    budget = models.DecimalField(max_digits=10, decimal_places=2, default=5000000)
    owner = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    players = models.ManyToManyField(Player)

    def __str__(self):
        return self.name
    
    @property
    def team_value(self):
        return sum(player.market_value for player in self.players.all())

    @property
    def final_value(self):
        return self.team_value + self.budget
    
"""
To delete all players when User or Team is deleted via 
admin panel or user is deleted from url.
"""
    
@receiver(pre_delete, sender=Team)
def delete_players(sender, instance, **kwargs):
    instance.players.all().delete()

# Player Transfer List Create
    
class TransferList(models.Model):
    player = models.OneToOneField(Player, on_delete=models.CASCADE)
    asking_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.player.first_name} {self.player.last_name}"

    def team_name(self):
        team = self.player.team_set.first()
        return team.name if team else None

# Market List
    
class MarketList(models.Model):
    transfer_list = models.OneToOneField(TransferList, on_delete=models.CASCADE)
    country = models.CharField(max_length = 255)

    def save(self, *args, **kwargs):
        self.country = self.transfer_list.player.country
        super().save(*args, **kwargs)

