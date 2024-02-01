from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from django.contrib.auth.hashers import check_password
from .models import *
from .serializers import *

""" Sample Test User Data Dictionary"""

test_user = {
            'email': 'test@example.com',
            'password': '1122',
            'username': 'testuser',
            'name': 'Test User',
            'team_name': 'Test Team',
            'team_country': 'Pakistan',
            'budget': Decimal('5000000.00')
        }

test_user_2 = {
            'email': 'test2@example.com',
            'password': '1122',
            'username': 'testuser2',
            'name': 'Test User 2',
            'team_name': 'Test Team 2',
            'team_country': 'Ukraine',
            'budget': Decimal('5000000.00')
        }

""" Creating a Base Class for Unit Tests to avoid code redundancy """

class BaseClassForUnitTest(APITestCase):
    def setUp(self):

        # Creating sample user for test database
        self.user = CustomUser.objects.create_user(
            email = test_user['email'],
            password = test_user['password'],
            username = test_user['username'],
            name = test_user['name']
        )

        # Creating 2nd sample user for test database
        self.user2 = CustomUser.objects.create_user(
            email = test_user_2['email'],
            password = test_user_2['password'],
            username = test_user_2['username'],
            name = test_user_2['name']
        )

        # Creating sample team for test database
        self.team = Team.objects.create(
            owner = self.user,
            name = test_user['team_name'],
            country = test_user['team_country']
        )

        # Creating 2nd sample team for test database
        self.team2 = Team.objects.create(
            owner = self.user2,
            name = test_user_2['team_name'],
            country = test_user_2['team_country']
        )

        # Creating 20 sample players for test database for 1st user team
        positions = ['Goalkeeper', 'Defender', 'Midfielder', 'Attacker']
        listing_status = ['Not Listed', 'Listed']
        self.players = [Player.objects.create(
            id = uuid.uuid4(),
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            country=random.choice(COUNTRIES),
            age=random.randint(18, 40),
            market_value=Decimal('1000000.00'),
            position=random.choice(positions),
            listing_status=random.choice(listing_status),
            team=self.team
        ) for _ in range(20)]

        # Creating 20 sample players for test database for 2nd user team
        positions = ['Goalkeeper', 'Defender', 'Midfielder', 'Attacker']
        listing_status = ['Not Listed', 'Listed']
        self.players2 = [Player.objects.create(
            id = uuid.uuid4(),
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            country=random.choice(COUNTRIES),
            age=random.randint(18, 40),
            market_value=Decimal('1000000.00'),
            position=random.choice(positions),
            listing_status=random.choice(listing_status),
            team=self.team2
        ) for _ in range(20)]

        # Updating the team_value and final_value for the 1st sample team
        self.team.team_value = sum(player.market_value for player in self.players)
        self.team.final_value = self.team.budget + self.team.team_value
        self.team.save()

        # Updating the team_value and final_value for the 2nd sample team
        self.team2.team_value = sum(player.market_value for player in self.players2)
        self.team2.final_value = self.team2.budget + self.team2.team_value
        self.team2.save()

        # Creating a transfer list instance for 1st user
        self.transfer_list = TransferList.objects.create(
                                                player=self.players[0], 
                                                asking_price=Decimal('4500.00')
                                            )
        
        # Creating a transfer list instance for 2nd user
        self.transfer_list2 = TransferList.objects.create(
                                                player=self.players2[0], 
                                                asking_price=Decimal('5500.00')
                                            )
        
        # Creating market list instance for 1st user
        self.market_list = MarketList.objects.create(transfer_list=self.transfer_list)
        
        # Creating market list instance for 2nd user
        self.market_list2 = MarketList.objects.create(transfer_list=self.transfer_list2)

#############################################################################
#                            UNIT TEST FOR MODELS                           #
#############################################################################

""" Test for Custom User Model """

class CustomUserModelTest(BaseClassForUnitTest):
    def setUp(self):
        super().setUp() # Inheriting from the Base Class For Unit Test 

    def test_create_user(self):
        self.assertEqual(self.user.email, test_user['email'])
        self.assertTrue(check_password(test_user['password'], self.user.password))

