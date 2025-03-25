from rest_framework.authentication import TokenAuthentication

class CookieTokenAuthentication(TokenAuthentication):
    def authenticate(self, request):
        token = request.COOKIES.get('access_token')
        if not token:
            return None

        return self.authenticate_credentials(token)
