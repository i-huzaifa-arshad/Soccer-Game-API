from rest_framework import generics, status, filters
from .models import (CustomUser, Team, Player,
                     TransferList, MarketList)
from .serializers import (UserRegisterSerializer, UserLoginSerializer,
                          TeamSerializer, UserListSerializer,
                          UserDetailSerializer, UserUpdateSerializer,
                          TeamUpdateSerializer, PlayerUpdateSerializer,
                          TransferListSerializer, MarketListSerializer,
                          BuyPlayerSerializer)
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from django.db import IntegrityError
from .helper import buy_player

# User Register

class UserRegisterView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserRegisterSerializer

    def perform_create(self, serializer):
        user = serializer.save()
        team = user.team

# User Login

class UserLoginView(generics.GenericAPIView):
    serializer_class = UserLoginSerializer

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        user = authenticate(email=email, password=password)
        if user is not None:
            token = Token.objects.filter(user=user)
            if token.exists():
                return Response({
                    'message': f'User *{user.username}* already logged in.'
                }, status=status.HTTP_400_BAD_REQUEST)
            else:
                token = Token.objects.create(user=user)
                team = user.team
                team_data = TeamSerializer(team).data
                return Response({
                    'message': f'Welcome *{user.name}* to the Soccer Online Game Manager Console. Your team details are as follows:',
                    'token': token.key,
                    'team': team_data
                })
        else:
            return Response({
                'error': 'Invalid Credentials'
            }, status=status.HTTP_400_BAD_REQUEST)

# User Logout

class UserLogoutView(generics.DestroyAPIView):
    queryset = CustomUser.objects.all()
    lookup_field = 'username'

    def destroy(self, request, *args, **kwargs):
        user = self.get_object()
        username = user.username
        token = Token.objects.filter(user=user)
        if token.exists():
            token.delete()
            return Response({
                'message': f'User *{username}* Logged out successfully.'
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'message': f'User *{username}* not logged in.'
            }, status=status.HTTP_400_BAD_REQUEST)

# User List

