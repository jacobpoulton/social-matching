from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _
from django.conf import settings


# Custom user manager used for the below user class.
class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, password=None, consent=False):
        # Require email
        if not email:
            raise ValueError("Users require an email address.")

        # Create user
        user = self.model(email=self.normalize_email(email))
        user.set_password(password)

        # Apply consent if admin, otherwise wait until user consents manually
        user.consent_information_sheet = consent
        user.consent_participation = consent
        user.consent_publication = consent

        # Save and return
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        # Create regular user and set admin
        user = self.create_user(email, password=password, consent=True)
        user.is_staff = True
        user.is_superuser = True

        # Save and return
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

    # Contact
    contact = models.TextField(max_length=128, null=True)

    # Consent
    # - All required to be true
    consent_information_sheet = models.BooleanField()
    consent_participation = models.BooleanField()
    consent_publication = models.BooleanField()

    # Relations to other user data
    details = models.OneToOneField('UserDetails', on_delete=models.PROTECT, null=True)
    preferences = models.OneToOneField('UserPreferences', on_delete=models.PROTECT, null=True)

    def match_count(self) -> int:
        return self.details.match_set.all().count()

    def is_matchable(self) -> bool:
        return (
            not self.is_staff
            and not self.is_superuser
            and self.preferences.in_match_pool
        )

    @classmethod
    def can_match(cls) -> bool:
        # Conditions necessary for matching
        return (
            len(cls.matchable_users()) > settings.GROUP_SIZE_MIN
        )

    @classmethod
    def matchable_users(cls) -> models.QuerySet:
        return cls.objects.filter(is_staff=False, is_superuser=False, preferences__in_match_pool=True)


# User details class.
# Stores non-identifiable information pertaining to matchmaking the user.
# Will represent the user in a non-identifiable manner once the base user class is deleted.
class UserDetails(models.Model):
    agreeableness = models.DecimalField(max_digits=3, decimal_places=3, default=0.5)
    neuroticism = models.DecimalField(max_digits=3, decimal_places=3, default=0.5)
    extroversion = models.DecimalField(max_digits=3, decimal_places=3, default=0.5)

    # Heuristic used in matching (agreeableness * 1-neuroticism)
    heuristic = models.DecimalField(max_digits=3, decimal_places=3, default=0.5)


# User preferences class.
# Stores user use preferences for the software.
# Will be deleted along with the base user class.
class UserPreferences(models.Model):
    in_match_pool = models.BooleanField(default=True)
    notification_match = models.BooleanField(default=True)
    notification_survey = models.BooleanField(default=True)


