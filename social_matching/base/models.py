from django.db import models
from django.contrib.auth.models import AbstractUser


# Base user class.
# Stores identifiable information as well as auth information.
# To be deleted once project has ran its course.
class User(AbstractUser):
    details = models.OneToOneField('UserDetails', on_delete=models.PROTECT)
    preferences = models.OneToOneField('UserPreferences', on_delete=models.PROTECT)


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
