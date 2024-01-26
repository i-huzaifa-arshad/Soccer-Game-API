from django.urls import path
from .views import *

urlpatterns = [
    path('signup/', UserRegisterView.as_view(), name='user-register'),
    path('login/', UserLoginView.as_view(), name='user-login'),
    path('logout/<str:username>/', UserLogoutView.as_view(), name= 'user-logout'),
    path('list_users/', UserListView.as_view(), name='user-list'),
    path('user_details/<str:username>/', UserDetailView.as_view(), name='user-detail'),   
    path('delete_user/<str:username>/', UserDeleteView.as_view(), name='user-delete'), 
    path('user_update/<str:username>/', UserUpdateView.as_view(), name='user-update'),
    path('player_update/<str:teamname>/<uuid:id>/', PlayerUpdateView.as_view(), name='player-update'),
    path('team_update/<str:owner__username>/', TeamUpdateView.as_view(), name='team-update'),
    path('transfer_list/<str:username>/', TransferListView.as_view(), name='transfer-list'),
    path('market_list/', MarketListView.as_view(), name='market-list')
    # path('buy_player/<str:username>/', BuyPlayerView.as_view(), name='buy-player')
]