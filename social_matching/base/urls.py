from django.urls import path
from django.views.generic import RedirectView
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('home/', RedirectView.as_view(url='', permanent=True)),
    path('welcome/', RedirectView.as_view(url='', permanent=True)),
    path('accounts/new/', views.CreateUserView.as_view(), name='create-user'),
]
