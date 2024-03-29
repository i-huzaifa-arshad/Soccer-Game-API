from rest_framework import serializers
from .models import CustomUser, Team, Player, TransferList, MarketList
import pycountry
from .helper import (
    user_register_create_team_and_players,
    get_player_name_and_price,
    show_market_list_data,
)

# User Register Serializer


class UserRegisterSerializer(serializers.ModelSerializer):
    team_name = serializers.CharField(write_only=True)
    team_country = serializers.ChoiceField(
        choices=[(country.name, country.name) for country in pycountry.countries],
        write_only=True,
    )
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ["username", "name", "email", "password", "team_name", "team_country"]

    def create(self, validated_data):
        team_name = validated_data.pop("team_name")
        team_country = validated_data.pop("team_country")
        user = super().create(validated_data)
        user.set_password(validated_data["password"])
        user.save()
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
        fields = ["username", "name"]


# User Update Serializer


class UserUpdateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = CustomUser
        fields = ["username", "name", "password"]

    def update(self, instance, validated_data):
        if "password" in validated_data:
            password = validated_data.pop("password")
            instance.set_password(password)
        return super().update(instance, validated_data)


# Player Details Serializer


class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = [
            "id",
            "first_name",
            "last_name",
            "country",
            "age",
            "market_value",
            "position",
            "listing_status",
        ]


# Player Update Serializer


class PlayerUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = ["first_name", "last_name", "country"]


# Team Details Serializer


class TeamSerializer(serializers.ModelSerializer):
    players = PlayerSerializer(many=True, read_only=True)
    team_value = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )
    final_value = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )

    class Meta:
        model = Team
        fields = ["name", "country", "budget", "team_value", "final_value", "players"]


# Team Update Serializer


class TeamUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ["name", "country"]


# User Details View Serializer


class UserDetailSerializer(serializers.ModelSerializer):
    team = TeamSerializer(read_only=True)

    class Meta:
        model = CustomUser
        fields = ["username", "name", "team"]


# Transfer List Create Serializer


class TransferListSerializer(serializers.ModelSerializer):
    player_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = TransferList
        fields = ["player_id", "asking_price"]

    def validate_player_id(self, value):
        try:
            player = Player.objects.get(id=value)
            return player
        except Player.DoesNotExist:
            raise serializers.ValidationError(
                "Player with this ID does not exist in the team!"
            )

    def create(self, validated_data):
        player = validated_data.pop("player_id")
        transfer_list = TransferList.objects.create(player=player, **validated_data)
        return transfer_list

    def to_representation(self, instance):
        return get_player_name_and_price(instance)


# Market List


class MarketListSerializer(serializers.ModelSerializer):
    player_id = serializers.SerializerMethodField()
    player_name = serializers.SerializerMethodField()
    player_country = serializers.SerializerMethodField()
    team_name = serializers.SerializerMethodField()
    position = serializers.SerializerMethodField()
    asking_price = serializers.SerializerMethodField()

    class Meta:
        model = MarketList
        fields = [
            "player_id",
            "player_name",
            "player_country",
            "team_name",
            "position",
            "asking_price",
        ]

    def to_representation(self, instance):
        return show_market_list_data(instance)


# Player Buy


class BuyPlayerSerializer(serializers.Serializer):
    player_id = serializers.UUIDField()
    price = serializers.DecimalField(max_digits=10, decimal_places=2)

    def validate_player_id(self, value):
        try:
            player = Player.objects.get(id=value)
        except Player.DoesNotExist:
            raise serializers.ValidationError("Player does not exist")
        return value
