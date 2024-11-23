from django.db import models as m1
from django.contrib.auth.models import User
from django.utils import timezone

# Model to track user login history
class UserLoginHistory(m1.Model):
    user = m1.ForeignKey(User, on_delete=m1.CASCADE)  # Links the login event to a specific user
    login_time = m1.DateTimeField(auto_now_add=True)  # Automatically sets the time when the login occurs

    def __str__(self):
        return f"{self.user.username} - {self.login_time}"

# Model to track user expenses with detailed attributes
 
