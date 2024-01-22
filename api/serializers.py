from rest_framework import serializers
from .models import *
import pycountry
import random
from faker import Faker

fake = Faker()

# User Register

class UserRegisterSerializer(serializers.ModelSerializer):
    team_name = serializers.CharField(write_only=True)
    team_country = serializers.ChoiceField(choices=[(country.name, country.name) for country in pycountry.countries], write_only=True)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['username', 'name', 'email', 'password', 'team_name', 'team_country'] 

    def create(self, validated_data):
        team_name = validated_data.pop('team_name')
        team_country = validated_data.pop('team_country')
        user = super().create(validated_data)
        user.set_password(validated_data['password'])
        user.save()
        team = Team.objects.create(owner=user, name=team_name, country=team_country)

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
        return user
    
# User Login
    
class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

# User List
    
class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['username', 'name', 'email'] 

# User Update
    
class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['username', 'name'] 
        
# Player Details

class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = ['id', 'first_name', 'last_name', 'country', 'age', 'market_value', 'position']

# Player Update
        
class PlayerUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = ['first_name', 'last_name', 'country']

# Team Details
        
class TeamSerializer(serializers.ModelSerializer):
    players = PlayerSerializer(many=True, read_only=True)
    team_value = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    final_value = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Team
        fields = ['name', 'country', 'budget', 'team_value', 'final_value', 'players']

# Team Update
        
class TeamUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ['name', 'country']

# User Team Details View

class UserTeamDetailSerializer(serializers.ModelSerializer):
    team = TeamSerializer(read_only=True)
    welcome_message = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ['welcome_message', 'team']
    
    def get_welcome_message(self, obj):
        return f'Welcome {obj.name} to the Soccer Game Console. Here is your Team {obj.team.name} details'

"""Test String"""

"""Test String 2"""