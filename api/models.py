from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
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
        extra_fields.setdefault('username', 'admin')
        extra_fields.setdefault('name', 'Admin')
        return self.create_user(email, password, **extra_fields)

# To generate random countries for a team when user user signup

COUNTRIES = [country.name for country in pycountry.countries]

class CustomUser(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=15, null=True) 
    name = models.CharField(max_length=20, null=True)
    email = models.EmailField(verbose_name="email address", unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    objects = CustomUserManager()
    USERNAME_FIELD = 'email' 

# Create Team model
    
class Team(models.Model):
    name = models.CharField(max_length=100)
    country = models.CharField(max_length=70, choices=[(country, country) for country in COUNTRIES])
    budget = models.DecimalField(max_digits=10, decimal_places=2, default=5000000)
    owner = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='team')

    def __str__(self):
        return self.name

    @property
    def team_value(self):
        return sum(player.market_value for player in self.players.all())

    @property
    def final_value(self):
        return self.team_value + self.budget

# Create Player Model
    
class Player(models.Model):
    POSITIONS = [
        ('Goalkeeper', 'Goalkeeper'),
        ('Defender', 'Defender'),
        ('Midfielder', 'Midfielder'),
        ('Attacker', 'Attacker'),
    ]
    LISTING_STATUS_CHOICES = [
        ('Not Listed', 'Not Listed'),
        ('Listed', 'Listed'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    country = models.CharField(max_length=70, choices=[(country, country) for country in COUNTRIES])
    age = models.PositiveIntegerField()
    market_value = models.DecimalField(max_digits=10, decimal_places=2, default=1000000)
    position = models.CharField(max_length=20, choices=POSITIONS)
    listing_status = models.CharField(max_length=20, choices=LISTING_STATUS_CHOICES, default='Not Listed')
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='players') 

    def __str__(self):
        return self.first_name + " " + self.last_name
    
# Player Transfer List Create

class TransferList(models.Model):
    player = models.OneToOneField(Player, on_delete=models.CASCADE)
    asking_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.player.first_name} {self.player.last_name}"

    def team_name(self):
        return self.player.team.name

    def save(self, *args, **kwargs):
        self.player.listing_status = 'Listed'
        self.player.save()
        super().save(*args, **kwargs)

# Market List

class MarketList(models.Model):
    transfer_list = models.OneToOneField(TransferList, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        self.country = self.transfer_list.player.country
        self.transfer_list.player.listing_status = 'Listed'
        self.transfer_list.player.save()
        super().save(*args, **kwargs)