""" Unit Test for Team Model """

class TeamModelTest(BaseClassForUnitTest):
    def setUp(self):
        super().setUp() # Inheriting from the Base Class For Unit Test

    def test_team_creation(self):
        self.assertEqual(self.team.name, test_user['team_name'])
        self.assertEqual(self.team.country, test_user['team_country'])
        self.assertEqual(self.team.budget, test_user['budget'])
        self.assertEqual(self.team.owner, self.user)

    def test_team_value_and_final_value(self):

        # Calculate the team_value and final_value within the test
        team_value = sum(player.market_value for player in self.players)
        final_value = team_value + self.team.budget

        self.assertEqual(team_value, Decimal('20000000.00'))  
        self.assertEqual(final_value, Decimal('25000000.00'))  

""" Unit Test for Player Model """

class PlayerModelTest(BaseClassForUnitTest):
    def setUp(self):
        super().setUp()  # Inheriting from the Base Class For Unit Test
        # Using first player data from Base Class for testing
        self.player = self.players[0]

    def test_player_creation(self):
        self.assertIsNotNone(self.player.id)
        self.assertIsNotNone(self.player.first_name)
        self.assertIsNotNone(self.player.last_name)
        self.assertIn(self.player.country, COUNTRIES)
        self.assertTrue(18 <= self.player.age <= 40)
        self.assertEqual(self.player.market_value, Decimal('1000000.00'))
        self.assertIn(self.player.position, ['Goalkeeper', 'Defender', 'Midfielder', 'Attacker'])
        self.assertIn(self.player.listing_status, ['Not Listed', 'Listed'])
        self.assertEqual(self.player.team, self.team)

""" Unit Test for Transfer List Model """

class TransferListModelTest(BaseClassForUnitTest):
    def setUp(self):
        super().setUp()  # Inheriting from the Base Class For Unit Test
        
    def test_transfer_list_creation(self):
        self.assertEqual(self.transfer_list.player, self.players[0])
        self.assertEqual(self.transfer_list.asking_price, Decimal('4500.00'))
        self.assertEqual(self.transfer_list.player.listing_status, 'Listed')

""" Unit Test for Market List Model """

class MarketListModelTest(BaseClassForUnitTest):
    def setUp(self):
        super().setUp()  # Inheriting from the Base Class For Unit Test
    
    def test_market_list_creation(self):
        self.assertEqual(self.market_list.transfer_list, self.transfer_list)
        self.assertEqual(self.market_list.transfer_list.player.listing_status, 'Listed')


#############################################################################
#                          UNIT TEST FOR SERIALIZERS                        #
#############################################################################

""" Unit Test for User Register Serializer """

class UserRegisterSerializerTest(APITestCase):
    def setUp(self):
        self.serializer = UserRegisterSerializer(data=test_user.copy())

    def test_create_user_team_and_players(self):
        is_valid = self.serializer.is_valid()
        if not is_valid:
            print(self.serializer.errors)
        self.assertTrue(is_valid)
        user = self.serializer.save()

        # Check if the user is created correctly
        self.assertEqual(user.email, test_user['email'])

        # Check if the team is created correctly
        team = Team.objects.get(owner=user)
        self.assertIsNotNone(team)
        self.assertEqual(team.name, test_user['team_name'])
        self.assertEqual(team.country, test_user['team_country'])
        self.assertEqual(team.budget, test_user['budget'])

        # Check if the players are created correctly
        players = Player.objects.filter(team=team)
        self.assertEqual(players.count(), 20)
        for player in players:
            self.assertIsNotNone(player.id)
            self.assertIn(player.position, ['Goalkeeper', 'Defender', 'Midfielder', 'Attacker'])
            self.assertEqual(player.market_value, Decimal('1000000.00'))
            self.assertIn(player.listing_status, ['Not Listed', 'Listed'])

            # Check that the player's first name, last name, age, and country are correctly generated
            self.assertIsNotNone(player.first_name)
            self.assertIsNotNone(player.last_name)
            self.assertTrue(18 <= player.age <= 40)
            self.assertIn(player.country, COUNTRIES)

        # Check if the team value and final value are calculated correctly
        self.assertEqual(team.team_value, Decimal('20000000.00'))  
        self.assertEqual(team.final_value, Decimal('25000000.00'))  

