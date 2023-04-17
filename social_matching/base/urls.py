from django.urls import path
from django.views.generic import RedirectView
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('home/', RedirectView.as_view(url='', permanent=True)),
    path('welcome/', RedirectView.as_view(url='', permanent=True)),
    path('accounts/new/', views.CreateUserView.as_view(), name='create-user'),
    path('accounts/details/', views.GiveDetailsView.as_view(), name='details'),
    path('accounts/remove/', views.delete_user, name='delete-user'),
    path('preferences/matching/', views.toggle_matching, name='toggle-matching'),
]
