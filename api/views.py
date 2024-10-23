from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from django.utils import timezone
from datetime import timedelta


SERVER_START_TIME = timezone.now()

def format_uptime(uptime_duration):
    """
    Formats the uptime duration into a human-readable format.
    """
    total_seconds = int(uptime_duration.total_seconds())

    weeks, remainder = divmod(total_seconds, 604800)  # 604800 seconds in a week
    days, remainder = divmod(remainder, 86400)        # 86400 seconds in a day
    hours, remainder = divmod(remainder, 3600)        # 3600 seconds in an hour
    minutes, seconds = divmod(remainder, 60)          # 60 seconds in a minute

    uptime_str = f"{weeks} weeks, {days} days, {hours} hours, {minutes} minutes, {seconds} seconds"
    return uptime_str

class ApiStatusView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request):
        formatted_time = timezone.now().strftime('%H:%M:%S, %Y-%m-%d')
        
        current_time = timezone.now()
        uptime_duration = current_time - SERVER_START_TIME

        uptime_str = format_uptime(uptime_duration)
        
        return Response({
            "message": "Status, OK",
            "api_version": "v1.0.0",
            "server_time": formatted_time,
            "uptime": uptime_str, 
            "status_code": status.HTTP_200_OK,
        }, status=status.HTTP_200_OK)
        
    def post(self, request):
        """Explicitly handle unsupported POST method."""
        return Response({
            "error": "POST method not allowed on this endpoint."
        }, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def put(self, request):
        """Explicitly handle unsupported PUT method."""
        return Response({
            "error": "PUT method not allowed on this endpoint."
        }, status=status.HTTP_405_METHOD_NOT_ALLOWED)


class ApiRootView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request):
        return Response({
            'message': 'Welcome to the InventoryWise API',
            'version': 'v1',
            'base_url': '',
            'documentation': '',
            'services': {
                'user_management_service': {
                    'available_endpoints': {
                        
                    }
                },
                'product_management_service': {
                    'available_endpoints': {
                        
                    }
                }
            }
        })