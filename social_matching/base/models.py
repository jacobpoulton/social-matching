from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _


# Custom user manager used for the below user class.
class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, password=None):
        # Require email
        if not email:
            raise ValueError("Users require an email address.")

        # Create and save model
        user = self.model(email=self.normalize_email(email))
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        # Create regular user and apply admin
        user = self.create_user(email, password=password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


# Base user class.
# Stores identifiable information as well as auth information.
# To be deleted once project has ran its course.
class User(AbstractUser):
    # Username is replaced with email field
    username = None
    email = models.EmailField(_('email address'), unique=True)
    objects = UserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    # Relations to other user data
    details = models.OneToOneField('UserDetails', on_delete=models.PROTECT, null=True)
    preferences = models.OneToOneField('UserPreferences', on_delete=models.PROTECT, null=True)


# User details class.
# Stores non-identifiable information pertaining to matchmaking the user.
# Will represent the user in a non-identifiable manner once the base user class is deleted.
class UserDetails(models.Model):
    pass


# User preferences class.
# Stores user use preferences for the software.
# Will be deleted along with the base user class.
class UserPreferences(models.Model):
    pass


# Survey data class.
# Stores survey participation data associated with user details data.
# Non-identifiable.
class SurveyData(models.Model):
    user = models.OneToOneField('UserDetails', on_delete=models.CASCADE)


# Match class.
# Groups together details of users matched, as well as data relating to the match.
# All users are non-identifiable.
class Match(models.Model):
    pass
