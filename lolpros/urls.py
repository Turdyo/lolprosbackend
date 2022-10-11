from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('addaccount/<str:account>', views.addAccount, name='addAccount'),
    path('player/<str:player>', views.playerDb, name='playerDb'),
    path('team/<str:team>', views.teamDb, name='teamDb'),
    path('leaderboard', views.leaderboard, name='leaderboard'),
    path('updateall', views.updateAll, name='updateAll'),
    path('register/<int:discordId>/<str:userName>/<str:accounts>/<str:role>/<str:token>', views.registerPlayer, name="registerPlayer"),
    path('discordplayer/<int:discordID>', views.getPlayerDiscord, name='getPlayerDiscord'),
]