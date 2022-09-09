from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('addacount/<str:account>', views.addAccount, name='addAccount'),
    path('player/<str:player>', views.playerDb, name='playerDb'),
    path('team/<str:team>', views.teamDb, name='teamDb'),
]