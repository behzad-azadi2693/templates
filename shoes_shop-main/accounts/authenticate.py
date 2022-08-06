from .models import User
from django.contrib.auth.backends import ModelBackend

class PhoneLoginBackend(ModelBackend):
    def authenticate(self, request, phone=None, password=None):
        try:
            user = User.objects.get(phone = phone)
            if user.check_password(password):
                return user
            return None

        except user.DosNotExist:
            return None
    
    def get_user(self, user_id):
        try:
            return User.objects.get(id=user_id)
        
        except User.DosNotExist:
            return None