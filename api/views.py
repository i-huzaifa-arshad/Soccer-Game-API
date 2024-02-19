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
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from django.db import IntegrityError
from .helper import CheckTokenUserMatch, buy_player


# User Register


class UserRegisterView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserRegisterSerializer


# User Login


class UserLoginView(generics.GenericAPIView):
    serializer_class = UserLoginSerializer

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
        user = authenticate(email=email, password=password)
        if user is not None:
            token, created = Token.objects.get_or_create(user=user)
            if not created:
                return Response(
                    {"message": f"User *{user.username}* already logged in."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            else:
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


class UserLogoutView(generics.DestroyAPIView):
    queryset = CustomUser.objects.all()
    lookup_field = "username"
    permission_classes = [IsAuthenticated, CheckTokenUserMatch]
    authentication_classes = [TokenAuthentication]

    def destroy(self, request, *args, **kwargs):
        user = self.get_object()
        username = user.username
        token = Token.objects.filter(user=user)
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


class UserDetailView(generics.RetrieveAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserDetailSerializer
    lookup_field = "username"
    permission_classes = [IsAuthenticated, CheckTokenUserMatch]
    authentication_classes = [TokenAuthentication]


# User Update


class UserUpdateView(generics.UpdateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserUpdateSerializer
    lookup_field = "username"
    permission_classes = [IsAuthenticated, CheckTokenUserMatch]
    authentication_classes = [TokenAuthentication]


# User Delete


class UserDeleteView(generics.DestroyAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserUpdateSerializer
    lookup_field = "username"
    permission_classes = [IsAuthenticated, CheckTokenUserMatch]
    authentication_classes = [TokenAuthentication]

    def destroy(self, request, *args, **kwargs):
        user = self.get_object()
        self.perform_destroy(user)
        return Response(
            {
                f"Successfully deleted all team and player data for the user *{user.username}*."
            },
            status=status.HTTP_204_NO_CONTENT,
        )


# Team Update


class TeamUpdateView(generics.UpdateAPIView):
    queryset = Team.objects.all()
    serializer_class = TeamUpdateSerializer
    lookup_field = "owner__username"
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]


# Player Update


class PlayerUpdateView(generics.UpdateAPIView):
    queryset = Player.objects.all()
    serializer_class = PlayerUpdateSerializer
    lookup_field = "id"
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]


# Player Transfer List Create


class TransferListView(generics.ListCreateAPIView):
    queryset = TransferList.objects.all()
    serializer_class = TransferListSerializer
    permission_classes = [IsAuthenticated, CheckTokenUserMatch]
    authentication_classes = [TokenAuthentication]

    def post(self, request, *args, **kwargs):
        username = self.kwargs["username"]
        user = CustomUser.objects.get(username=username)
        team = Team.objects.get(owner=user)
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        player = serializer.validated_data["player_id"]
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
        "transfer_list__player__id",
        "transfer_list__player__first_name",
        "transfer_list__player__last_name",
        "transfer_list__player__country",
        "transfer_list__player__team__name",
        "transfer_list__player__position",
        "transfer_list__asking_price",
    ]

    def get_queryset(self):
        return MarketList.objects.all()


# Player Buy View


class BuyPlayerView(generics.CreateAPIView):
    serializer_class = BuyPlayerSerializer
    permission_classes = [IsAuthenticated, CheckTokenUserMatch]
    authentication_classes = [TokenAuthentication]

    def post(self, request, *args, **kwargs):
        username = self.kwargs["username"]
        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        player = Player.objects.get(id=serializer.validated_data["player_id"])
        if player.team.owner.username == username:
            return Response(
                {"message": "You can't buy your own team player."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        response = buy_player(serializer, username)
        return response