class UserListView(generics.ListAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserListSerializer

# User Details

class UserDetailView(generics.RetrieveAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserDetailSerializer
    lookup_field = 'username'

    def authenticate_user(self, request, *args, **kwargs):
        user = self.get_object()
        token = Token.objects.filter(user=user)
        if token.exists():
            return True
        else:
            return False

    def get(self, request, *args, **kwargs):
        if not self.authenticate_user(request, *args, **kwargs):
            username = self.kwargs['username']
            return Response({
                'message': f'User *{username}* not logged in. Please login first.'
            }, status=status.HTTP_400_BAD_REQUEST)
        return super().get(request, *args, **kwargs)

# User Update

class UserUpdateView(generics.UpdateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserUpdateSerializer
    lookup_field = 'username'

    def authenticate_user(self, request, *args, **kwargs):
        user = self.get_object()
        token = Token.objects.filter(user=user)
        if token.exists():
            return True
        else:
            return False

    def update(self, request, *args, **kwargs):
        if not self.authenticate_user(request, *args, **kwargs):
            username = self.kwargs['username']
            return Response({
                'message': f'User *{username}* not logged in. Please login first.'
            }, status=status.HTTP_400_BAD_REQUEST)
        return super().update(request, *args, **kwargs)

# User Delete

class UserDeleteView(generics.DestroyAPIView):
    queryset = CustomUser.objects.all()
    lookup_field = 'username'

    def authenticate_user(self, request, *args, **kwargs):
        user = self.get_object()
        token = Token.objects.filter(user=user)
        if token.exists():
            return True
        else:
            return False

    def destroy(self, request, *args, **kwargs):
        if not self.authenticate_user(request, *args, **kwargs):
            username = self.kwargs['username']
            return Response({
                'message': f'User *{username}* not logged in. Please login first.'
            }, status=status.HTTP_400_BAD_REQUEST)
        user = self.get_object()
        username = user.username
        user.delete()
        return Response({
            'message': f'User *{username}* deleted successfully! All team data is deleted.'
        }, status=status.HTTP_204_NO_CONTENT)

# Team Update

class TeamUpdateView(generics.UpdateAPIView):
    queryset = Team.objects.all()
    serializer_class = TeamUpdateSerializer
    lookup_field = 'owner__username'

    def authenticate_user(self, request, *args, **kwargs):
        team = self.get_object()
        user = team.owner
        token = Token.objects.filter(user=user)
        if token.exists():
            return True
        else:
            return False

    def update(self, request, *args, **kwargs):
        if not self.authenticate_user(request, *args, **kwargs):
            username = self.kwargs['owner__username']
            return Response({
                'message': f'User *{username}* not logged in. Please login first.'
            }, status=status.HTTP_400_BAD_REQUEST)
        return super().update(request, *args, **kwargs)

# Player Update

class PlayerUpdateView(generics.UpdateAPIView):
    queryset = Player.objects.all()
    serializer_class = PlayerUpdateSerializer
    lookup_field = 'id'

    def authenticate_user(self, request, *args, **kwargs):
        teamname = self.kwargs['teamname']
        team = Team.objects.get(name=teamname)
        user = team.owner
        token = Token.objects.filter(user=user)
        if token.exists():
            return True, user
        else:
            return False, user

    def update(self, request, *args, **kwargs):
        is_authenticated, user = self.authenticate_user(request, *args, **kwargs)
        if not is_authenticated:
            teamname = self.kwargs['teamname']
            username = user.username
            return Response({
                'message': f'Owner *{username}* of the Team *{teamname}* not logged in. Please login first to update this player record.'
            }, status=status.HTTP_400_BAD_REQUEST)
        return super().update(request, *args, **kwargs)

# Player Transfer List Create

class TransferListView(generics.ListCreateAPIView):
    serializer_class = TransferListSerializer

    def get_user(self):
        return CustomUser.objects.get(username=self.kwargs['username'])

    def get_team(self):
        return Team.objects.get(owner=self.get_user())

    def get_queryset(self):
        team = self.get_team()
        return TransferList.objects.filter(player__in=team.players.all())

    def authenticate_user(self):
        return Token.objects.filter(user=self.get_user()).exists()

    def get_serializer(self, *args, **kwargs):
        kwargs['context'] = self.get_serializer_context()
        kwargs['context'].update({"players": self.get_team().players.all()})
        return self.serializer_class(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        if not self.authenticate_user():
            return Response({
                'message': f'User *{self.get_user().username}* not logged in. Please login first to add players to transfer list.'
            }, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            transfer_list_entry = serializer.save()
            MarketList.objects.create(transfer_list=transfer_list_entry)
        except IntegrityError:
            player = serializer.validated_data['player']
            return Response({
                'Warning': f'Player *{player.first_name} {player.last_name}* already listed in the transfer list.'
            }, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=self.get_success_headers(serializer.data))

# Market List View

class MarketListView(generics.ListAPIView):
    serializer_class = MarketListSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = [
        'transfer_list__player__first_name', 'transfer_list__player__last_name',
        'transfer_list__player__country', 'transfer_list__player__team__name',
        'transfer_list__asking_price']

    def get_queryset(self):
        return MarketList.objects.all()

# Player Buy View

class BuyPlayerView(generics.CreateAPIView):
    serializer_class = BuyPlayerSerializer

    def get_serializer(self, *args, **kwargs):
        kwargs['context'] = self.get_serializer_context()
        return self.serializer_class(*args, **kwargs)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context

    def authenticate_user(self):
        user = CustomUser.objects.get(username=self.kwargs['username'])
        token = Token.objects.filter(user=user)
        if token.exists():
            return True
        else:
            return False

    def post(self, request, *args, **kwargs):
        if not self.authenticate_user():
            username = self.kwargs['username']
            return Response({
                'message': f'User *{username}* not logged in. Please login first to buy a player.'
            }, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        response = buy_player(serializer, self.kwargs['username'])
        return response
