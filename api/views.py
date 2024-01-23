from django.contrib.auth import authenticate
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from .models import *
from .serializers import *


# User Register

class UserRegisterView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserRegisterSerializer

    def perform_create(self, serializer):
        user = serializer.save()
        team = Team.objects.get

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
                return Response({'message': f'User *{user.username}* already logged in.'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                token = Token.objects.create(user=user)
                team = Team.objects.get(owner=user)
                team_data = TeamSerializer(team).data
                return Response({
                    'message': f'Welcome *{user.name}* to the Soccer Online Game Manager Console. Your team details are as follows:',
                    'team': team_data
                   # 'token': token.key # Hiding the token for now
                })
        else:
            return Response({'error': 'Invalid Credentials'}, status=status.HTTP_400_BAD_REQUEST)

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
            return Response({'message': f'User *{username}* Logged out successfully.'}, status=status.HTTP_200_OK)
        else:
            return Response({'message': f'User *{username}* not logged in.'}, status=status.HTTP_400_BAD_REQUEST)

# User List
        
class UserListView(generics.ListAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserListSerializer

# User Details
    
class UserDetailView(generics.RetrieveAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserDetailSerializer
    lookup_field = 'username'

    ''' Check if user is logged in or not. If logged in,
        proceed. Else, ask user to login first.
    '''

    def authenticate_user(self, request, *args, **kwargs):
        user = self.get_object()
        username = user.username
        token = Token.objects.filter(user=user)
        if token.exists():
            return True
        else:
            return False
        
    def get(self, request, *args, **kwargs):
        if not self.authenticate_user(request, *args, **kwargs):
            username = self.kwargs['username']
            return Response({'message': f'User *{username}* not logged in. Please login first.'}, status=status.HTTP_400_BAD_REQUEST)
        return super().get(request, *args, **kwargs)


# User Update
    
class UserUpdateView(generics.UpdateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserUpdateSerializer
    lookup_field = 'username'

    ''' Check if user is logged in or not. If logged in,
        proceed. Else, ask user to login first.
    '''

    def authenticate_user(self, request, *args, **kwargs):
        user = self.get_object()
        username = user.username
        token = Token.objects.filter(user=user)
        if token.exists():
            return True
        else:
            return False

    def update(self, request, *args, **kwargs):
        if not self.authenticate_user(request, *args, **kwargs):
            username = self.kwargs['username']
            return Response({'message': f'User *{username}* not logged in. Please login first.'}, status=status.HTTP_400_BAD_REQUEST)
        return super().update(request, *args, **kwargs)


# User Delete

class UserDeleteView(generics.DestroyAPIView):
    queryset = CustomUser.objects.all()
    lookup_field = 'username'

    ''' Check if user is logged in or not. If logged in,
        proceed. Else, ask user to login first.
    '''

    def authenticate_user(self, request, *args, **kwargs):
        user = self.get_object()
        username = user.username
        token = Token.objects.filter(user=user)
        if token.exists():
            return True
        else:
            return False

    def destroy(self, request, *args, **kwargs):
        if not self.authenticate_user(request, *args, **kwargs):
            username = self.kwargs['username']
            return Response({'message': f'User *{username}* not logged in. Please login first.'}, status=status.HTTP_400_BAD_REQUEST)
        user = self.get_object()
        username = user.username
        user.delete()
        return Response({'message': f'User *{username}* deleted successfully! All team data is deleted.'}, status=status.HTTP_204_NO_CONTENT)


# Team Update
    
class TeamUpdateView(generics.UpdateAPIView):
    queryset = Team.objects.all()
    serializer_class = TeamUpdateSerializer
    lookup_field = 'owner__username'

    ''' Check if user is logged in or not. If logged in,
        proceed. Else, ask user to login first.
    '''

    def authenticate_user(self, request, *args, **kwargs):
        team = self.get_object()
        user = team.owner
        username = user.username
        token = Token.objects.filter(user=user)
        if token.exists():
            return True
        else:
            return False

    def update(self, request, *args, **kwargs):
        if not self.authenticate_user(request, *args, **kwargs):
            username = self.kwargs['owner__username']
            return Response({'message': f'User *{username}* not logged in. Please login first.'}, status=status.HTTP_400_BAD_REQUEST)
        return super().update(request, *args, **kwargs)



# Player Update
    
# # With simple ID
# class PlayerUpdateView(generics.UpdateAPIView):
#     queryset = Player.objects.all()
#     serializer_class = PlayerUpdateSerializer
#     lookup_url_kwarg = 'id'

#     ''' Check if user is logged in or not. If logged in,
#         proceed. Else, ask user to login first.
#     '''

#     def authenticate_user(self, request, *args, **kwargs):
#         teamname = self.kwargs['teamname']
#         team = Team.objects.get(name=teamname)
#         user = team.owner
#         username = user.username
#         token = Token.objects.filter(user=user)
#         if token.exists():
#             return True, username
#         else:
#             return False, username

#     def update(self, request, *args, **kwargs):
#         is_authenticated, username = self.authenticate_user(request, *args, **kwargs)
#         if not is_authenticated:
#             return Response({'message': f'User ({username}) not logged in. Please login first.'}, status=status.HTTP_400_BAD_REQUEST)
#         return super().update(request, *args, **kwargs)

# With UUID 
    
class PlayerUpdateView(generics.UpdateAPIView):
    queryset = Player.objects.all()
    serializer_class = PlayerUpdateSerializer
    lookup_field = 'id'

    ''' Check if user is logged in or not. If logged in,
        proceed. Else, ask user to login first.
    '''

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
            return Response({'message': f'Owner *{username}* of the Team *{teamname}* not logged in. Please login first to update this player record.'}, status=status.HTTP_400_BAD_REQUEST)

        return super().update(request, *args, **kwargs)

# Transfer List Create
    
class TransferListView(generics.CreateAPIView):
    serializer_class = TransferListSerializer
    

# Transfer List View
    
class MarketListView(generics.ListAPIView):
    queryset = TransferList.objects.all()
    serializer_class = MarketListSerializer
    