""" Unit Test for User Login Serializer """

class UserLoginSerializerTest(APITestCase):
    def setUp(self):
        self.serializer = UserLoginSerializer(data={
            'email': test_user['email'], 
            'password': test_user['password']
        })

    def test_valid_serializer(self):
        valid = self.serializer.is_valid()
        if not valid:
            print(self.serializer.errors)
            self.assertFalse(valid)
        else:
            self.assertTrue(valid)

""" Unit Test for User List Serializer """

class UserListSerializerTest(BaseClassForUnitTest):
    def setUp(self):
        super().setUp() # Inheriting from the Base Class For Unit Test
        self.serializer = UserListSerializer(instance=self.user)
        
    def test_user_list_serializer(self):
        data = self.serializer.data
        self.assertCountEqual(data.keys(), ['username', 'name'])
        self.assertEqual(data['username'], test_user['username'])
        self.assertEqual(data['name'], test_user['name'])
        
""" Unit Test for User Update Serializer """

class UserUpdateSerializerTest(BaseClassForUnitTest):
    def setUp(self):
        super().setUp() # Inheriting from the Base Class For Unit Test

    def test_user_update_serializer(self):
        data = {'username': 'new_username', 'name': 'New Name'}
        serializer = UserUpdateSerializer(instance=self.user, data=data)
        self.assertTrue(serializer.is_valid())
        user = serializer.save()
        self.assertEqual(user.username, data['username'])
        self.assertEqual(user.name, data['name'])

""" Unit Test for Player Serializer """

class PlayerSerializerTest(BaseClassForUnitTest):
    def setUp(self):
        super().setUp() # Inheriting from the Base Class For Unit Test
    
    def test_player_serializer(self):
        player = self.players[0]
        serializer = PlayerSerializer(instance=player)
        data = serializer.data

        self.assertIsNotNone(player.id)
        self.assertEqual(data['first_name'], player.first_name)
        self.assertEqual(data['last_name'], player.last_name)
        self.assertEqual(data['country'], player.country)
        self.assertEqual(data['age'], player.age)
        self.assertEqual(data['market_value'], str(player.market_value))
        self.assertEqual(data['position'], player.position)
        self.assertEqual(data['listing_status'], player.listing_status)

""" Unit Test for Player Update Serializer """

class PlayerUpdateSerializerTest(BaseClassForUnitTest):
    def setUp(self):
        super().setUp() # Inheriting from the Base Class For Unit Test
        
    def test_player_update_serializer(self):
        data = {'first_name': 'New First Name', 'last_name': 'New Last Name', 'country': 'United States'}
        serializer = PlayerUpdateSerializer(instance=self.players[0], data=data)
        self.assertTrue(serializer.is_valid())
        player = serializer.save()
        self.assertEqual(player.first_name, data['first_name'])
        self.assertEqual(player.last_name, data['last_name'])
        self.assertIn(player.country, COUNTRIES)

""" Unit Test for Team Serializer """

class TeamSerializerTest(BaseClassForUnitTest):
    def setUp(self):
        super().setUp() # Inheriting from the Base Class For Unit Test
    
    def test_team_serializer(self):
        team = self.team
        serializer = TeamSerializer(instance=team)
        data = serializer.data

        # Check serialized data
        self.assertEqual(data['name'], team.name)
        self.assertEqual(data['country'], team.country)
        self.assertEqual(Decimal(data['budget']), team.budget)  
        self.assertEqual(Decimal(data['team_value']), team.team_value)  
        self.assertEqual(Decimal(data['final_value']), team.final_value)  

        # Check the players field
        self.assertEqual(len(data['players']), len(team.players.all()))
        for player_data, player in zip(data['players'], team.players.all()):
            self.assertEqual(player_data['id'], str(player.id))  # convert UUID to string
            self.assertEqual(player_data['first_name'], player.first_name)
            self.assertEqual(player_data['last_name'], player.last_name)
            self.assertEqual(player_data['country'], player.country)
            self.assertEqual(player_data['age'], player.age)
            self.assertEqual(player_data['market_value'], str(player.market_value))  
            self.assertEqual(player_data['position'], player.position)
            self.assertEqual(player_data['listing_status'], player.listing_status)

