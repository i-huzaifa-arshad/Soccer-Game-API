from rest_framework import generics, status, filters
from .models import CustomUser, Team, Player, TransferList, MarketList
from .serializers import (
    UserRegisterSerializer,
    UserLoginSerializer,
    TeamSerializer,
    UserListSerializer,
    UserDetailSerializer,
    UserUpdateSerializer,
    TeamUpdateSerializer,
    PlayerUpdateSerializer,
    TransferListSerializer,
    MarketListSerializer,
    BuyPlayerSerializer,
)
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import NotAuthenticated, ValidationError
from django.contrib.auth import authenticate
from rest_framework.response import Response
from django.db import IntegrityError
from .helper import UserAuthentication, buy_player

# User Register


class UserRegisterView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserRegisterSerializer


# User Login


class UserLoginView(UserAuthentication, generics.GenericAPIView):
    serializer_class = UserLoginSerializer

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
        user = authenticate(email=email, password=password)
        if user is not None:
            try:
                self.check_user_already_logged_in(user.username)
            except ValidationError as e:
                return Response(
                    {"message": str(e.detail[0])},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            token = Token.objects.create(user=user)
            team = user.team
            team_data = TeamSerializer(team).data
            return Response(
                {
                    "message": f"Welcome *{user.name}* to the Soccer Online Game Manager Console. Your team details are as follows:",
                    "token": token.key,
                    "team": team_data,
                }
            )
        else:
            return Response(
                {"error": "Invalid Credentials"}, status=status.HTTP_400_BAD_REQUEST
            )


# User Logout


class UserLogoutView(UserAuthentication, generics.DestroyAPIView):

    def delete(self, *args, **kwargs):
        username = self.kwargs.get("username")
        try:
            _, token = self.check_user_not_logged_in(username)
        except NotAuthenticated as e:
            return Response(
                {"message": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if token.exists():
            token.delete()
            return Response(
                {"message": f"User *{username}* Logged out successfully."},
                status=status.HTTP_200_OK,
            )


# User List


class UserListView(generics.ListAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserListSerializer


# User Details


class UserDetailView(UserAuthentication, generics.RetrieveAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserDetailSerializer
    lookup_field = "username"

    def get(self, *args, **kwargs):
        username = self.kwargs.get("username")
        try:
            self.check_user_not_logged_in(username)
        except NotAuthenticated as e:
            return Response(
                {"message": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return super().get(*args, **kwargs)


# User Update


class UserUpdateView(UserAuthentication, generics.UpdateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserUpdateSerializer
    lookup_field = "username"

    def update(self, *args, **kwargs):
        username = self.kwargs.get("username")
        try:
            self.check_user_not_logged_in(username)
        except NotAuthenticated as e:
            return Response(
                {"message": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return super().update(*args, **kwargs)


# User Delete


class UserDeleteView(UserAuthentication, generics.DestroyAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserUpdateSerializer
    lookup_field = "username"

    def destroy(self, request, username=None):
        username = self.kwargs.get("username")
        try:
            self.check_user_not_logged_in(username)
        except NotAuthenticated as e:
            return Response(
                {"message": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user = self.get_object()
        user.delete()
        return Response(
            {
                "message": f"User *{username}* deleted successfully! All team data is deleted."
            },
            status=status.HTTP_204_NO_CONTENT,
        )


# Team Update


class TeamUpdateView(UserAuthentication, generics.UpdateAPIView):
    queryset = Team.objects.all()
    serializer_class = TeamUpdateSerializer
    lookup_field = "owner__username"

    def update(self, request, username=None, *args, **kwargs):
        username = self.kwargs.get("owner__username")
        try:
            self.check_user_not_logged_in(username)
        except NotAuthenticated as e:
            return Response(
                {"message": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return super().update(request, *args, **kwargs)


# Player Update


class PlayerUpdateView(UserAuthentication, generics.UpdateAPIView):
    queryset = Player.objects.all()
    serializer_class = PlayerUpdateSerializer
    lookup_field = "id"

    def update(self, *args, **kwargs):
        teamname = self.kwargs.get("teamname")
        team = Team.objects.get(name=teamname)
        user = team.owner
        try:
            self.check_user_not_logged_in(user.username)
        except NotAuthenticated as e:
            return Response(
                {"message": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return super().update(*args, **kwargs)


# Player Transfer List Create


class TransferListView(UserAuthentication, generics.ListCreateAPIView):
    serializer_class = TransferListSerializer

    def get_user(self):
        return CustomUser.objects.get(username=self.kwargs["username"])

    def get_team(self):
        return Team.objects.get(owner=self.get_user())

    def get_queryset(self):
        team = self.get_team()
        return TransferList.objects.filter(player__in=team.players.all())

    def post(self, request, *args, **kwargs):
        username = self.kwargs["username"]
        try:
            self.check_user_not_logged_in(username)
        except NotAuthenticated as e:
            return Response(
                {"message": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        player = serializer.validated_data["player_id"]
        team = self.get_team()
        if not team.players.filter(id=player.id).exists():
            return Response(
                {"error": "Player does not exist in the team"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            transfer_list_entry = serializer.save()
            MarketList.objects.create(transfer_list=transfer_list_entry)
        except IntegrityError:
            return Response(
                {
                    "Warning": f"Player *{player.first_name} {player.last_name}* already listed in the transfer list."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
        )


# Market List View


class MarketListView(generics.ListAPIView):
    serializer_class = MarketListSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = [
        "transfer_list__player__first_name",
        "transfer_list__player__last_name",
        "transfer_list__player__country",
        "transfer_list__player__team__name",
        "transfer_list__asking_price",
    ]

    def get_queryset(self):
        return MarketList.objects.all()


# Player Buy View


class BuyPlayerView(UserAuthentication, generics.CreateAPIView):
    serializer_class = BuyPlayerSerializer

    def get_serializer(self, *args, **kwargs):
        kwargs["context"] = self.get_serializer_context()
        return self.serializer_class(*args, **kwargs)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context

    def post(self, request, *args, **kwargs):
        username = self.kwargs["username"]
        try:
            self.check_user_not_logged_in(username)
        except NotAuthenticated as e:
            return Response(
                {"message": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        player = Player.objects.get(id=serializer.validated_data["player_id"])
        if player.team.owner.username == username:
            return Response(
                {"message": "You can't buy your own team player."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        response = buy_player(serializer, username)
        return response