# Survey data class.
# Stores survey participation data associated with user details data.
# Non-identifiable.
class SurveyData(models.Model):
    user_details = models.OneToOneField('UserDetails', on_delete=models.CASCADE)

    # Survey Response Data
    SOCIAL_ISOLATION_CHOICES = [
        (1, "Very socially isolated"),
        (2, "Slightly socially isolated"),
        (3, "Neither socially isolated or connected"),
        (4, "Slightly socially connected"),
        (5, "Very socially connected"),
    ]
    social_isolation_before = models.PositiveSmallIntegerField(
        verbose_name="Before Participation",
        choices=SOCIAL_ISOLATION_CHOICES,
        blank=False, default=None,
    )
    social_isolation_during = models.PositiveSmallIntegerField(
        verbose_name="During Participation",
        choices=SOCIAL_ISOLATION_CHOICES,
        blank=False, default=None,
    )

    # Group-related Data
    group_contact = models.CharField(
        verbose_name="Do you plan to keep in contact with anyone you met whilst participating?",
        max_length=1,
        choices=[("Y", "Yes"), ("N", "No"), ("M", "Maybe")],
        null=True, blank=True, default=None,
    )

    GROUP_RELATION_CHOICES = [
        (1, "None of them"),
        (2, "A few of them"),
        (3, "About half"),
        (4, "Most of them"),
        (5, "All of them"),
    ]
    group_relation_overall = models.PositiveSmallIntegerField(
        verbose_name="You all got on well with each other.",
        choices=GROUP_RELATION_CHOICES,
        null=True, blank=True, default=None,
    )
    group_relation_agreeable = models.PositiveSmallIntegerField(
        verbose_name="They were agreeable.",
        choices=GROUP_RELATION_CHOICES,
        null=True, blank=True, default=None,
    )
    group_relation_neuroticism = models.PositiveSmallIntegerField(
        verbose_name="They were emotionally stable.",
        choices=GROUP_RELATION_CHOICES,
        null=True, blank=True, default=None,
    )
    group_relation_extroversion = models.PositiveSmallIntegerField(
        verbose_name="They were extroverted.",
        choices=GROUP_RELATION_CHOICES,
        null=True, blank=True, default=None,
    )
    group_relation_introversion = models.PositiveSmallIntegerField(
        verbose_name="They were introverted.",
        choices=GROUP_RELATION_CHOICES,
        null=True, blank=True, default=None,
    )

    group_additional = models.TextField(
        verbose_name="Do you have any other thoughts or opinions regarding the group(s) you were matched with?",
        null=True, blank=True, default=None,
    )

    # Game Related Data
    game_gamer = models.PositiveSmallIntegerField(
        verbose_name="To what extent would you consider yourself a gamer?",
        choices=[
            (1, "Not a gamer"),
            (2, "Has played games"),
            (3, "Casual gamer"),
            (4, "Regular gamer"),
            (5, "Hardcore gamer")
        ],
        null=True, blank=True, default=None,
    )

    GAME_AFFECTIVENESS_CHOICES = [
        (1, "Strongly Disagree"),
        (2, "Disagree"),
        (3, "Neither agree nor disagree"),
        (4, "Agree"),
        (5, "Strongly Agree"),
    ]
    game_affectiveness_interaction = models.PositiveSmallIntegerField(
        verbose_name="The game encouraged social interaction within your group.",
        choices=GAME_AFFECTIVENESS_CHOICES,
        null=True, blank=True, default=None,
    )
    game_affectiveness_approachable = models.PositiveSmallIntegerField(
        verbose_name="The game is approachable <em>(1)</em>.",
        choices=GAME_AFFECTIVENESS_CHOICES,
        null=True, blank=True, default=None,
    )
    game_affectiveness_accessible = models.PositiveSmallIntegerField(
        verbose_name="The game is easily available / accessible <em>(2)</em>.",
        choices=GAME_AFFECTIVENESS_CHOICES,
        null=True, blank=True, default=None,
    )

    game_additional = models.TextField(
        verbose_name="Do you have any other thoughts or opinions about the game?",
        null=True, blank=True, default=None,
    )

    # Concluding Data
    WEBSITE_AFFECTIVENESS_CHOICES = [
        (1, "1"),
        (2, "2"),
        (3, "3"),
        (4, "4"),
        (5, "5"),
    ]
    website_affectiveness_user_friendly = models.PositiveSmallIntegerField(
        verbose_name="To what extent does the website feel <em>user-friendly</em>?",
        choices=WEBSITE_AFFECTIVENESS_CHOICES,
        null=True, blank=True, default=None,
    )
    website_affectiveness_accessible = models.PositiveSmallIntegerField(
        verbose_name="To what extent does the website feel <em>accessible</em>?",
        choices=WEBSITE_AFFECTIVENESS_CHOICES,
        null=True, blank=True, default=None,
    )

    concluding_additional = models.TextField(
        verbose_name="Do you have any final thoughts or comments?",
        null=True, blank=True, default=None,
    )


# Match class.
# Groups together details of users matched, as well as data relating to the match.
# All users are non-identifiable.
class Match(models.Model):
    details_list = models.ManyToManyField('UserDetails')

    # Metadata regarding the matches
    origin_date = models.DateField(auto_now=True)

    mean_agreeableness = models.DecimalField(max_digits=3, decimal_places=3, default=0.5)
    mean_neuroticism = models.DecimalField(max_digits=3, decimal_places=3, default=0.5)
    mean_extroversion = models.DecimalField(max_digits=3, decimal_places=3, default=0.5)
    mean_heuristic = models.DecimalField(max_digits=3, decimal_places=3, default=0.5)

    variance_agreeableness = models.DecimalField(max_digits=3, decimal_places=3, default=0.5)
    variance_neuroticism = models.DecimalField(max_digits=3, decimal_places=3, default=0.5)
    variance_extroversion = models.DecimalField(max_digits=3, decimal_places=3, default=0.5)
    variance_heuristic = models.DecimalField(max_digits=3, decimal_places=3, default=0.5)
