from django.contrib.auth import authenticate
from django.db.models import Q

from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from rest_framework.authentication import SessionAuthentication, TokenAuthentication

from .helper import CustomUserRateThrottle

from .models import User, FriendRequest
from .serializers import UserSerializer, FriendRequestSerializer

class SignupView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')
        if not email or not password:
            return Response({'error': 'Email and password are required'}, status=status.HTTP_400_BAD_REQUEST)
        user = User.objects.create_user(email=email, password=password, name=request.data.get('name'))
        serializer = self.get_serializer(user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class LoginView(generics.GenericAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        email = request.data.get('email', '').strip().lower()
        password = request.data.get('password', '').strip()
        print("email", email, "password", password)
        if not email or not password:
            return Response({'error': 'Email and password are required'}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(request, username=email, password=password)
        print('user', user)
        if not user:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key}, status=status.HTTP_200_OK)


class UserSearchView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        query = self.request.query_params.get('q', '')
        return User.objects.filter(Q(email__iexact=query) | Q(name__icontains=query))


class SendFriendRequestView(generics.CreateAPIView):
    serializer_class = FriendRequestSerializer
    permission_classes = [IsAuthenticated]
    throttle_scope = 'user'
    throttle_classes = [CustomUserRateThrottle]

    def create(self, request, *args, **kwargs):
        from_user = request.user
        to_user_id = request.data.get('to_user_id')
        
        try:
            to_user = User.objects.get(id=to_user_id)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
        if from_user == to_user:
            return Response({'error': 'You cannot send a friend request to yourself'}, status=status.HTTP_400_BAD_REQUEST)
        if FriendRequest.objects.filter(from_user=from_user, to_user=to_user, status='pending').exists():
            return Response({'error': 'Friend request already sent'}, status=status.HTTP_400_BAD_REQUEST)
        if FriendRequest.objects.filter(from_user=from_user, to_user=to_user, status='accepted').exists():
            return Response({'error': 'You are already friends'}, status=status.HTTP_400_BAD_REQUEST)
        friend_request = FriendRequest(from_user=from_user, to_user=to_user, status='pending')
        friend_request.save()
        return Response({'message': 'Friend request sent'}, status=status.HTTP_201_CREATED)



class AcceptFriendRequestView(generics.UpdateAPIView):
    serializer_class = FriendRequestSerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        friend_request_id = self.kwargs.get('pk')
        friend_request = FriendRequest.objects.get(id=friend_request_id)
        print('friend_request', friend_request)
        print('friend_request.to_user', friend_request.to_user)
        print('request.user', request.user)
        if friend_request.to_user != request.user:
            print('in')
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        friend_request.status = 'accepted'
        friend_request.save()
        return Response({'message': 'Friend request accepted'}, status=status.HTTP_200_OK)


class RejectFriendRequestView(generics.UpdateAPIView):
    serializer_class = FriendRequestSerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        friend_request_id = self.kwargs.get('pk')
        friend_request = FriendRequest.objects.get(id=friend_request_id)
        if friend_request.to_user != request.user:
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        friend_request.status = 'rejected'
        friend_request.save()
        return Response(
            {'message': 'Friend request rejected'},
            status=status.HTTP_200_OK
        )


class ListFriendsView(generics.ListAPIView):
    
    serializer_class = UserSerializer
    authentication_classes = (TokenAuthentication, SessionAuthentication)
    permission_classes = [IsAuthenticated]
    

    def get_queryset(self):
        user = self.request.user
        friends = User.objects.filter(
            Q(sent_requests__to_user=user, sent_requests__status='accepted') |
            Q(received_requests__from_user=user, received_requests__status='accepted')
        )
        print('friends', friends.count())
        return friends

class ListPendingRequestsView(generics.ListAPIView):
    serializer_class = FriendRequestSerializer
    permission_classes = [IsAuthenticated]

    """
    Retrieves the list of pending friend requests for the authenticated user.

    Returns:
        QuerySet: A queryset containing the pending friend requests.
    """
    def get_queryset(self):
        # Get the authenticated user
        user = self.request.user

        # Retrieve the pending friend requests for the user
        pending_requests = FriendRequest.objects.filter(
            Q(from_user=user, status='pending') | 
            Q(to_user=user, status='pending')
        )

        return pending_requests


