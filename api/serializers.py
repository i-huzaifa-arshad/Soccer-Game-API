from rest_framework import serializers
from .models import *
from .helper_functions import *

# User Register Serializer

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
        """
        Calling helper function so system can automatically
        create player data when user signup from the url
        """
        user_register_create_team_and_players(user, team_name, team_country)
        return user

# User Login Serializer
    
class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

# User List Serializer
    
class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['username', 'name'] 

# User Update Serializer
    
class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['username', 'name'] 
        
# Player Details Serializer

class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = ['id', 'first_name', 'last_name', 'country', 'age', 'market_value', 'position', 'listing_status']

# Player Update Serializer
        
class PlayerUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = ['first_name', 'last_name', 'country']

# Team Details Serializer
        
class TeamSerializer(serializers.ModelSerializer):
    players = PlayerSerializer(many=True, read_only=True)
    team_value = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    final_value = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Team
        fields = ['name', 'country', 'budget', 'team_value', 'final_value', 'players']

# Team Update Serializer
        
class TeamUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ['name', 'country']

# User Details View Serializer

class UserDetailSerializer(serializers.ModelSerializer):
    team = TeamSerializer(read_only=True)

    class Meta:
        model = CustomUser
        fields = ['username', 'name', 'team']
   

# Transfer List Create Serializer

class TransferListSerializer(serializers.ModelSerializer):
    player = serializers.PrimaryKeyRelatedField(queryset=Player.objects.none())

    class Meta:
        model = TransferList
        fields = ['player', 'asking_price']
    # try to remove this init  but get same functionality. make helper function
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'context' in kwargs and 'players' in kwargs['context']:
            self.fields['player'].queryset = kwargs['context']['players']

    """
    Calling helper function to show the player full name 
    instead of ID, when a user list player to Transfer List
    for selling from the URL
    """

    def to_representation(self, instance):
        return transfer_list_name_instead_of_id(instance)

# Market List

class MarketListSerializer(serializers.ModelSerializer):
    player_name = serializers.SerializerMethodField()
    player_country = serializers.SerializerMethodField()
    team_name = serializers.SerializerMethodField()
    asking_price = serializers.SerializerMethodField()

    class Meta:
        model = MarketList
        fields = ['player_name', 'player_country', 'team_name', 'asking_price']
    
    """
    Calling helper function to show player details when 
    user visits the Market List from URL
    """

    def to_representation(self, instance):
        return market_list_serializer_helper(instance)

# Player Buy

class BuyPlayerSerializer(serializers.Serializer):
    player = serializers.PrimaryKeyRelatedField(queryset=Player.objects.none())
    price = serializers.DecimalField(max_digits=10, decimal_places=2)
    
    def get_player_queryset(self):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            username = request.user.username
            user = CustomUser.objects.get(username=username)
            try:
                user_team = Team.objects.get(owner=user)
                return Player.objects.filter(listing_status='Listed').exclude(team__owner=user).exclude(team=user_team)
            except Team.DoesNotExist:
                return Player.objects.filter(listing_status='Listed').exclude(team__owner=user)
        return Player.objects.none()


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['player'].queryset = self.get_player_queryset()


"""
The current code works. The only issue is it also showing the 
current logged in user team players in Player field. It need to
be fixed. 

Also, from admin panel, the admin can add player but it can't assign
team name to it. Add this functionality.
"""
