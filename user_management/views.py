from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed
from api.serializers import UserSerializer, ProfileSerializer
from django.db.models import Q
from .models import Profile, User
from api.utils import generate_token, generate_refresh_token, JWTAuthentication


class UserRegisterView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        username = request.data.get('username')
        email = request.data.get('email')
        
        if User.objects.filter(username=username).exists():
            return Response({
                "message": "A user with this username already exists",
                "status_code": status.HTTP_400_BAD_REQUEST
			}, status=status.HTTP_400_BAD_REQUEST)
        
        if User.objects.filter(email=email).exists():
            return Response({
                "message": "A user with this email already exists",
                "status_code": status.HTTP_400_BAD_REQUEST
            }, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                'message': "user created successfully",
                'user': UserSerializer(user).data,
                'status_code': status.HTTP_201_CREATED
            }, status=status.HTTP_201_CREATED)
            
        return Response({
            'message': 'Error resgistering user',
            'errors': serializer.errors,
            'status_code': status.HTTP_400_BAD_REQUEST
		}, status=status.HTTP_400_BAD_REQUEST)


class UserLoginView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        identifier = request.data.get('identifier')
        password = request.data.get('password')
        print(identifier)
        
        if not identifier or not password:
            return Response({
                "message": "Username or Email is required",
                "status_code": status.HTTP_400_BAD_REQUEST
            }, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            user = User.objects.get(Q(email=identifier) | Q(username=identifier))
        except User.DoesNotExist:
            raise AuthenticationFailed('User Not Found')
        
        if not user.check_password(password):
            raise AuthenticationFailed("Incorrect Password")
        
        token = generate_token(user)
        refresh_token = generate_refresh_token(user)
        
        response = Response({
            "message": "Login successful",
            "token": token,
            "refresh_token": refresh_token,
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email
            },
            "status_code": status.HTTP_200_OK
		}, status=status.HTTP_200_OK)
        
        response.set_cookie(key='token', value=token, httponly=True)
        return response


class UserProfileView(APIView):
    authentication_classes = [JWTAuthentication]
    
    def get(self, request):
        profile = Profile.objects.get(user=request.user)
        serializer = ProfileSerializer(profile)
        
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
class UserLogoutView(APIView):
    authentication_classes = [JWTAuthentication]
    
    def post(self, request):
        user_token = request.COOKIES.get('token', None)
        if user_token is not None:
            response = Response({
                "message": "Logged Out Successfully",
                "status_code": status.HTTP_200_OK
            }, status=status.HTTP_200_OK)
            
            response.delete_cookie("token")
            return response
        
        return Response({
            "message": "User is already logged out",
            "status_code": status.HTTP_400_BAD_REQUEST
        }, status=status.HTTP_400_BAD_REQUEST)
            

class RefreshTokenView(APIView):
    authentication_classes = [JWTAuthentication]
    
    def post(self, request):
        refresh_token = request.data.get('refresh_token')
        if not refresh_token:
            raise AuthenticationFailed('Refresh token not provided')
        
        try:
            user_id = JWTAuthentication.decode_refresh_token(refresh_token)
            user = User.objects.get(id=user_id)
            new_access_token = generate_token(user)
            response = Response({'access_token': new_access_token})
            response.set_cookie(
                key='access_token',
                value=new_access_token,
                httponly=True,
            )
            return response
        except User.DoesNotExist:
            raise AuthenticationFailed('User not found')