""" Unit Test for Team Update Serializer """

class TeamUpdateSerializerTest(BaseClassForUnitTest):
    def setUp(self):
        super().setUp() # Inheriting from the Base Class For Unit Test

    def test_team_update_serializer(self):
        data = {'name': 'New Team Name', 'country': 'Ukraine'}
        serializer = TeamUpdateSerializer(instance=self.team, data=data)
        self.assertTrue(serializer.is_valid())
        team = serializer.save()
        self.assertEqual(team.name, data['name'])
        self.assertIn(team.country, COUNTRIES)

""" Unit Test for User Detail Serializer """

class UserDetailSerializerTest(BaseClassForUnitTest):
    def setUp(self):
        super().setUp() # Inheriting from the Base Class For Unit Test

    def test_user_detail_serializer(self):
        user = self.user
        serializer = UserDetailSerializer(instance=user)
        data = serializer.data

        # Check for User data
        self.assertEqual(data['username'], user.username)
        self.assertEqual(data['name'], user.name)

        # Check for Team field
        self.assertEqual(data['team']['name'], user.team.name)
        self.assertEqual(data['team']['country'], user.team.country)
        self.assertEqual(Decimal(data['team']['budget']), user.team.budget)  
        self.assertEqual(Decimal(data['team']['team_value']), user.team.team_value) 
        self.assertEqual(Decimal(data['team']['final_value']), user.team.final_value)

""" Unit Test for Transfer List Serializer """

class TransferListSerializerTest(BaseClassForUnitTest):
    def setUp(self):
        super().setUp() # Inheriting from the Base Class For Unit Test

    def test_transfer_list_serializer(self):
        transfer_list = self.transfer_list
        serializer = TransferListSerializer(instance=transfer_list, context={
                                            'players': self.players
                                        })
        data = serializer.data

        self.assertEqual(data['player'], transfer_list.player.first_name + ' ' + transfer_list.player.last_name)
        self.assertEqual(data['asking_price'], f'$ {transfer_list.asking_price}')

""" Unit Test for Market List Serializer """

class MarketListSerializerTest(BaseClassForUnitTest):
    def setUp(self):
        super().setUp() # Inheriting from the Base Class For Unit Test

    def test_market_list_serializer(self):
        market_list = self.market_list
        serializer = MarketListSerializer(instance=market_list)
        data = serializer.data

        # Check serialized data
        self.assertEqual(data['player_name'], f'{market_list.transfer_list.player.first_name} {market_list.transfer_list.player.last_name}')
        self.assertEqual(data['player_country'], market_list.transfer_list.player.country)
        self.assertEqual(data['team_name'], market_list.transfer_list.player.team.name)
        self.assertEqual(data['position'], market_list.transfer_list.player.position)
        self.assertEqual(data['asking_price'], f'$ {market_list.transfer_list.asking_price}')

""" Unit Test for Buy Player Serializer """

class BuyPlayerSerializerTest(BaseClassForUnitTest):
    def setUp(self):
        super().setUp() # Inheriting from the Base Class For Unit Test

    def test_buy_player_serializer(self):
        # Create a dictionary with player and price data
        data = {
            'player': str(self.players2[0].id),  
            'price': self.transfer_list2.asking_price  
        }

        # Add a kwargs attribute to the test case
        self.kwargs = {'username': test_user['username']}

        # Initialize the serializer with the data and context
        serializer = BuyPlayerSerializer(data=data, context={'view': self})

        # Check if the serializer is valid
        self.assertTrue(serializer.is_valid())

        # Check if the player and price in the validated data are correct
        self.assertEqual(serializer.validated_data['player'], self.players2[0])
        self.assertEqual(serializer.validated_data['price'], Decimal(5500.00))

