from http.client import HTTPResponse
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
import requests
import os
from dotenv import load_dotenv, find_dotenv
from lolpros.models import Account, Team, Player

load_dotenv(find_dotenv())


def index(request):
    return HttpResponse("YES")


def addAccount(request, account):
    api_key = os.getenv('RIOT_API_KEY')
    urlAccount = f"https://euw1.api.riotgames.com/lol/summoner/v4/summoners/by-name/{account}?api_key={api_key}"

    res = requests.get(urlAccount)
    res = res.json()
    urlLp = f"https://euw1.api.riotgames.com/lol/league/v4/entries/by-summoner/{res['id']}?api_key={api_key}"

    res2 = requests.get(urlLp)
    res2 = res2.json()

    if res2 != []:
        for league in res2:
            if league['queueType'] == "RANKED_SOLO_5x5":
                res2 = league
    else:
        res2 = {
            'tier': '',
            'rank': '',
            'leaguePoints': 0,
            'wins': 0,
            'losses': 0,
        }

    res = res | res2

    try:
        if Account.objects.get(id=res['id']):
            print(f"Le compte {res['name']} existe déja, mise à jour...")
            a = Account.objects.filter(id=res['id'])
            a.update(
                name=res['name'], 
                summonerLvl=res['summonerLevel'], 
                profileIcon=f"http://ddragon.leagueoflegends.com/cdn/12.17.1/img/profileicon/{res['profileIconId']}.png",
                tier=res['tier'],
                rank=res['rank'],
                leaguePoints=res['leaguePoints'],
                wins=res['wins'],
                losses=res['losses']
            )
            a = Account.objects.get(id=res['id'])
            a.getLpc()
            a.save()
            a.refresh_from_db()
            
    except Account.DoesNotExist:
        a = Account(
            id=res['id'],
            name=res['name'], 
            summonerLvl=res['summonerLevel'], 
            profileIcon=f"http://ddragon.leagueoflegends.com/cdn/12.17.1/img/profileicon/{res['profileIconId']}.png",
            tier=res['tier'],
            rank=res['rank'],
            leaguePoints=res['leaguePoints'],
            wins=res['wins'],
            losses=res['losses']
        )
        a.getLpc()
        a.save()

    return JsonResponse(res)


def getPlayerDb(player):
    player = player.lower()

    try:
        playerInfos = Player.objects.get(name=player)

    except Player.DoesNotExist:
        response = {
            "response": "Le joueur n'existe pas"
        }
        return response

    accountsInfos = Account.objects.filter(player__name=player)

    response = {
        "playerId" : playerInfos.id,
        "playerName" : playerInfos.name.capitalize(),
        "playerTeam" : playerInfos.team.name.capitalize() if playerInfos.team else None,
        "teamId" : playerInfos.team.id if playerInfos.team else None,
        "accounts" : [],
    }

    for account in accountsInfos:
        response['accounts'].append({
            "playerId": playerInfos.id,
            'name': account.name,
            'summonerLvl': account.summonerLvl,
            'profileIcon': account.profileIcon,
            'tier': account.tier,
            'rank': account.rank,
            'leaguePoints': account.leaguePoints,
            'wins': account.wins,
            'losses': account.losses,
            'LPC': account.LPC,
        })
    return response


def playerDb(request, player):
    return JsonResponse(getPlayerDb(player))


def getTeamDb(team):
    team = team.lower()

    try:
        teamInfos = Team.objects.get(name=team)

    except Team.DoesNotExist:
        response = {
            "response": "La Team n'existe pas"
        }
        return JsonResponse(response)

    playersInfos = Player.objects.filter(team__name=team)

    response = {
        "teamId" : teamInfos.id,
        "teamName" : teamInfos.name.capitalize(),
        "teamLogo" : teamInfos.logo,
        "players" : [],
    }

    for player in playersInfos:
        response['players'].append(getPlayerDb(player.name))

    return response


def teamDb(request, team):
    return JsonResponse(getTeamDb(team))


def players(request):
    players = Player.objects.all()

    response = {}

    for player in players:
        return