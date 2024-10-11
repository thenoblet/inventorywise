from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone


class ApiStatusView(APIView):
    def get(self, request):
        formatted_time = timezone.now().strftime('%H:%M:%S, %Y-%m-%d')
        
        return Response({
            "message": "Status, OK",
            "api_version": "v1.0.0",
            "server_time": formatted_time,
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