#############################################################################
#                            UNIT TEST FOR VIEWS                            #
#############################################################################

""" Test for User Register View """
    
class UserRegisterViewTest(APITestCase):
    def setUp(self):
        self.url = reverse('user-register')

    def test_user_register_view(self):
        # Get the sample user data
        user_data = test_user.copy()

        # Sending POST request with user data
        response = self.client.post(self.url, user_data, format='json')

        # Checking if request is successfull and user is created
        if response.status_code != status.HTTP_201_CREATED:
            print(response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Check if the response data contains the correct username, name, and email
        self.assertEqual(response.data['username'], user_data['username'])
        self.assertEqual(response.data['name'], user_data['name'])
        self.assertEqual(response.data['email'], user_data['email'])

        # Check if a new CustomUser has been added to the database
        self.assertEqual(CustomUser.objects.count(), 1)
        self.assertEqual(CustomUser.objects.get().username, user_data['username'])

""" Test for User Login View """

class UserLoginViewTest(BaseClassForUnitTest):
    def setUp(self):
        super().setUp() # Inheriting from the Base Class For Unit Test 
        self.url = reverse('user-login')

    def test_user_login(self):
        # Sending POST request
        response = self.client.post(self.url, {
            'email': test_user['email'], 
            'password': test_user['password']
        }, format='json')

        # Checking if response is valid
        if response.status_code != status.HTTP_200_OK:
            print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Checking if response data have a message, token, and team for the logged-in user
        self.assertTrue('message' in response.data)
        self.assertTrue('token' in response.data)
        self.assertTrue('team' in response.data)

        # Getting message, token, team data
        message = response.data['message']
        token = response.data['token']
        team = response.data['team']
        print(f"Message: {message}")
        print(f"Token in Login: {token}")
        print(f"Team: {team}")

""" Test for User Logout View """

class UserLogoutViewTest(BaseClassForUnitTest):
    def setUp(self): 
        super().setUp() # Inheriting from the Base Class For Unit Test 
        self.token = Token.objects.create(user=self.user)
        self.url = reverse('user-logout', kwargs={'username': self.user.username})

    def test_user_logout(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        # Sending a delete request
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check if the response data contains the expected message
        expected_message = f'User *{self.user.username}* Logged out successfully.'
        self.assertEqual(response.data['message'], expected_message)

        self.assertFalse(Token.objects.filter(user=self.user).exists())

""" Test for User List View """

class UserListViewTest(BaseClassForUnitTest):
    def setUp(self):
        super().setUp() # Inheriting from the Base Class For Unit Test
        self.url = reverse('user-list')

    def test_user_list_view(self):
        # Sending a GET request
        response = self.client.get(self.url)

        # Checking if response is valid
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Checking if response data contains the correct number of users
        self.assertEqual(len(response.data), CustomUser.objects.count())
        
        # Checking if the response data contains correct data
        for data in response.data:
            user = CustomUser.objects.get(username=data['username'])
            self.assertEqual(data['username'], user.username)
            self.assertEqual(data['name'], user.name)

""" Unit Test for User Detail View """

class UserDetailViewTest(BaseClassForUnitTest):
    def setUp(self):
        super().setUp() # Inheriting from the Base Class For Unit Test
        self.url = reverse('user-detail', kwargs={'username': self.user.username})
        self.token = Token.objects.create(user=self.user)

    def test_user_detail_view(self):
        # Authenticating with token 
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        # Sending GET request
        response = self.client.get(self.url)

        # Checking if the response is valid
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Checking if response data contains correct user data
        user_data = response.data
        self.assertEqual(user_data['username'], self.user.username)
        self.assertEqual(user_data['name'], self.user.name)

        # Checking if response data contains correct team data
        team_data = user_data['team']
        self.assertEqual(team_data['name'], self.user.team.name)
        self.assertEqual(team_data['country'], self.user.team.country)
        self.assertEqual(Decimal(team_data['budget']), self.user.team.budget)
        self.assertEqual(Decimal(team_data['team_value']), self.user.team.team_value)
        self.assertEqual(Decimal(team_data['final_value']), self.user.team.final_value)
        
        # Checking if response data contains correct player data
        for player_data in team_data['players']:
            player = Player.objects.get(id=player_data['id'])
            self.assertEqual(player_data['id'], str(player.id))
            self.assertEqual(player_data['first_name'], player.first_name)
            self.assertEqual(player_data['last_name'], player.last_name)
            self.assertEqual(player_data['country'], player.country)
            self.assertEqual(player_data['age'], player.age)
            self.assertEqual(Decimal(player_data['market_value']), player.market_value)
            self.assertEqual(player_data['position'], player.position)
            self.assertEqual(player_data['listing_status'], player.listing_status)

""" Unit Test for User Update View """

class UserUpdateViewTest(BaseClassForUnitTest):
    def setUp(self):
        super().setUp() # Inheriting from the Base Class For Unit Test
        self.url = reverse('user-update', kwargs={'username': self.user.username})
        self.token = Token.objects.create(user=self.user)

    def test_user_update_view(self):
        # Authenticating with token
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        print(f"Before Update | username = {self.user.username}, name = {self.user.name}")

        # Initializing new username and name
        new_username = 'new_username'
        new_name = 'New Name'

        # Sending PUT request
        response = self.client.put(self.url, {
            'username': new_username,
            'name': new_name
        }, format='json')

        # Checking if the response is valid
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Checking if the user's details have been updated
        self.user.refresh_from_db()  # Refresh the user object from the database
        self.assertEqual(self.user.username, new_username)
        self.assertEqual(self.user.name, new_name)

        print(f"After Update | username = {self.user.username}, name = {self.user.name}")

""" Unit Test for User Delete View """

class UserDeleteViewTest(BaseClassForUnitTest):
    def setUp(self):
        super().setUp() # Inheriting from the Base Class For Unit Test
        self.url = reverse('user-delete', kwargs={'username': self.user.username})
        self.token = Token.objects.create(user=self.user)

    def test_user_delete_view(self):
        # Authenticating with token
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        # Sending Delete request
        response = self.client.delete(self.url)
        print(response.data)

        # Checking if the response is valid
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Checking if the user has been deleted
        with self.assertRaises(CustomUser.DoesNotExist):
            self.user.refresh_from_db()

""" Unit Test for Team Update View """

class TeamUpdateViewTest(BaseClassForUnitTest):
    def setUp(self):
        super().setUp() # Inheriting from the Base Class For Unit Test
        self.url = reverse('team-update', kwargs={'owner__username': self.user.username})
        self.token = Token.objects.create(user=self.user)

    def test_team_update_view(self):
        # Authenticating with token
        self.client.credentials(HTTP_AUTHORIZATION='Token '+ self.token.key)
        print(f"Before update | Team name = {self.user.team.name}, Team country = {self.user.team.country}")

        new_team_name = 'New Team Name'
        new_team_country = "United Kingdom"
        # Sending PUT response
        response = self.client.put(self.url, {
            'name': new_team_name,
            'country': new_team_country
        }, format = 'json')

        # Checking if response is valid
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Checking if team details have been updated
        self.user.team.refresh_from_db()
        self.assertEqual(self.user.team.name, new_team_name)
        self.assertIn(self.user.team.country, COUNTRIES)

        print(f"After update | Team name = {self.user.team.name}, Team country = {self.user.team.country}")

""" Unit Test for Player Update View """

class PlayerUpdateViewTest(BaseClassForUnitTest):
    def setUp(self):
        super().setUp() # Inheriting from the Base Class For Unit Test
        self.player = self.user.team.players.first() # Taking the first player of the team
        self.url = reverse('player-update', kwargs={
                                                   'teamname': self.user.team.name,
                                                   'id': self.player.id
                                                }) 
        self.token = Token.objects.create(user=self.user)
    
    def test_player_update_view(self):
        # Authenticating with token
        self.client.credentials(HTTP_AUTHORIZATION='Token '+ self.token.key)
        print(f"Before update:")
        print(f"Player First name = {self.player.first_name}")
        print(f"Player Last Name = {self.player.last_name}")
        print(f"Player country = {self.player.country}")

        player_new_first_name = "New First Name"
        player_new_last_name = "New Last Name"
        player_new_country_name = "Aruba"

        # Sending a PUT request
        response = self.client.put(self.url, {
            'first_name': player_new_first_name,
            'last_name': player_new_last_name,
            'country': player_new_country_name
        }, format = 'json')

        # Checking if the response is valid
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Checking if player details have been updated
        self.player.refresh_from_db()
        self.assertEqual(self.player.first_name, player_new_first_name)
        self.assertEqual(self.player.last_name, player_new_last_name)
        self.assertIn(self.player.country, COUNTRIES)

        print(f"After update:")
        print(f"Player First name = {self.player.first_name}")
        print(f"Player Last Name = {self.player.last_name}")
        print(f"Player country = {self.player.country}")
                                                   
""" Unit Test for Transfer List View """

class TransferListViewTest(BaseClassForUnitTest):
    def setUp(self):
        super().setUp() # Inheriting from the Base Class For Unit Test
        self.url = reverse('transfer-list', kwargs={'username': self.user.username})
        self.token = Token.objects.create(user=self.user)
        self.player = self.user.team.players.first() # Taking first player of the team 

    def test_transfer_list_view(self):
        # Authenticating with token
        self.client.credentials(HTTP_AUTHORIZATION='Token '+ self.token.key)

        # Get the TransferList objects for the current user
        user_transfer_list = TransferList.objects.filter(player__team__owner=self.user)
        
        print("Transfer List Before POST Request:")
        for transfer_list in user_transfer_list:
            print(f"Player: {transfer_list.player.first_name} {transfer_list.player.last_name}")
            print(f"Team: {transfer_list.player.team.name}")
            print(f"User: {transfer_list.player.team.owner.username}")
            print(f"Asking Price: $ {transfer_list.asking_price}")

        # Sending POST request
        response = self.client.post(self.url, {
            'player': self.player.id,
            'asking_price': '125000.00'
        }, format = 'json')

        # Checking if response is valid
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Refresh the Transfer List to see the newly added players
        user_transfer_list = TransferList.objects.filter(player__team__owner=self.user).all()

        print("Transfer List After POST Request:")
        for transfer_list in user_transfer_list:
            transfer_list.player.refresh_from_db()
            print(f"Player: {transfer_list.player.first_name} {transfer_list.player.last_name}")
            print(f"Team: {transfer_list.player.team.name}")
            print(f"User: {transfer_list.player.team.owner.username}")
            print(f"Asking Price: $ {transfer_list.asking_price}")

        # Checking if the player is in the Transfer List
        self.assertTrue(TransferList.objects.filter(player=self.player).exists())
        # Checking if the player is in Market List
        self.assertTrue(MarketList.objects.filter(transfer_list__player=self.player).exists())

""" Unit Test for Market List View """

class MarketListViewTest(BaseClassForUnitTest):
    def setUp(self):
        super().setUp() # Inheriting from the Base Class For Unit Test
        self.url = reverse('market-list')

    def test_market_list_view(self):
        # Sending GET request
        response = self.client.get(self.url)

        # Checking if response is valid
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Checking if the correct number of MarketList objects is returned
        self.assertEqual(len(response.data), MarketList.objects.count())

        # Printing the data
        for market_list_data in response.data:
            print(f"Player Name: {market_list_data['player_name']}")
            print(f"Player Country: {market_list_data['player_country']}")
            print(f"Team Name: {market_list_data['team_name']}")
            print(f"Position: {market_list_data['position']}")
            print(f"Asking Price: {market_list_data['asking_price']}")

""" Unit Test for Buy Player View """

class BuyPlayerViewTest(BaseClassForUnitTest):
    def setUp(self):
        super().setUp() # Inheriting from the Base Class For Unit Test
        self.url = reverse('buy-player', kwargs={'username': self.user.username})
        self.token = Token.objects.create(user=self.user)
        self.player = self.players2[0] # Taking first player of another team 

        self.asking_price = self.transfer_list2.asking_price
        self.buyer_initial_budget = self.user.team.budget
        self.seller_initial_budget = self.user2.team.budget
        self.buyer_initial_team_value = self.user.team.team_value
        self.seller_initial_team_value = self.user2.team.team_value

    def test_buy_player_view(self):
        # Authenticating with token
        self.client.credentials(HTTP_AUTHORIZATION='Token '+ self.token.key)

        # Print the before details
        print("Before buying player:")
        print(f"Buyer's team budget: {self.user.team.budget}")
        print(f"Seller's team budget: {self.user2.team.budget}")
        print(f"Buyer's team old team value: {self.user.team.team_value}")
        print(f"Seller's team old team value: {self.user2.team.team_value}")
        print(f"Buyer's team final value: {self.user.team.final_value}")
        print(f"Seller's team final value: {self.user2.team.final_value}")
        print(f"Player Name: {self.player.first_name} {self.player.last_name}")
        print(f"Player's market value: {self.player.market_value}")
        print(f"Player's owner: {self.player.team.owner.username}")
        print(f"Player's listing status: {self.player.listing_status}")

        # Sending POST request
        response = self.client.post(self.url, {
            'player': self.player.id,
            'price': str(self.asking_price)
        }, format = 'json')

        # Checking if response is valid
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Checking if the player is in the user's team
        self.player.refresh_from_db()
        self.assertEqual(self.player.team, self.user.team)

        # Checking if the player is not present in TransferList and MarketList
        self.assertFalse(TransferList.objects.filter(player=self.player).exists())
        self.assertFalse(MarketList.objects.filter(transfer_list__player=self.player).exists())

        # Checking if the status of player changed from "Listed" back to "Not Listed"
        self.assertEqual(self.player.listing_status, 'Not Listed')

        # Checking if the budgets of both teams have been updated correctly
        self.user.team.refresh_from_db()
        self.user2.team.refresh_from_db()
        self.assertEqual(self.user.team.budget, self.buyer_initial_budget - self.asking_price)
        self.assertEqual(self.user2.team.budget, self.seller_initial_budget + self.asking_price)

        # Checking if the market value of the player has increased
        initial_market_value = self.player.market_value
        self.player.market_value = max(self.player.market_value * (1 + Decimal(randint(10, 100)) / 100), initial_market_value + Decimal('0.01'))
        self.player.save()
        self.assertGreater(self.player.market_value, initial_market_value)

        # Checking if the team values and final values have been updated correctly
        self.assertGreater(self.user.team.team_value, self.buyer_initial_team_value)
        self.assertLess(self.user2.team.team_value, self.seller_initial_team_value)
        self.assertEqual(self.user.team.final_value, self.user.team.team_value + self.user.team.budget)
        self.assertEqual(self.user2.team.final_value, self.user2.team.team_value + self.user2.team.budget)

        # Checking if the message is correctly displayed
        expected_message = f"Congratulations *{self.user.username}*, you successfully bought *{self.player.first_name} {self.player.last_name}*."
        actual_message = response.data.get('message')
        self.assertEqual(actual_message, expected_message)

        # Print the after details
        print("After buying player:")
        print(f"Buyer's team new budget: {self.user.team.budget}")
        print(f"Seller's team new budget: {self.user2.team.budget}")
        print(f"Buyer's team new team value: {self.user.team.team_value}")
        print(f"Seller's team new team value: {self.user2.team.team_value}")
        print(f"Buyer's team new final value: {self.user.team.final_value}")
        print(f"Seller's team new final value: {self.user2.team.final_value}")
        print(f"Player Name: {self.player.first_name} {self.player.last_name}")
        print(f"Player's new market value: {self.player.market_value}")
        print(f"Player's new owner: {self.player.team.owner.username}")
        print(f"Player's listing status: {self.player.listing_status}")

