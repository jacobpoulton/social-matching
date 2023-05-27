from django.contrib import admin
from . import models


@admin.register(models.User)
class UserAdmin(admin.ModelAdmin):
    pass


@admin.register(models.UserDetails)
class MatchAdmin(admin.ModelAdmin):
    pass


@admin.register(models.UserPreferences)
class MatchAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Match)
class MatchAdmin(admin.ModelAdmin):
    pass


@admin.register(models.SurveyData)
class MatchAdmin(admin.ModelAdmin):
    pass
