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
        fields = ['username', 'name'] 

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

# User Details View

class UserDetailSerializer(serializers.ModelSerializer):
    team = TeamSerializer(read_only=True)

    class Meta:
        model = CustomUser
        fields = ['username', 'name', 'team']
   

# Transfer List Create

class TransferListSerializer(serializers.ModelSerializer):
    player = serializers.PrimaryKeyRelatedField(queryset=Player.objects.none())

    class Meta:
        model = TransferList
        fields = ['player', 'asking_price']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'context' in kwargs and 'players' in kwargs['context']:
            self.fields['player'].queryset = kwargs['context']['players']

    # Customization for showing full name of player
        
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['player'] = instance.player.first_name + ' ' + instance.player.last_name
        return data


# Market List

class MarketListSerializer(serializers.ModelSerializer):
    player_name = serializers.SerializerMethodField()
    player_country = serializers.CharField(source='transfer_list.player.country')
    team_name = serializers.SerializerMethodField()
    asking_price = serializers.DecimalField(source='transfer_list.asking_price', max_digits=10, decimal_places=2)

    class Meta:
        model = MarketList
        fields = ['player_name', 'player_country', 'team_name', 'asking_price']

    def get_player_name(self, obj):
        return f'{obj.transfer_list.player.first_name} {obj.transfer_list.player.last_name}'
        
    def get_team_name(self, obj):
        return obj.transfer_list.player.team_set.first().name if obj.transfer_list.player.team_set.exists() else None
