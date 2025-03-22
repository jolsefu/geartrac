from rest_framework.views import APIView, Response
from .serializers import UserSerializer
from django.http import HttpResponse

class SignupView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)

def index(request):
    return HttpResponse("Hello, there")
