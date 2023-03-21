from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model


# Modified user creation form to use the updated user class.
class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = get_user_model()
        fields = ("username", "password1", "password2")
